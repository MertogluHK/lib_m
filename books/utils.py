from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional

from django.conf import settings
from django.templatetags.static import static
from django.db import connection
from django.db.models import Avg

FALLBACK_IMAGE_NAME = 'images/library-hero.webp'


def _iter_static_image_dirs() -> Iterable[Path]:
	for directory in getattr(settings, 'STATICFILES_DIRS', []):
		yield Path(directory) / 'images'


def get_book_cover_image_url(book_id: int | None) -> str:
	"""
	Return the static URL that matches <book_id>.jpg if it exists, otherwise fallback.
	"""
	if not book_id:
		return static(FALLBACK_IMAGE_NAME)

	filename = f'{book_id}.jpg'
	for image_dir in _iter_static_image_dirs():
		candidate = image_dir / filename
		if candidate.exists():
			return static(f'images/{filename}')

	return static(FALLBACK_IMAGE_NAME)


def _update_legacy_star(book_id: int, average: float) -> None:
	with connection.cursor() as cursor:
		cursor.execute("UPDATE books SET star = %s WHERE id = %s", [average, book_id])


def recalc_book_rating_from_posts(book) -> Optional[float]:
	if not book:
		return None
	from community.models import CommunityPost
	agg = CommunityPost.objects.filter(
		book=book,
		rating__isnull=False
	).aggregate(avg=Avg('rating'))
	average = float(agg['avg'] or 0.0)
	book.external_rating = average
	book.save(update_fields=['external_rating'])
	_update_legacy_star(book.id, average)
	return average


def recalc_all_book_ratings() -> None:
	from books.models import Book
	for book in Book.objects.all():
		recalc_book_rating_from_posts(book)


def sync_legacy_book_row(book) -> None:
	"""
	Sync book data to legacy books table.
	If sync fails, log the error but don't raise exception to allow book creation to succeed.
	"""
	if not book or not book.id:
		return
	rating_value = book.external_rating if book.external_rating is not None else 0.0
	try:
		with connection.cursor() as cursor:
			cursor.execute("SELECT 1 FROM books WHERE id = %s", [book.id])
			exists = cursor.fetchone()
			if exists:
				cursor.execute(
					"""
					UPDATE books
					SET book_name = %s,
					    page_count = %s,
					    author = %s,
					    book_exp = %s,
					    category = %s,
					    star = %s,
					    stok = %s,
					    reserve = %s
					WHERE id = %s
					""",
					[
						book.title,
						book.page_count,
						book.author,
						book.description or '',
						book.category or '',
						rating_value,
						book.stock,
						book.reserved_count,
						book.id,
					]
				)
			else:
				cursor.execute(
					"""
					INSERT INTO books (id, book_name, page_count, author, book_exp, star, category, stok, reserve)
					VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
					""",
					[
						book.id,
						book.title,
						book.page_count,
						book.author,
						book.description or '',
						rating_value,
						book.category or '',
						book.stock,
						book.reserved_count,
					]
				)
	except Exception as e:
		# Log the error but don't raise - allow book creation to succeed even if legacy sync fails
		import logging
		logger = logging.getLogger(__name__)
		logger.warning(f"Failed to sync book {book.id} to legacy table: {str(e)}")
		# Don't raise - book is already created in Django model

