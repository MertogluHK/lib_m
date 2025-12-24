from django.shortcuts import render, get_object_or_404
from books.models import Book
from books.utils import get_book_cover_image_url

# Create your views here.

def home(request):
	return render(request, 'frontend/home.html')

def login_page(request):
	return render(request, 'frontend/login.html')

def register_page(request):
	return render(request, 'frontend/register.html')

def books_page(request):
	return render(request, 'frontend/books.html')

def book_detail_page(request, book_id):
	book = get_object_or_404(Book.objects.prefetch_related('reviews'), pk=book_id)
	average = float(book.average_rating or 0.0)
	filled = max(0, min(5, int(round(average))))
	star_string = '★' * filled + '☆' * (5 - filled)
	category_list = [c.strip() for c in (book.category or '').split(',') if c.strip()]
	stock_available = book.stock > 0
	book_image_url = get_book_cover_image_url(book.id)
	return render(
		request,
		'frontend/book_detail.html',
		{
			'book': book,
			'star_string': star_string,
			'average_rating': average,
			'category_list': category_list,
			'stock_available': stock_available,
			'book_image_url': book_image_url,
		}
	)

def community_page(request):
	return render(request, 'frontend/community.html')

def reservations_page(request):
	return render(request, 'frontend/reservations.html')

def payment_page(request):
    # Server-side guard: eğer query string'de kitap bilgisi varsa stok kontrolü yap
    from books.models import Book
    q = request.GET.get('q', '').strip()
    stock_available = True
    stock_message = ''
    
    if q:
        try:
            # Kitap adından arayıp stokunu kontrol et
            book = Book.objects.filter(title__icontains=q).first()
            if book:
                stock_available = book.stock > 0
                if not stock_available:
                    stock_message = 'Seçilen kitap şu anda stokta bulunmamaktadır.'
        except Exception:
            # Hata durumunda ödemeye izin ver (client-side kontrol yapacak)
            stock_available = True
    
    return render(request, 'frontend/payment.html', {
        'stock_available': stock_available,
        'stock_message': stock_message
    })

def admin_dashboard_page(request):
	return render(request, 'frontend/admin_dashboard.html')

def profile_page(request):
	return render(request, 'frontend/profile.html')