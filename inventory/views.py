from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Vehicle, Booking
from .serializers import VehicleSerializer, BookingSerializer

# API viewsets
class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all().order_by('id')
    serializer_class = VehicleSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['brand', 'fuel_type', 'is_available']
    search_fields = ['name', 'brand']

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.select_related('vehicle').all().order_by('-created_at')
    serializer_class = BookingSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['vehicle', 'customer_name']


# ---------------- Frontend views ----------------
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .forms import BookingForm
from django.contrib import messages
from datetime import date

def vehicle_list_page(request):
    vehicles = Vehicle.objects.all().order_by('id')
    brand = request.GET.get('brand')
    fuel = request.GET.get('fuel_type')
    is_avail = request.GET.get('is_available')

    if brand:
        vehicles = vehicles.filter(brand__iexact=brand)
    if fuel:
        vehicles = vehicles.filter(fuel_type__iexact=fuel)
    if is_avail is not None and is_avail != '':
        if is_avail.lower() in ['true', '1', 'yes']:
            vehicles = vehicles.filter(is_available=True)
        elif is_avail.lower() in ['false', '0', 'no']:
            vehicles = vehicles.filter(is_available=False)

    context = {
        'vehicles': vehicles,
        'today': date.today().isoformat(),
    }
    return render(request, 'inventory/vehicle_list.html', context)

def vehicle_detail_page(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            payload = {
                'vehicle': vehicle.id,
                'customer_name': form.cleaned_data['customer_name'],
                'customer_phone': form.cleaned_data['customer_phone'],
                'start_date': form.cleaned_data['start_date'],
                'end_date': form.cleaned_data['end_date'],
            }
            serializer = BookingSerializer(data=payload)
            if serializer.is_valid():
                booking = serializer.save()
                messages.success(request, 'Booking created successfully!')
                return redirect(reverse('inventory:booking_success', kwargs={'pk': booking.pk}))
            else:
                # show serializer errors as messages
                for key, val in serializer.errors.items():
                    messages.error(request, f"{key}: {val}")
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = BookingForm(initial={'start_date': date.today().isoformat()})

    context = {
        'vehicle': vehicle,
        'form': form,
    }
    return render(request, 'inventory/vehicle_detail.html', context)

def booking_success_page(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    return render(request, 'inventory/booking_success.html', {'booking': booking})

def booking_list_page(request):
    bookings = Booking.objects.select_related('vehicle').order_by('-created_at')
    return render(request, 'inventory/booking_list.html', {'bookings': bookings})
