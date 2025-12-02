from django.db import models
from decimal import Decimal
from django.core.validators import MinValueValidator

class Vehicle(models.Model):
    FUEL_PETROL = 'Petrol'
    FUEL_DIESEL = 'Diesel'
    FUEL_ELECTRIC = 'Electric'
    FUEL_HYBRID = 'Hybrid'
    FUEL_CHOICES = [
        (FUEL_PETROL, 'Petrol'),
        (FUEL_DIESEL, 'Diesel'),
        (FUEL_ELECTRIC, 'Electric'),
        (FUEL_HYBRID, 'Hybrid'),
    ]

    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.brand} {self.name} ({self.year})"


class Booking(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='bookings')
    customer_name = models.CharField(max_length=200)
    customer_phone = models.CharField(max_length=15)
    start_date = models.DateField()
    end_date = models.DateField()
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking {self.id} - {self.customer_name} ({self.vehicle})"
