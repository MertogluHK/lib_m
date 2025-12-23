from rest_framework import serializers
from .models import CommunityPost, CommunityComment
from books.models import Book

class CommunityCommentSerializer(serializers.ModelSerializer):
	user_username = serializers.CharField(source='user.username', read_only=True)
	post_id = serializers.IntegerField(source='post.id', read_only=True)
	post_book_title = serializers.CharField(source='post.book_title', read_only=True)

	class Meta:
		model = CommunityComment
		fields = ['id', 'user_username', 'content', 'created_at', 'post_id', 'post_book_title']
		read_only_fields = ['id', 'user_username', 'created_at', 'post_id', 'post_book_title']

class CommunityPostSerializer(serializers.ModelSerializer):
	user_username = serializers.CharField(source='user.username', read_only=True)
	comment_count = serializers.IntegerField(read_only=True)
	comments = CommunityCommentSerializer(many=True, read_only=True)
	book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all(), write_only=True)
	book_id = serializers.IntegerField(source='book.id', read_only=True)

	class Meta:
		model = CommunityPost
		fields = ['id', 'user_username', 'book', 'book_id', 'book_title', 'content', 'rating', 'created_at', 'comment_count', 'comments']
		read_only_fields = ['id', 'user_username', 'created_at', 'comment_count', 'book_title', 'book_id', 'comments']

	def validate_rating(self, value):
		if value is None:
			return value
		if not (1 <= value <= 5):
			raise serializers.ValidationError('Yıldız 1 ile 5 arasında olmalı.')
		return value

	def validate(self, attrs):
		book = attrs.get('book')
		if not book:
			raise serializers.ValidationError({'book': 'Bir kitap seçmelisiniz.'})
		attrs['book_title'] = book.title
		return attrs

