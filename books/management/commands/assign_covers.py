from django.core.management.base import BaseCommand
from books.models import Book


class Command(BaseCommand):
    help = 'Assign cover_url to books missing it using a deterministic placeholder.'

    def handle(self, *args, **options):
        updated = 0
        for b in Book.objects.filter(cover_url=''):
            b.cover_url = f"https://picsum.photos/seed/{b.isbn}/300/450"
            b.save(update_fields=['cover_url'])
            updated += 1
        self.stdout.write(self.style.SUCCESS(f"Updated covers for {updated} books"))


