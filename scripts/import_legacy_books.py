from django.db import connection, transaction
from books.models import Book


def run():
	with connection.cursor() as cursor:
		cursor.execute(
			"""
			SELECT id, book_name, page_count, author, book_exp, star, category, stok, reserve
			FROM books
			ORDER BY id
			"""
		)
		rows = cursor.fetchall()

	if not rows:
		print("No legacy rows found in books table.")
		return

	imported = 0
	with transaction.atomic():
		Book.objects.all().delete()
		for legacy_id, name, page_count, author, book_exp, star, category, stok, reserve in rows:
			book = Book(
				id=legacy_id,
				isbn=f"LEGACY-{legacy_id}",
				title=(name or "").strip() or f"Kitap {legacy_id}",
				author=(author or "").strip() or "Bilinmiyor",
				publisher="",
				published_year=None,
				page_count=int(page_count or 1),
				description=(book_exp or "").strip(),
				category=(category or "").strip(),
				cover_url="",
				external_rating=float(star or 0),
				stock=max(0, min(int(stok or 0), 4)),
				reserved_count=int(reserve or 0),
			)
			book.save(force_insert=True)
			imported += 1

	with connection.cursor() as cursor:
		cursor.execute(
			"SELECT setval('books_book_id_seq', %s, true)",
			[rows[-1][0]],
		)

	print(f"Imported {imported} legacy books into books_book.")


if __name__ == "__main__":
	run()

