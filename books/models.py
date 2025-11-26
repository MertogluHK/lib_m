from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

class Book(models.Model):
	isbn = models.CharField(max_length=20, unique=True)
	title = models.CharField(max_length=255)
	author = models.CharField(max_length=255)
	publisher = models.CharField(max_length=255, blank=True)
	page_count = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
	published_year = models.PositiveIntegerField(null=True, blank=True)
	description = models.TextField(blank=True)
	category = models.CharField(max_length=255, blank=True)
	cover_url = models.URLField(blank=True)
	external_rating = models.FloatField(null=True, blank=True)
	reserved_count = models.PositiveIntegerField(default=0)
	stock = models.PositiveSmallIntegerField(default=1, validators=[MinValueValidator(0), MaxValueValidator(4)])
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self) -> str:
		return f"{self.title} ({self.isbn})"

	@property
	def average_rating(self) -> float:
		agg = self.reviews.aggregate(models.Avg('rating'))
		avg = agg['rating__avg']
		if avg is not None:
			return float(avg)
		return float(self.external_rating or 0.0)

class Review(models.Model):
	book = models.ForeignKey(Book, related_name='reviews', on_delete=models.CASCADE)
	user = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE)
	rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)])
	comment = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		unique_together = ('book', 'user')

	def clean(self):
		if not (0 <= self.rating <= 5):
			raise ValidationError('Rating must be between 0 and 5')

	def __str__(self) -> str:
		return f"{self.user.username} -> {self.book.title}: {self.rating}"
