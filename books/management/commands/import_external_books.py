import os
from typing import Optional

import psycopg2
from django.core.management.base import BaseCommand
from django.db import transaction

from books.models import Book


def normalize_text(value: Optional[str]) -> str:
	if not value:
		return ''
	return value.strip()


class Command(BaseCommand):
	help = "Import books from external PostgreSQL database (book_db) into the local Book model."

	def add_arguments(self, parser):
		parser.add_argument('--limit', type=int, help='Limit number of rows to import')

	def handle(self, *args, **options):
		db_name = os.getenv('PG_BOOK_DB', 'book_db')
		db_user = os.getenv('PG_BOOK_USER', 'postgres')
		db_password = os.getenv('PG_BOOK_PASSWORD', '....')
		db_host = os.getenv('PG_BOOK_HOST', 'localhost')
		db_port = os.getenv('PG_BOOK_PORT', '5432')

		limit = options.get('limit')

		self.stdout.write(self.style.NOTICE(f"Connecting to Postgres {db_user}@{db_host}:{db_port}/{db_name}"))

		conn = psycopg2.connect(
			dbname=db_name,
			user=db_user,
			password=db_password,
			host=db_host,
			port=db_port,
		)
		cur = conn.cursor()

		query = "SELECT id, book_name, page_count, author, book_exp, star, category, stok, reserve FROM books ORDER BY id"
		if limit:
			query += " LIMIT %s"
			cur.execute(query, (limit,))
		else:
			cur.execute(query)
		rows = cur.fetchall()

		self.stdout.write(self.style.NOTICE(f"Found {len(rows)} rows"))

		imported = 0
		updated = 0
		with transaction.atomic():
			for external_id, book_name, page_count, author, book_exp, star, category, stok, reserve in rows:
				title = normalize_text(book_name) or f"Kitap {external_id}"
				author_name = normalize_text(author) or "Bilinmeyen Yazar"
				description = normalize_text(book_exp)
				categories = normalize_text(category)
				external_rating = None
				try:
					if star is not None:
						external_rating = float(star)
				except (TypeError, ValueError):
					external_rating = None
				isbn = f"PGSRC-{external_id}"
				stock_value = max(0, int(stok or 0))
				reserve_value = max(0, int(reserve or 0))

				obj, created = Book.objects.update_or_create(
					isbn=isbn,
					defaults={
						'title': title[:255],
						'author': author_name[:255],
						'publisher': '',
						'published_year': None,
						'description': description,
						'category': categories[:255],
						'cover_url': '',
						'external_rating': external_rating,
						'stock': stock_value,
						'reserved_count': reserve_value,
					}
				)
				if created:
					imported += 1
				else:
					updated += 1

		cur.close()
		conn.close()

		self.stdout.write(self.style.SUCCESS(f"Imported {imported}, updated {updated} records."))

