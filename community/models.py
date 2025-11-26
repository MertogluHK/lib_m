from django.db import models
from django.contrib.auth.models import User
from books.models import Book

class CommunityPost(models.Model):
	user = models.ForeignKey(User, related_name='community_posts', on_delete=models.CASCADE)
	book_title = models.CharField(max_length=255)
	book = models.ForeignKey(Book, related_name='community_posts', on_delete=models.SET_NULL, null=True, blank=True)
	content = models.TextField()
	rating = models.PositiveSmallIntegerField(null=True, blank=True, default=None)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return f"{self.user.username} - {self.book_title}"

	@property
	def comment_count(self):
		return self.comments.count()

class CommunityComment(models.Model):
	post = models.ForeignKey(CommunityPost, related_name='comments', on_delete=models.CASCADE)
	user = models.ForeignKey(User, related_name='community_comments', on_delete=models.CASCADE)
	content = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['created_at']

	def __str__(self):
		return f"{self.user.username} - {self.post.book_title}"
