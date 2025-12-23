"""
Centralized test directory for all LIB-M apps.

This directory contains pytest/Django test files organized by app:
- test_books.py
- test_users.py
- test_reservations.py
- test_community.py
- test_frontend.py

Usage:
    pytest                    # Run all tests
    pytest tests/test_books.py  # Run specific test file
    pytest tests/test_books.py::BookModelTests  # Run specific test class
"""
