from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class RegisterSerializer(serializers.ModelSerializer):
	password = serializers.CharField(write_only=True, min_length=8)

	class Meta:
		model = User
		fields = ['id', 'username', 'email', 'password']
		read_only_fields = ['id']

	def validate_username(self, value):
		if User.objects.filter(username=value).exists():
			raise serializers.ValidationError('username already exists')
		return value

	def create(self, validated_data):
		password = validated_data.pop('password')
		user = User(**validated_data)
		user.set_password(password)
		user.save()
		return user


class RoleAwareTokenObtainPairSerializer(TokenObtainPairSerializer):
	require_staff = False
	allow_staff = True

	@classmethod
	def get_token(cls, user):
		token = super().get_token(user)
		token['role'] = 'admin' if user.is_staff else 'user'
		return token

	def validate(self, attrs):
		username = attrs.get('username') or attrs.get('email')
		password = attrs.get('password')
		# Try to authenticate normally
		user = authenticate(username=username, password=password)
		if user is None:
			# If authentication failed, check if the user exists and password matches
			try:
				maybe_user = User.objects.get(username=username)
			except User.DoesNotExist:
				raise serializers.ValidationError('No active account found with the given credentials')
			# If password matches but user is inactive, show a clear message
			if maybe_user.check_password(password) and not maybe_user.is_active:
				raise serializers.ValidationError('Hesabınız askıya alınmıştır. Yönetici ile iletişime geçiniz.')
			# Otherwise return the generic error
			raise serializers.ValidationError('No active account found with the given credentials')
		# At this point authentication succeeded
		# Enforce staff/user restrictions for endpoint
		if self.require_staff and not user.is_staff:
			raise serializers.ValidationError('Bu giriş sadece yöneticiler içindir.')
		if not self.allow_staff and user.is_staff:
			raise serializers.ValidationError('Yöneticiler bu bölümden giriş yapamaz.')
		# If non-staff user, ensure active
		if not user.is_staff and not user.is_active:
			raise serializers.ValidationError('Hesabınız askıya alınmıştır. Yönetici ile iletişime geçiniz.')
		# Build token pair
		refresh = self.get_token(user)
		data = {
			'refresh': str(refresh),
			'access': str(refresh.access_token),
		}
		self.user = user
		data['role'] = 'admin' if user.is_staff else 'user'
		data['username'] = user.username
		return data


class UserTokenObtainPairSerializer(RoleAwareTokenObtainPairSerializer):
	require_staff = False
	allow_staff = False


class AdminTokenObtainPairSerializer(RoleAwareTokenObtainPairSerializer):
	require_staff = True
	allow_staff = True


class UserAdminSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ['id', 'username', 'email', 'is_active', 'is_staff', 'date_joined', 'last_login']
		read_only_fields = ['id', 'username', 'email', 'is_staff', 'date_joined', 'last_login']


class MeSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ['id', 'username', 'email', 'first_name', 'last_name']
		read_only_fields = ['id', 'username']
