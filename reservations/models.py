from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from books.models import Book

class Reservation(models.Model):
	class Status(models.TextChoices):
		PENDING = 'PENDING', 'Pending'
		PICKED_UP = 'PICKED_UP', 'Picked Up'
		CANCELLED = 'CANCELLED', 'Cancelled'
		EXPIRED = 'EXPIRED', 'Expired'
		RETURNED = 'RETURNED', 'Returned'

	user = models.ForeignKey(User, related_name='reservations', on_delete=models.CASCADE)
	book = models.ForeignKey(Book, related_name='reservations', on_delete=models.CASCADE)
	reserved_at = models.DateTimeField(auto_now_add=True)
	pickup_deadline_days = models.PositiveSmallIntegerField()  # max 3
	deposit_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
	status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
	picked_up_at = models.DateTimeField(null=True, blank=True)
	cancelled_at = models.DateTimeField(null=True, blank=True)
	returned_at = models.DateTimeField(null=True, blank=True)
	refund_issued = models.BooleanField(default=False)

	class Meta:
		unique_together = ('user', 'book', 'status')

	def clean(self):
		if not (1 <= self.pickup_deadline_days <= 3):
			raise ValidationError('Pickup deadline must be between 1 and 3 days')

	def __str__(self) -> str:
		return f"{self.user.username} reserves {self.book.title} ({self.status})"
