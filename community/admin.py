from django.contrib import admin
from .models import CommunityPost, CommunityComment

@admin.register(CommunityPost)
class CommunityPostAdmin(admin.ModelAdmin):
	list_display = ['id', 'user', 'book_title', 'created_at', 'comment_count']
	list_filter = ['created_at']
	search_fields = ['book_title', 'content', 'user__username']

@admin.register(CommunityComment)
class CommunityCommentAdmin(admin.ModelAdmin):
	list_display = ['id', 'post', 'user', 'created_at']
	list_filter = ['created_at']
	search_fields = ['content', 'user__username']
