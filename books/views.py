import math
from django.db.models import Q, Avg, FloatField, Value, Case, When
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Book, Review
from .serializers import BookSerializer, ReviewSerializer
from .utils import sync_legacy_book_row

class IsAuthenticatedOrReadOnly(permissions.BasePermission):
	def has_permission(self, request, view):
		if request.method in ('GET', 'HEAD', 'OPTIONS'):
			return True
		return request.user and request.user.is_authenticated

class IsStaffOrReadOnly(permissions.BasePermission):
	def has_permission(self, request, view):
		if request.method in permissions.SAFE_METHODS:
			return True
		return request.user.is_authenticated and request.user.is_staff

class BookViewSet(viewsets.ModelViewSet):
	queryset = Book.objects.all()
	serializer_class = BookSerializer
	permission_classes = [IsStaffOrReadOnly]
	page_size = 15
	SORT_MAPPING = {
		'title_asc': ('title',),
		'title_desc': ('-title',),
		'created_desc': ('-created_at',),
		'created_asc': ('created_at',),
		'stock_desc': ('-stock', 'title'),
		'stock_asc': ('stock', 'title'),
		'rating_desc': ('-effective_rating', '-created_at'),
		'rating_asc': ('effective_rating', 'title'),
	}

	def get_queryset(self):
		qs = super().get_queryset()
		qs = qs.annotate(
			avg_rating_db=Avg('reviews__rating'),
		).annotate(
			effective_rating=Case(
				When(avg_rating_db__isnull=False, then='avg_rating_db'),
				When(external_rating__isnull=False, then='external_rating'),
				default=Value(0.0),
				output_field=FloatField()
			)
		)

		query = self.request.query_params.get('q')
		if query:
			query = query.strip()
			if query:
				qs = qs.filter(title__icontains=query)

		author = self.request.query_params.get('author')
		if author:
			author = author.strip()
			if author:
				qs = qs.filter(author__iexact=author)

		categories_param = self.request.query_params.get('categories')
		if categories_param:
			cat_parts = [part.strip() for part in categories_param.split(',') if part.strip()]
			if cat_parts:
				for part in cat_parts:
					qs = qs.filter(category__icontains=part)

		min_rating = self.request.query_params.get('min_rating')
		if min_rating:
			try:
				min_rating_value = float(min_rating)
				qs = qs.filter(effective_rating__gte=min_rating_value)
			except ValueError:
				pass

		in_stock = self.request.query_params.get('in_stock')
		if in_stock and in_stock.lower() in ('1', 'true', 'yes', 'on'):
			qs = qs.filter(stock__gt=0)

		return qs

	def apply_sorting(self, queryset):
		sort_param = self.request.query_params.get('sort') or 'title_asc'
		ordering = self.SORT_MAPPING.get(sort_param, ('title',))
		return queryset.order_by(*ordering)

	def list(self, request, *args, **kwargs):
		try:
			page_size = int(request.query_params.get('page_size', self.page_size))
		except (TypeError, ValueError):
			page_size = self.page_size
		page_size = max(1, min(100, page_size))
		queryset = self.apply_sorting(self.filter_queryset(self.get_queryset()))
		total = queryset.count()
		page = request.query_params.get('page')
		try:
			page = int(page)
			if page < 1:
				page = 1
		except (TypeError, ValueError):
			page = 1
		total_pages = max(1, math.ceil(total / page_size)) if total else 1
		if total and page > total_pages:
			page = total_pages
		start = (page - 1) * page_size
		end = start + page_size
		serializer = self.get_serializer(queryset[start:end], many=True)
		return Response({
			'results': serializer.data,
			'page': page,
			'total_pages': total_pages,
			'total': total,
		})

	def perform_create(self, serializer):
		"""
		Create book and sync to legacy table.
		If legacy sync fails, book is still created in Django model.
		"""
		try:
			book = serializer.save()
		except Exception as e:
			# Re-raise serializer/model validation errors
			raise
		
		# Try to sync to legacy table, but don't fail if it doesn't work
		try:
			sync_legacy_book_row(book)
		except Exception as e:
			# Log but don't raise - book is already created
			import logging
			logger = logging.getLogger(__name__)
			logger.warning(f"Book {book.id} created but legacy sync failed: {str(e)}")

	def perform_update(self, serializer):
		book = serializer.save()
		sync_legacy_book_row(book)

	def perform_destroy(self, instance):
		"""Delete book and also remove from legacy books table"""
		from django.db import connection
		book_id = instance.id
		# Delete from legacy table first
		with connection.cursor() as cursor:
			cursor.execute("DELETE FROM books WHERE id = %s", [book_id])
		# Then delete from Django model (this will cascade delete related objects)
		super().perform_destroy(instance)

	@action(detail=True, methods=['get', 'post'], permission_classes=[IsAuthenticatedOrReadOnly])
	def reviews(self, request, pk=None):
		book = self.get_object()
		if request.method == 'GET':
			qs = book.reviews.select_related('user').all().order_by('-created_at')
			return Response(ReviewSerializer(qs, many=True).data)
		else:
			serializer = ReviewSerializer(data=request.data)
			serializer.is_valid(raise_exception=True)
			if not (0 <= serializer.validated_data['rating'] <= 5):
				return Response({'detail': 'Rating must be between 0 and 5'}, status=400)
			Review.objects.update_or_create(
				book=book,
				user=request.user,
				defaults={
					'rating': serializer.validated_data['rating'],
					'comment': serializer.validated_data.get('comment', ''),
				}
			)
			return Response({'detail': 'Review saved'})

	@action(detail=False, methods=['get'])
	def suggest(self, request):
		query = (request.query_params.get('q') or '').strip()
		if not query:
			return Response([])
		qs = Book.objects.filter(Q(title__icontains=query) | Q(author__icontains=query)).order_by('title')[:8]
		data = [{'id': b.id, 'title': b.title, 'author': b.author} for b in qs]
		return Response(data)

	@action(detail=False, methods=['get'])
	def filters(self, request):
		authors = list(Book.objects.exclude(author='').order_by('author').values_list('author', flat=True).distinct())
		raw_categories = Book.objects.exclude(category='').values_list('category', flat=True)
		category_set = set()
		for entry in raw_categories:
			for part in entry.split(','):
				clean = part.strip()
				if clean:
					category_set.add(clean)
		categories = sorted(category_set, key=lambda x: x.lower())
		return Response({
			'authors': authors,
			'categories': categories,
			'ratings': [5, 4.5, 4, 3.5, 3, 2.5, 2, 1.5, 1]
		})

	@action(detail=True, methods=['post'], permission_classes=[IsStaffOrReadOnly])
	def upload_cover(self, request, pk=None):
		"""Upload cover image for a book"""
		try:
			from PIL import Image
		except ImportError:
			return Response({'detail': 'Pillow library is required for image processing'}, status=500)
		
		from django.conf import settings
		from pathlib import Path
		import os
		
		book = self.get_object()
		if 'cover' not in request.FILES:
			return Response({'detail': 'No cover file provided'}, status=400)
		
		file = request.FILES['cover']
		# Validate file type
		if not file.content_type.startswith('image/'):
			return Response({'detail': 'File must be an image'}, status=400)
		
		# Validate file size (max 5MB)
		if file.size > 5 * 1024 * 1024:
			return Response({'detail': 'File size must be less than 5MB'}, status=400)
		
		try:
			# Get static images directory
			static_dirs = getattr(settings, 'STATICFILES_DIRS', [])
			if not static_dirs:
				return Response({'detail': 'Static files directory not configured'}, status=500)
			
			images_dir = Path(static_dirs[0]) / 'images'
			images_dir.mkdir(parents=True, exist_ok=True)
			
			# Save as {book_id}.jpg
			output_path = images_dir / f'{book.id}.jpg'
			
			# If file already exists, remove it first to ensure fresh upload
			if output_path.exists():
				output_path.unlink()
			
			# Open and process image
			# Reset file pointer to beginning in case it was read before
			file.seek(0)
			img = Image.open(file)
			# Convert to RGB if necessary (handles RGBA, P, etc.)
			if img.mode != 'RGB':
				img = img.convert('RGB')
			# Resize if too large (max 1000px on longest side)
			max_size = 1000
			if max(img.size) > max_size:
				img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
			
			# Save as JPEG
			img.save(output_path, 'JPEG', quality=85, optimize=True)
			
			# Verify file was saved
			if not output_path.exists():
				return Response({'detail': 'File was not saved successfully'}, status=500)
			
			# Log success for debugging
			import logging
			logger = logging.getLogger(__name__)
			logger.info(f'Cover image saved successfully for book {book.id} at {output_path}')
			
			return Response({
				'detail': 'Cover uploaded successfully',
				'book_id': book.id,
				'file_path': str(output_path)
			})
		except Exception as e:
			import logging
			logger = logging.getLogger(__name__)
			logger.error(f'Error uploading cover for book {book.id}: {str(e)}', exc_info=True)
			return Response({'detail': f'Error uploading cover: {str(e)}'}, status=500)

class ReviewViewSet(viewsets.ReadOnlyModelViewSet):
	queryset = Review.objects.select_related('book', 'user').all().order_by('-created_at')
	serializer_class = ReviewSerializer
	permission_classes = [permissions.AllowAny]
