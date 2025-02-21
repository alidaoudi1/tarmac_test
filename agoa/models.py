from typing import Any
from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from datetime import datetime
from django.db.models import CharField, ForeignKey, DateTimeField, OneToOneField


class Airline(models.Model):
    """Airline Company"""

    name: models.CharField = models.CharField(max_length=100)
    iata_code: models.CharField = models.CharField(
        max_length=2, unique=True
    )  # Ex: AF for Air France

    def __str__(self) -> str:
        return f"{self.name} ({self.iata_code})"


class Airport(models.Model):
    """Airport"""

    name: models.CharField = models.CharField(max_length=100)
    iata_code: models.CharField = models.CharField(
        max_length=3, unique=True
    )  # Ex: CDG, ORY
    city: models.CharField = models.CharField(max_length=100)
    country: models.CharField = models.CharField(max_length=100)
    latitude: models.FloatField = models.FloatField()
    longitude: models.FloatField = models.FloatField()

    def __str__(self) -> str:
        return f"{self.iata_code} - {self.name}"


class Flight(models.Model):
    """Flight"""

    flight_number: models.CharField = models.CharField(max_length=10)
    airline: models.ForeignKey = models.ForeignKey(Airline, on_delete=models.CASCADE)
    departure_airport: models.ForeignKey = models.ForeignKey(
        Airport, related_name="departures", on_delete=models.CASCADE
    )
    arrival_airport: models.ForeignKey = models.ForeignKey(
        Airport, related_name="arrivals", on_delete=models.CASCADE
    )

    scheduled_departure: models.DateTimeField = models.DateTimeField()
    actual_departure: models.DateTimeField = models.DateTimeField(null=True, blank=True)
    scheduled_arrival: models.DateTimeField = models.DateTimeField()
    actual_arrival: models.DateTimeField = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ["flight_number", "airline", "scheduled_departure"]

    def __str__(self) -> str:
        airline: Airline = self.airline  # Type annotation helps type checker
        if airline:
            return f"{airline.iata_code}{self.flight_number}"
        return f"Flight {self.flight_number}"


class Turnaround(models.Model):
    """Period between landing and takeoff at the same airport"""

    arrival_flight: models.OneToOneField["Flight", Any] = models.OneToOneField(
        "Flight", related_name="arrival_turnaround", on_delete=models.CASCADE
    )
    departure_flight: models.OneToOneField["Flight", Any] = models.OneToOneField(
        "Flight", related_name="departure_turnaround", on_delete=models.CASCADE
    )
    airport: models.ForeignKey["Airport", Any] = models.ForeignKey(
        "Airport", on_delete=models.CASCADE
    )

    scheduled_start: models.DateTimeField = models.DateTimeField()
    actual_start: models.DateTimeField = models.DateTimeField(null=True, blank=True)
    scheduled_end: models.DateTimeField = models.DateTimeField()
    actual_end: models.DateTimeField = models.DateTimeField(null=True, blank=True)

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
