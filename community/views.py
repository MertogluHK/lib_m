from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import CommunityPost, CommunityComment
from .serializers import CommunityPostSerializer, CommunityCommentSerializer
from books.utils import recalc_book_rating_from_posts

class IsAuthenticatedOrReadOnly(permissions.BasePermission):
	def has_permission(self, request, view):
		if request.method in permissions.SAFE_METHODS:
			return True
		return request.user and request.user.is_authenticated

class IsOwnerOrReadOnly(permissions.BasePermission):
	def has_object_permission(self, request, view, obj):
		if request.method in permissions.SAFE_METHODS:
			return True
		# Sahibi veya admin/staff kullanıcılar düzenleyebilir/silebilir
		return obj.user == request.user or request.user.is_staff

class CommunityPostViewSet(viewsets.ModelViewSet):
	queryset = CommunityPost.objects.select_related('user', 'book').prefetch_related('comments').all()
	serializer_class = CommunityPostSerializer
	permission_classes = [IsAuthenticatedOrReadOnly]

	def get_permissions(self):
		if self.action in ['destroy', 'update', 'partial_update']:
			return [IsOwnerOrReadOnly()]
		return [IsAuthenticatedOrReadOnly()]

	def perform_create(self, serializer):
		post = serializer.save(user=self.request.user)
		recalc_book_rating_from_posts(post.book)

	def perform_update(self, serializer):
		post = serializer.save()
		recalc_book_rating_from_posts(post.book)

	def perform_destroy(self, instance):
		book = instance.book
		super().perform_destroy(instance)
		if book:
			recalc_book_rating_from_posts(book)

	@action(detail=False, methods=['get'])
	def my_posts(self, request):
		if not request.user.is_authenticated:
			return Response({'detail': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
		posts = CommunityPost.objects.filter(user=request.user).select_related('user').prefetch_related('comments').all()
		serializer = self.get_serializer(posts, many=True)
		return Response(serializer.data)

	@action(detail=True, methods=['get', 'post'], permission_classes=[IsAuthenticatedOrReadOnly])
	def comments(self, request, pk=None):
		post = self.get_object()
		if request.method == 'GET':
			comments = post.comments.select_related('user').all()
			return Response(CommunityCommentSerializer(comments, many=True).data)
		else:
			serializer = CommunityCommentSerializer(data=request.data)
			serializer.is_valid(raise_exception=True)
			serializer.save(post=post, user=request.user)
			return Response(serializer.data, status=status.HTTP_201_CREATED)

	@action(detail=False, methods=['get'])
	def my_comments(self, request):
		if not request.user.is_authenticated:
			return Response({'detail': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
		comments = CommunityComment.objects.filter(user=request.user).select_related('user', 'post').all()
		serializer = CommunityCommentSerializer(comments, many=True)
		return Response(serializer.data)

	@action(detail=True, methods=['put', 'patch', 'delete'], url_path='comments/(?P<comment_id>[^/.]+)')
	def comment_detail(self, request, pk=None, comment_id=None):
		post = self.get_object()
		try:
			comment = post.comments.get(id=comment_id)
		except CommunityComment.DoesNotExist:
			return Response({'detail': 'Yorum bulunamadı'}, status=status.HTTP_404_NOT_FOUND)
		
		# Sahibi veya admin/staff kullanıcılar düzenleyebilir/silebilir
		if comment.user != request.user and not request.user.is_staff:
			return Response({'detail': 'Bu yorumu düzenleme yetkiniz yok'}, status=status.HTTP_403_FORBIDDEN)
		
		if request.method == 'DELETE':
			comment.delete()
			return Response(status=status.HTTP_204_NO_CONTENT)
		
		# Update comment
		serializer = CommunityCommentSerializer(comment, data=request.data, partial=request.method == 'PATCH')
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(serializer.data)
