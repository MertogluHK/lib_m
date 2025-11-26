from rest_framework import serializers
from .models import Reservation

class ReservationSerializer(serializers.ModelSerializer):
	user_username = serializers.CharField(source='user.username', read_only=True)
	book_title = serializers.CharField(source='book.title', read_only=True)

	class Meta:
		model = Reservation
		fields = [
			'id', 'user', 'user_username', 'book', 'book_title',
			'pickup_deadline_days', 'deposit_amount', 'status',
			'reserved_at', 'picked_up_at', 'cancelled_at', 'returned_at', 'refund_issued'
		]
		read_only_fields = ['id', 'user_username', 'book_title', 'reserved_at', 'picked_up_at', 'cancelled_at', 'returned_at', 'refund_issued', 'status']

	def validate_pickup_deadline_days(self, value):
		if not (1 <= value <= 3):
			raise serializers.ValidationError('Pickup deadline must be between 1 and 3 days')
		return value

	def validate(self, attrs):
		# Force fixed deposit amount to 50 if provided otherwise set in view
		attrs['deposit_amount'] = attrs.get('deposit_amount', 50) or 50
		return attrs