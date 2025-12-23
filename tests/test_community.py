"""
Tests for the community app.
Covers CommunityPost, CommunityComment models and moderation features.
"""
from django.test import TestCase
from community.models import CommunityPost, CommunityComment
from django.contrib.auth.models import User


class CommunityPostTests(TestCase):
    """Tests for CommunityPost model and API"""
    pass


class CommunityPostPermissionTests(TestCase):
    """Tests for CommunityPost permissions (create, edit, delete)"""
    pass


class CommunityCommentTests(TestCase):
    """Tests for CommunityComment model and API"""
    pass


class CommunityModerationTests(TestCase):
    """Tests for admin moderation features (post/comment deletion by staff)"""
    pass
