from rest_framework import serializers
from .models import Book, Review
from .utils import get_book_cover_image_url

class ReviewSerializer(serializers.ModelSerializer):
	user_username = serializers.CharField(source='user.username', read_only=True)

	class Meta:
		model = Review
		fields = ['id', 'user', 'user_username', 'rating', 'comment', 'created_at']
		read_only_fields = ['id', 'user_username', 'created_at']

class BookSerializer(serializers.ModelSerializer):
	average_rating = serializers.SerializerMethodField()
	cover_image = serializers.SerializerMethodField()

	class Meta:
		model = Book
		fields = [
			'id',
			'isbn',
			'title',
			'author',
			'publisher',
			'page_count',
			'published_year',
			'description',
			'category',
			'cover_url',
			'external_rating',
			'stock',
			'reserved_count',
			'average_rating',
			'cover_image',
		]
		read_only_fields = ['id', 'average_rating']

	def get_average_rating(self, obj: Book) -> float:
		# Use annotated effective_rating if available (from queryset annotation)
		try:
			effective_rating = getattr(obj, 'effective_rating', None)
			if effective_rating is not None:
				return float(effective_rating)
		except (AttributeError, TypeError, ValueError):
			pass
		# Try avg_rating_db annotation if available
		try:
			avg_rating_db = getattr(obj, 'avg_rating_db', None)
			if avg_rating_db is not None:
				return float(avg_rating_db)
		except (AttributeError, TypeError, ValueError):
			pass
		# Otherwise fall back to external_rating or 0.0
		try:
			external_rating = getattr(obj, 'external_rating', None)
			if external_rating is not None:
				return float(external_rating)
		except (AttributeError, TypeError, ValueError):
			pass
		# Last resort: return 0.0
		return 0.0

	def get_cover_image(self, obj: Book) -> str:
		try:
			return get_book_cover_image_url(obj.id)
		except Exception:
			# Return fallback image if there's any error
			from django.templatetags.static import static
			return static('images/library-hero.webp')
