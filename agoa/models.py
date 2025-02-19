from typing import Any
from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from datetime import datetime


class Airline(models.Model):
    """Airline Company"""

    name: str = models.CharField(max_length=100)
    iata_code: str = models.CharField(max_length=2, unique=True)  # Ex: AF for Air France

    def __str__(self) -> str:
        return f"{self.name} ({self.iata_code})"


class Airport(models.Model):
    """Airport"""

    name: str = models.CharField(max_length=100)
    iata_code: str = models.CharField(max_length=3, unique=True)  # Ex: CDG, ORY
    city: str = models.CharField(max_length=100)
    country: str = models.CharField(max_length=100)

    def __str__(self) -> str:
        return f"{self.name} ({self.iata_code})"


class Flight(models.Model):
    """Flight"""

    flight_number: str = models.CharField(max_length=10)
    airline: Airline = models.ForeignKey(Airline, on_delete=models.CASCADE)
    departure_airport: Airport = models.ForeignKey(
        Airport, related_name="departures", on_delete=models.CASCADE
    )
    arrival_airport: Airport = models.ForeignKey(
        Airport, related_name="arrivals", on_delete=models.CASCADE
    )

    scheduled_departure: datetime = models.DateTimeField()
    actual_departure: datetime | None = models.DateTimeField(null=True, blank=True)
    scheduled_arrival: datetime = models.DateTimeField()
    actual_arrival: datetime | None = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ["flight_number", "airline", "scheduled_departure"]

    def __str__(self) -> str:
        return f"{self.airline.iata_code}{self.flight_number}"


class Turnaround(models.Model):
    """Period between landing and takeoff at the same airport"""

    arrival_flight: Flight = models.OneToOneField(
        Flight, related_name="arrival_turnaround", on_delete=models.CASCADE
    )
    departure_flight: Flight = models.OneToOneField(
        Flight, related_name="departure_turnaround", on_delete=models.CASCADE
    )
    airport: Airport = models.ForeignKey(Airport, on_delete=models.CASCADE)

    scheduled_start: datetime = models.DateTimeField()
    actual_start: datetime | None = models.DateTimeField(null=True, blank=True)
    scheduled_end: datetime = models.DateTimeField()
    actual_end: datetime | None = models.DateTimeField(null=True, blank=True)

    def clean(self) -> None:
        if (
            self.arrival_flight.arrival_airport != self.airport
            or self.departure_flight.departure_airport != self.airport
        ):
            raise ValidationError(
                "Flights must arrive and depart from the same airport as the turnaround"
            )

    def __str__(self) -> str:
        return f"Turnaround {self.arrival_flight} -> {self.departure_flight}"
