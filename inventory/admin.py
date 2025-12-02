from django.contrib import admin
from .models import Vehicle, Booking

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['id', 'brand', 'name', 'year', 'price_per_day', 'fuel_type', 'is_available']
    list_filter = ['brand', 'fuel_type', 'is_available']
    search_fields = ['brand', 'name']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'vehicle', 'customer_name', 'customer_phone', 'start_date', 'end_date', 'total_amount', 'created_at']
    list_filter = ['vehicle', 'start_date', 'end_date']
    search_fields = ['customer_name', 'customer_phone']
