from django.db import models
from django.core.validators import MinValueValidator


class Airline(models.Model):
    """Compagnie aérienne"""

    name = models.CharField(max_length=100)
    iata_code = models.CharField(max_length=2, unique=True)  # Ex: AF pour Air France

    def __str__(self):
        return f"{self.name} ({self.iata_code})"


class Airport(models.Model):
    """Aéroport"""

    name = models.CharField(max_length=100)
    iata_code = models.CharField(max_length=3, unique=True)  # Ex: CDG, ORY
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.iata_code})"


class Flight(models.Model):
    """Vol"""

    flight_number = models.CharField(max_length=10)
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE)
    departure_airport = models.ForeignKey(
        Airport, related_name="departures", on_delete=models.CASCADE
    )
    arrival_airport = models.ForeignKey(
        Airport, related_name="arrivals", on_delete=models.CASCADE
    )

    scheduled_departure = models.DateTimeField()
    actual_departure = models.DateTimeField(null=True, blank=True)
    scheduled_arrival = models.DateTimeField()
    actual_arrival = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ["flight_number", "airline", "scheduled_departure"]

    def __str__(self):
        return f"{self.airline.iata_code}{self.flight_number}"


class Turnaround(models.Model):
    """Période entre l'atterrissage et le décollage sur un même aéroport"""

    arrival_flight = models.OneToOneField(
        Flight, related_name="arrival_turnaround", on_delete=models.CASCADE
    )
    departure_flight = models.OneToOneField(
        Flight, related_name="departure_turnaround", on_delete=models.CASCADE
    )
    airport = models.ForeignKey(Airport, on_delete=models.CASCADE)

    scheduled_start = models.DateTimeField()
    actual_start = models.DateTimeField(null=True, blank=True)
    scheduled_end = models.DateTimeField()
    actual_end = models.DateTimeField(null=True, blank=True)

    def clean(self):
        from django.core.exceptions import ValidationError

        # Vérifier que les vols arrivent et partent du même aéroport
        if (
            self.arrival_flight.arrival_airport != self.airport
            or self.departure_flight.departure_airport != self.airport
        ):
            raise ValidationError(
                "Les vols doivent arriver et partir du même aéroport que le turnaround"
            )

    def __str__(self):
        return f"Turnaround {self.arrival_flight} -> {self.departure_flight}"
