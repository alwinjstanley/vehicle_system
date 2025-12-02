from rest_framework import serializers
from .models import Vehicle, Booking
from datetime import date
from decimal import Decimal
from django.db import transaction

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = '__all__'


class BookingSerializer(serializers.ModelSerializer):
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'vehicle', 'customer_name', 'customer_phone', 'start_date', 'end_date', 'total_amount', 'created_at']

    def validate_customer_phone(self, value):
        digits = ''.join(ch for ch in value if ch.isdigit())
        if len(digits) != 10:
            raise serializers.ValidationError("Phone number must contain exactly 10 digits.")
        return digits

    def validate(self, data):
        start = data.get('start_date')
        end = data.get('end_date')
        vehicle = data.get('vehicle')

        today = date.today()
        if start < today:
            raise serializers.ValidationError({'start_date': 'Start date cannot be in the past.'})
        if end <= start:
            raise serializers.ValidationError({'end_date': 'End date must be after start date.'})

        overlapping = Booking.objects.filter(
            vehicle=vehicle,
            start_date__lte=end,
            end_date__gte=start
        )
        if self.instance:
            overlapping = overlapping.exclude(pk=self.instance.pk)

        if overlapping.exists():
            raise serializers.ValidationError("This vehicle is already booked for the selected dates (overlap).")

        return data

    def create(self, validated_data):
        vehicle = validated_data['vehicle']
        start = validated_data['start_date']
        end = validated_data['end_date']
        days = (end - start).days
        if days <= 0:
            raise serializers.ValidationError("Booking must be at least one day long.")

        total = (vehicle.price_per_day * Decimal(days)).quantize(Decimal('0.01'))

        with transaction.atomic():
            booking = Booking.objects.create(
                vehicle=vehicle,
                customer_name=validated_data['customer_name'],
                customer_phone=validated_data['customer_phone'],
                start_date=start,
                end_date=end,
                total_amount=total
            )
            vehicle.is_available = False
            vehicle.save(update_fields=['is_available'])
        return booking

    def update(self, instance, validated_data):
        instance.customer_name = validated_data.get('customer_name', instance.customer_name)
        phone = validated_data.get('customer_phone', instance.customer_phone)
        instance.customer_phone = phone

        start = validated_data.get('start_date', instance.start_date)
        end = validated_data.get('end_date', instance.end_date)
        vehicle = validated_data.get('vehicle', instance.vehicle)

        temp_data = {'start_date': start, 'end_date': end, 'vehicle': vehicle}
        self.validate(temp_data)

        days = (end - start).days
        total = (vehicle.price_per_day * Decimal(days)).quantize(Decimal('0.01'))

        with transaction.atomic():
            old_vehicle = instance.vehicle
            if old_vehicle != vehicle:
                old_vehicle.is_available = True
                old_vehicle.save(update_fields=['is_available'])
                vehicle.is_available = False
                vehicle.save(update_fields=['is_available'])

            instance.vehicle = vehicle
            instance.start_date = start
            instance.end_date = end
            instance.total_amount = total
            instance.save()
        return instance
