"""
Pytest configuration and shared test fixtures.

This file contains:
- Pytest configuration
- Shared fixtures for all test files
- Database setup/teardown
- Mock data factories
"""

import pytest
from django.contrib.auth.models import User
from books.models import Book


@pytest.fixture
def test_user(db):
    """Create a test user"""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def test_admin_user(db):
    """Create a test admin user"""
    return User.objects.create_user(
        username='testadmin',
        email='admin@example.com',
        password='adminpass123',
        is_staff=True,
        is_superuser=True
    )


@pytest.fixture
def test_book(db):
    """Create a test book"""
    return Book.objects.create(
        title='Test Book',
        author='Test Author',
        isbn='978-3-16-148410-0',
        category='Test Category',
        stock=5
    )
