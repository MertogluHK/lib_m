from django.urls import path
from . import views

urlpatterns = [
	path('', views.home, name='home'),
	path('login/', views.login_page, name='login'),
	path('register/', views.register_page, name='register'),
	path('books/', views.books_page, name='books'),
	path('books/<int:book_id>/', views.book_detail_page, name='book_detail'),
	path('community/', views.community_page, name='community'),
	path('profile/', views.profile_page, name='profile'),
	path('reservations/', views.reservations_page, name='reservations'),
	path('payment/', views.payment_page, name='payment'),
	path('admin-panel/', views.admin_dashboard_page, name='admin_dashboard'),
]
