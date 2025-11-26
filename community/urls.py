from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CommunityPostViewSet

router = DefaultRouter()
router.register(r'posts', CommunityPostViewSet, basename='communitypost')

urlpatterns = [
	path('', include(router.urls)),
]

