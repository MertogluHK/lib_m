from django.contrib import admin
from .models import Reservation


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('reservation_id', 'user', 'book', 'status_badge', 'pickup_date_display', 'return_date_display', 'picked_up_at_display', 'returned_at_display')
    list_filter = ('status', 'pickup_date', 'reserved_at')
    search_fields = ('user__username', 'book__title')
    readonly_fields = ('reserved_at', 'picked_up_at', 'cancelled_at', 'returned_at', 'return_date_display')
    fields = (
        'user', 'book', 'status', 'pickup_date', 'pickup_deadline_days', 'return_date_display', 'deposit_amount',
        'reserved_at', 'picked_up_at', 'cancelled_at', 'returned_at', 'refund_issued',
    )

    def reservation_id(self, obj):
        return f"#{obj.id}"
    reservation_id.short_description = 'ID'

    def status_badge(self, obj):
        status_colors = {
            'PENDING': '#FFA500',
            'PICKED_UP': '#0000FF',
            'CANCELLED': '#FF0000',
            'RETURNED': '#008000',
            'EXPIRED': '#808080'
        }
        color = status_colors.get(obj.status, '#000000')
        status_label = obj.get_status_display()
        return f'<span style="color: {color}; font-weight: bold;">{status_label}</span>'
    status_badge.allow_tags = True
    status_badge.short_description = 'Durum'

    def pickup_date_display(self, obj):
        if obj.pickup_date:
            return obj.pickup_date.strftime('%d.%m.%Y')
        return '-'
    pickup_date_display.short_description = 'Alınacağı Tarihi'
    pickup_date_display.admin_order_field = 'pickup_date'

    def return_date_display(self, obj):
        if obj.return_date:
            return obj.return_date.strftime('%d.%m.%Y')
        return '-'
    return_date_display.short_description = 'İade Tarihi'

    def picked_up_at_display(self, obj):
        if obj.picked_up_at:
            return obj.picked_up_at.strftime('%d.%m.%Y %H:%M')
        return '-'
    picked_up_at_display.short_description = 'Alım Zamanı'
    picked_up_at_display.admin_order_field = 'picked_up_at'

    def returned_at_display(self, obj):
        if obj.returned_at:
            return obj.returned_at.strftime('%d.%m.%Y %H:%M')
        return '-'
    returned_at_display.short_description = 'İade Zamanı'
    returned_at_display.admin_order_field = 'returned_at'
