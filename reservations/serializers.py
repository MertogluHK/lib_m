from rest_framework import serializers
from .models import Reservation
from datetime import timedelta

class ReservationSerializer(serializers.ModelSerializer):
	user_username = serializers.CharField(source='user.username', read_only=True)
	book_title = serializers.CharField(source='book.title', read_only=True)
	return_date = serializers.SerializerMethodField(read_only=True)

	class Meta:
		model = Reservation
		fields = [
			'id', 'user', 'user_username', 'book', 'book_title',
			'pickup_date', 'pickup_deadline_days', 'return_date', 'deposit_amount', 'status',
			'reserved_at', 'picked_up_at', 'cancelled_at', 'returned_at', 'refund_issued'
		]
		read_only_fields = ['id', 'user', 'user_username', 'book_title', 'return_date', 'reserved_at', 'picked_up_at', 'cancelled_at', 'returned_at', 'refund_issued', 'status']

	def get_return_date(self, obj):
		"""İade tarihi hesapla"""
		if obj.pickup_date:
			return (obj.pickup_date + timedelta(days=obj.pickup_deadline_days)).isoformat()
		elif obj.picked_up_at:
			return (obj.picked_up_at.date() + timedelta(days=obj.pickup_deadline_days)).isoformat()
		return None

	def validate_pickup_date(self, value):
		"""pickup_date is required"""
		if not value:
			raise serializers.ValidationError('Alınacağı tarih zorunludur.')
		return value

	def validate_pickup_deadline_days(self, value):
		if not (1 <= value <= 30):
			raise serializers.ValidationError('Gün sayısı 1-30 arasında olmalıdır')
		return value

	def validate(self, attrs):
		# Force fixed deposit amount to 50 if provided otherwise set in view
		attrs['deposit_amount'] = attrs.get('deposit_amount', 50) or 50
		return attrs