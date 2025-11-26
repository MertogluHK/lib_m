import math
import random
from typing import List, Dict, Any
import requests
from django.core.management.base import BaseCommand
from django.db import transaction
from books.models import Book


SEARCH_TERMS = [
    'fiction','novel','science','history','fantasy','mystery','biography','technology','philosophy','psychology','classic','literature','children','education','art','music','poetry','business','economics','health','travel'
]


def openlibrary_cover_url(cover_id: int, size: str = 'L') -> str:
    # Sizes: S, M, L
    return f"https://covers.openlibrary.org/b/id/{cover_id}-{size}.jpg"


def openlibrary_isbn_cover_url(isbn: str, size: str = 'L') -> str:
    return f"https://covers.openlibrary.org/b/isbn/{isbn}-{size}.jpg"


def pick_isbn(doc: Dict[str, Any]) -> str | None:
    for key in ('isbn_13', 'isbn'):  # isbn_13 first, fallback generic
        vals = doc.get(key)
        if vals:
            # Return first plausible numeric-only 10/13 string
            for v in vals:
                digits = ''.join(ch for ch in str(v) if ch.isdigit() or ch.upper() == 'X')
                if len(digits) in (10, 13):
                    return digits
    return None


class Command(BaseCommand):
    help = 'Load real books from Open Library with real covers. Ensures >=250 distinct and total copies >=700, max 4 per book.'

    def add_arguments(self, parser):
        parser.add_argument('--min_distinct', type=int, default=250)
        parser.add_argument('--min_total', type=int, default=700)
        parser.add_argument('--per_term', type=int, default=100)

    @transaction.atomic
    def handle(self, *args, **options):
        min_distinct = options['min_distinct']
        min_total = options['min_total']
        per_term = options['per_term']

        created_or_updated = 0
        total_copies = 0

        distinct_needed = min_distinct
        for term in SEARCH_TERMS:
            if distinct_needed <= 0:
                break
            try:
                resp = requests.get('https://openlibrary.org/search.json', params={'q': term, 'limit': per_term, 'fields': 'title,author_name,first_publish_year,isbn,cover_i'})
                resp.raise_for_status()
            except Exception:
                continue
            data = resp.json()
            docs: List[Dict[str, Any]] = data.get('docs', [])
            for doc in docs:
                if distinct_needed <= 0:
                    break
                title = doc.get('title') or None
                authors = doc.get('author_name') or []
                year = doc.get('first_publish_year') or None
                isbn = pick_isbn(doc)
                cover_i = doc.get('cover_i')

                if not title or not authors or not isbn:
                    continue

                cover_url = openlibrary_cover_url(cover_i) if cover_i else openlibrary_isbn_cover_url(isbn)
                author = ', '.join(authors[:3])
                publisher = ''

                stock = random.randint(1, 4)

                obj, was_created = Book.objects.get_or_create(
                    isbn=isbn,
                    defaults={
                        'title': title[:255],
                        'author': author[:255],
                        'publisher': publisher[:255],
                        'published_year': year or None,
                        'description': '',
                        'cover_url': cover_url,
                        'stock': stock,
                    }
                )
                if not was_created:
                    # update minimal fields, preserve existing if present
                    obj.title = obj.title or title[:255]
                    obj.author = obj.author or author[:255]
                    if not obj.cover_url:
                        obj.cover_url = cover_url
                    if not obj.published_year and year:
                        obj.published_year = year
                    if obj.stock < stock:
                        obj.stock = min(4, stock)
                    obj.save()

                created_or_updated += 1
                distinct_needed -= 1 if was_created else 0

        # Compute total copies and top up up to min_total (respecting max 4 per book)
        from django.db.models import Sum
        total_copies = Book.objects.aggregate(total=Sum('stock'))['total'] or 0
        if total_copies < min_total:
            for b in Book.objects.order_by('id'):
                if total_copies >= min_total:
                    break
                if b.stock < 4:
                    addable = min(4 - b.stock, min_total - total_copies)
                    b.stock += addable
                    b.save(update_fields=['stock'])
                    total_copies += addable

        self.stdout.write(self.style.SUCCESS(f"Distinct: {Book.objects.count()} | Total copies: {total_copies}"))


