from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VehicleViewSet, BookingViewSet
from . import views

router = DefaultRouter()
router.register(r'vehicles', VehicleViewSet, basename='vehicle')
router.register(r'bookings', BookingViewSet, basename='booking')

app_name = 'inventory'

urlpatterns = [
    # API
    path('api/', include(router.urls)),

    # Frontend pages
    path('', views.vehicle_list_page, name='vehicle_list'),
    path('vehicles/<int:pk>/', views.vehicle_detail_page, name='vehicle_detail'),
    path('bookings/success/<int:pk>/', views.booking_success_page, name='booking_success'),
    path('bookings/', views.booking_list_page, name='booking_list'),
]
