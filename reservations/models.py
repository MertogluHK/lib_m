from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
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
	pickup_date = models.DateField()  # Kullanıcının seçtiği alış tarihi - REQUIRED
	pickup_deadline_days = models.PositiveSmallIntegerField()  # max 3
	deposit_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
	status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
	picked_up_at = models.DateTimeField(null=True, blank=True)
	cancelled_at = models.DateTimeField(null=True, blank=True)
	returned_at = models.DateTimeField(null=True, blank=True)
	refund_issued = models.BooleanField(default=False)

	class Meta:
		pass

	@property
	def return_date(self):
		"""İade tarihi = pickup_date + pickup_deadline_days"""
		if self.pickup_date:
			return self.pickup_date + timedelta(days=self.pickup_deadline_days)
		elif self.picked_up_at:
			return self.picked_up_at.date() + timedelta(days=self.pickup_deadline_days)
		return None

	def clean(self):
		if not (1 <= self.pickup_deadline_days <= 30):
			raise ValidationError('Gün sayısı 1-30 arasında olmalıdır')

	def __str__(self) -> str:
		return f"{self.user.username} reserves {self.book.title} ({self.status})"
