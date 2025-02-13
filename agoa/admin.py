from django.contrib import admin
from .models import Airline, Airport, Flight, Turnaround

@admin.register(Airline)
class AirlineAdmin(admin.ModelAdmin):
    """Configure Airline list view with name and IATA code."""
    list_display = ('name', 'iata_code')

@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    """Configure Airport list view with name, IATA code, location."""
    list_display = ('name', 'iata_code', 'city', 'country')

@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    """Configure Flight list view with flight details and schedule."""
    list_display = ('flight_number', 'airline', 'departure_airport', 'arrival_airport', 'scheduled_departure')

@admin.register(Turnaround)
class TurnaroundAdmin(admin.ModelAdmin):
    """Configure Turnaround list view with connected flights and timing."""
    list_display = ('arrival_flight', 'departure_flight', 'airport', 'scheduled_start') 