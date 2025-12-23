from django.shortcuts import render
from django.db import transaction
from rest_framework import viewsets, permissions, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Reservation
from .serializers import ReservationSerializer
from books.models import Book

# Create your views here.

class IsOwnerOrAdmin(permissions.BasePermission):
	def has_object_permission(self, request, view, obj):
		return request.user.is_staff or obj.user == request.user

class ReservationViewSet(viewsets.ModelViewSet):
	queryset = Reservation.objects.select_related('user', 'book').all().order_by('-reserved_at')
	serializer_class = ReservationSerializer
	permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

	def perform_create(self, serializer):
		book = serializer.validated_data['book']
		pickup_date = serializer.validated_data.get('pickup_date')
		with transaction.atomic():
			book_locked = Book.objects.select_for_update().get(pk=book.pk)
			if book_locked.stock <= 0:
				raise serializers.ValidationError({'book': 'Bu kitap şu anda stokta bulunmuyor.'})
			book_locked.stock -= 1
			book_locked.reserved_count += 1
			book_locked.save(update_fields=['stock', 'reserved_count'])
			serializer.save(user=self.request.user, status=Reservation.Status.PENDING, deposit_amount=50, pickup_date=pickup_date)

	def get_queryset(self):
		qs = super().get_queryset()
		if not self.request.user.is_staff:
			qs = qs.filter(user=self.request.user)
		return qs

	def get_permissions(self):
		# Ensure authenticated for main actions; owner/admin check is object-level via IsOwnerOrAdmin
		if self.action in ['list', 'retrieve', 'create', 'pickup', 'cancel', 'return_book', 'update', 'partial_update', 'destroy']:
			return [permissions.IsAuthenticated(), IsOwnerOrAdmin()]
		return super().get_permissions()

	@action(detail=True, methods=['post'])
	def pickup(self, request, pk=None):
		with transaction.atomic():
			reservation = Reservation.objects.select_for_update().get(pk=self.get_object().pk)
			if reservation.status != Reservation.Status.PENDING:
				return Response({'detail': 'Reservation not pending'}, status=400)
			reservation.status = Reservation.Status.PICKED_UP
			reservation.picked_up_at = timezone.now()
			reservation.refund_issued = True  # simulate refund on time
			reservation.save(update_fields=['status', 'picked_up_at', 'refund_issued'])
		return Response({'detail': 'Marked as picked up, deposit refunded'})

	@action(detail=True, methods=['post'])
	def cancel(self, request, pk=None):
		with transaction.atomic():
			reservation = Reservation.objects.select_for_update().get(pk=self.get_object().pk)
			if reservation.status != Reservation.Status.PENDING:
				return Response({'detail': 'Reservation not pending'}, status=400)
			book = Book.objects.select_for_update().get(pk=reservation.book_id)
			if book.reserved_count <= 0:
				return Response({'detail': 'Inventory mismatch for this reservation.'}, status=400)
			book.reserved_count -= 1
			book.stock += 1
			book.save(update_fields=['stock', 'reserved_count'])
			reservation.status = Reservation.Status.CANCELLED
			reservation.cancelled_at = timezone.now()
			reservation.refund_issued = False  # keeping deposit per spec unless picked up in time
			reservation.save(update_fields=['status', 'cancelled_at', 'refund_issued'])
		return Response({'detail': 'Reservation cancelled; deposit kept'})

	@action(detail=True, methods=['post'], url_path='return')
	def return_book(self, request, pk=None):
		with transaction.atomic():
			reservation = Reservation.objects.select_for_update().get(pk=self.get_object().pk)
			if reservation.status != Reservation.Status.PICKED_UP:
				return Response({'detail': 'Only picked up reservations can be returned'}, status=400)
			book = Book.objects.select_for_update().get(pk=reservation.book_id)
			if book.reserved_count <= 0:
				return Response({'detail': 'Inventory mismatch for this reservation.'}, status=400)
			book.reserved_count -= 1
			book.stock += 1
			book.save(update_fields=['stock', 'reserved_count'])
			reservation.status = Reservation.Status.RETURNED
			reservation.returned_at = timezone.now()
			reservation.save(update_fields=['status', 'returned_at'])
		return Response({'detail': 'Book returned to stock'})

	@action(detail=False, methods=['post'])
	def check_availability(self, request):
		"""Belirtilen tarihte kitabın uygun olup olmadığını kontrol et"""
		from datetime import datetime, timedelta
		book_id = request.data.get('book_id')
		pickup_date_str = request.data.get('pickup_date')  # YYYY-MM-DD format
		
		if not book_id or not pickup_date_str:
			return Response({'error': 'book_id ve pickup_date gerekli'}, status=400)
		
		try:
			pickup_date = datetime.strptime(pickup_date_str, '%Y-%m-%d').date()
		except ValueError:
			return Response({'error': 'Geçersiz tarih formatı (YYYY-MM-DD)'}, status=400)
		
		try:
			book = Book.objects.get(pk=book_id)
		except Book.DoesNotExist:
			return Response({'error': 'Kitap bulunamadı'}, status=404)
		
		# Stoğu kontrol et
		if book.stock > 0:
			return Response({
				'available': True,
				'message': 'Bu kitap bu tarihte stoktadır',
				'next_available_date': None
			})
		
		# Stok yoksa - iade edecekleri kontrol et
		# Pickup date'ten önce iade edecek rezervasyonları bul
		pending_reservations = Reservation.objects.filter(
			book=book,
			status=Reservation.Status.PICKED_UP
		).select_related('user')
		
		earliest_return = None
		for res in pending_reservations:
			if res.return_date and res.return_date < pickup_date:
				if not earliest_return or res.return_date < earliest_return:
					earliest_return = res.return_date
		
		if earliest_return:
			# Iade edildikten sonra gün ekle (iade edildikten sabah uygun)
			next_available = earliest_return + timedelta(days=1)
			return_str = earliest_return.strftime("%d.%m.%Y")
			next_str = next_available.strftime("%d.%m.%Y")
			return Response({
				'available': True,
				'message': f'Bu kitap o tarihte stoktada yok ancak {return_str}\'de iade edilecek, {next_str}\'den itibaren uygun',
				'next_available_date': next_available.isoformat(),
				'return_before_date': earliest_return.isoformat()
			})
		
		# Hiç iade yok veya tamamı seçilmiş tarihten sonra - en yakın iade bulunması gerekiyor
		all_future_returns = Reservation.objects.filter(
			book=book,
			status=Reservation.Status.PICKED_UP
		).exclude(return_date__isnull=True).order_by('return_date')
		
		if all_future_returns.exists():
			earliest = all_future_returns.first().return_date
			next_available = earliest + timedelta(days=1)
			earliest_str = earliest.strftime("%d.%m.%Y")
			next_str = next_available.strftime("%d.%m.%Y")
			return Response({
				'available': False,
				'message': f'Bu kitap o tarihte stoktada yok. En yakın iade tarihi: {earliest_str}, {next_str}\'den itibaren uygun',
				'next_available_date': next_available.isoformat(),
				'return_before_date': earliest.isoformat()
			})
		
		return Response({
			'available': False,
			'message': 'Bu kitap şu anda stoktada bulunmamaktadır ve hiç iade planı yoktur',
			'next_available_date': None
		})
