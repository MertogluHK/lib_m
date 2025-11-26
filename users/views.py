from django.shortcuts import render
from rest_framework import views, status, viewsets, permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth.models import User
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import (
	RegisterSerializer,
	UserAdminSerializer,
	UserTokenObtainPairSerializer,
	AdminTokenObtainPairSerializer,
	MeSerializer,
)

# Create your views here.

class RegisterView(views.APIView):
	permission_classes = []
	def post(self, request):
		serializer = RegisterSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		user = serializer.save()
		return Response({'id': user.id, 'username': user.username}, status=201)


class MeView(views.APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request):
		return Response(
			{
				'id': request.user.id,
				'username': request.user.username,
				'email': request.user.email,
				'first_name': request.user.first_name,
				'last_name': request.user.last_name,
				'is_staff': request.user.is_staff,
			}
		)

	def patch(self, request):
		serializer = MeSerializer(request.user, data=request.data, partial=True)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(serializer.data)


class UserTokenObtainPairView(TokenObtainPairView):
	serializer_class = UserTokenObtainPairSerializer


class AdminTokenObtainPairView(TokenObtainPairView):
	serializer_class = AdminTokenObtainPairSerializer


class UserAdminViewSet(viewsets.ModelViewSet):
	queryset = User.objects.all().order_by('username')
	serializer_class = UserAdminSerializer
	permission_classes = [IsAdminUser]
	http_method_names = ['get', 'patch']
