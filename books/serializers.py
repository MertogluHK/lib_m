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
	average_rating = serializers.FloatField(read_only=True)
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

	def get_cover_image(self, obj: Book) -> str:
		return get_book_cover_image_url(obj.id)
