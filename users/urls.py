from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, MeView, UserAdminViewSet

router = DefaultRouter()
router.register(r'manage', UserAdminViewSet, basename='user-manage')

urlpatterns = [
	path('register/', RegisterView.as_view(), name='register'),
	path('me/', MeView.as_view(), name='me'),
	path('', include(router.urls)),
]
