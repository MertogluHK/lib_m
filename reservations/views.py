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
		with transaction.atomic():
			book_locked = Book.objects.select_for_update().get(pk=book.pk)
			if book_locked.stock <= 0:
				raise serializers.ValidationError({'book': 'Bu kitap şu anda stokta bulunmuyor.'})
			book_locked.stock -= 1
			book_locked.reserved_count += 1
			book_locked.save(update_fields=['stock', 'reserved_count'])
			serializer.save(user=self.request.user, status=Reservation.Status.PENDING, deposit_amount=50)

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
