import random
from typing import List
from django.core.management.base import BaseCommand
from django.db import transaction, models
from books.models import Book


SAMPLE_TITLES: List[str] = [
    # 300+ placeholder distinct titles (short synthetic dataset)
]

SAMPLE_AUTHORS: List[str] = [
    'Haruki Murakami','Stephen King','J. K. Rowling','Agatha Christie','George Orwell','Ursula K. Le Guin','Isaac Asimov','J. R. R. Tolkien','Jane Austen','Fyodor Dostoevsky','Ernest Hemingway','Mark Twain','Virginia Woolf','Leo Tolstoy','C. S. Lewis','Dan Brown','Paulo Coelho','Khaled Hosseini','Kazuo Ishiguro','Yuval Noah Harari','Elif Shafak','Orhan Pamuk','Ahmet Ümit','Zülfü Livaneli','Stefan Zweig','Franz Kafka','Gabriel García Márquez','Milan Kundera','Neil Gaiman','Terry Pratchett'
]

SAMPLE_PUBLISHERS: List[str] = [
    'Penguin','Vintage','HarperCollins','Random House','Bloomsbury','Canongate','Knopf','Faber & Faber','Simon & Schuster','Hachette','Dogan Kitap','Yapi Kredi','Everest'
]


def generate_titles(min_count: int) -> List[str]:
    base_titles = [
        'Shadows of Time','Echoes of Silence','Fractured Light','Forgotten Realms','Distant Horizons','Midnight Sun','Winds of Change','Crimson Rivers','Hidden Truths','Silent Whispers',
        'Golden Threads','Iron Will','Broken Compass','Paper Towns Reborn','Silver Lining','Neon Nights','Azure Skies','Scarlet Letters','Ivory Tower','Obsidian Heart',
        'Clockwork Dreams','Quantum Tides','Celestial Bridge','Emerald Forest','Dust and Stars','Glass Kingdom','Winter Garden','Summer Storm','Autumn Leaves','Spring Tide',
        'Atlas of Secrets','The Long Road','The Last Archive','City of Ghosts','Wired for Hope','Songs of the Sea','The Narrow Gate','Parallel Lines','Between Two Worlds','Edge of Reason',
    ]
    titles = list(base_titles)
    idx = 1
    while len(titles) < min_count:
        titles.append(f"Untitled Chronicle #{idx}")
        idx += 1
    return titles


class Command(BaseCommand):
    help = 'Load sample books: >=250 distinct and total copies >=700, max 4 per book.'

    def add_arguments(self, parser):
        parser.add_argument('--min_distinct', type=int, default=250)
        parser.add_argument('--min_total', type=int, default=700)

    @transaction.atomic
    def handle(self, *args, **options):
        min_distinct = options['min_distinct']
        min_total = options['min_total']

        titles = generate_titles(min_distinct)
        authors = SAMPLE_AUTHORS
        publishers = SAMPLE_PUBLISHERS

        created = 0
        total_copies = 0

        # First, ensure we have at least min_distinct unique books
        for i in range(min_distinct):
            title = titles[i]
            author = random.choice(authors)
            publisher = random.choice(publishers)
            year = random.randint(1950, 2024)
            isbn = f"978-{random.randint(1000000000, 1999999999)}"
            stock = random.randint(1, 4)

            obj, was_created = Book.objects.get_or_create(
                isbn=isbn,
                defaults={
                    'title': title,
                    'author': author,
                    'publisher': publisher,
                    'published_year': year,
                    'description': '',
                    'cover_url': f"https://picsum.photos/seed/{isbn}/300/450",
                    'stock': stock,
                }
            )
            # If ISBN collision, adjust
            if not was_created:
                obj.title = title
                obj.author = author
                obj.publisher = publisher
                obj.published_year = year
                obj.stock = stock
                if not obj.cover_url:
                    obj.cover_url = f"https://picsum.photos/seed/{isbn}/300/450"
                obj.save()
            created += 1 if was_created else 0
            total_copies += obj.stock

        # If total_copies still below target, bump stocks up to max 4
        if total_copies < min_total:
            qs = list(Book.objects.order_by('id'))
            idx = 0
            while total_copies < min_total and idx < len(qs):
                b = qs[idx]
                if b.stock < 4:
                    addable = min(4 - b.stock, min_total - total_copies)
                    b.stock += addable
                    b.save(update_fields=['stock'])
                    total_copies += addable
                idx += 1

        self.stdout.write(self.style.SUCCESS(f"Distinct books ensured: {Book.objects.count()} | Total copies: {Book.objects.aggregate(total=models.Sum('stock'))['total']}"))


