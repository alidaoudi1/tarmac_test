from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view
from django.db.models import Avg, Q, ExpressionWrapper, F, DurationField
from datetime import datetime, timedelta
from django.utils import timezone
from .models import Airline, Airport, Flight, Turnaround
from .serializers import (
    AirlineSerializer,
    AirportSerializer,
    FlightSerializer,
    TurnaroundSerializer,
)
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer


@extend_schema_view(
    list=extend_schema(description="List all airlines"),
    retrieve=extend_schema(description="Retrieve a specific airline"),
    create=extend_schema(description="Create a new airline"),
    update=extend_schema(description="Update an airline"),
    destroy=extend_schema(description="Delete an airline"),
)
class AirlineViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing airlines.

    Provides CRUD operations:
    - GET /api/airlines/ : List all airlines
    - POST /api/airlines/ : Create a new airline
    - GET /api/airlines/{id}/ : Retrieve a specific airline
    - PUT /api/airlines/{id}/ : Update an airline
    - DELETE /api/airlines/{id}/ : Delete an airline

    Required fields:
    - name: Full name of the airline
    - iata_code: 2-letter IATA code (unique)
    """

    queryset = Airline.objects.all()
    serializer_class = AirlineSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"])
    def turnaround_stats(self, request):
        """Get average turnaround duration by airline"""
        airlines = Airline.objects.all()
        stats = []

        for airline in airlines:
            # Calculate average duration for turnarounds involving this airline
            turnarounds = Turnaround.objects.filter(
                Q(arrival_flight__airline=airline)
                | Q(departure_flight__airline=airline)
            )
            if turnarounds.exists():
                avg_duration = turnarounds.aggregate(
                    avg_duration=Avg(
                        ExpressionWrapper(
                            F("scheduled_end") - F("scheduled_start"),
                            output_field=DurationField(),
                        )
                    )
                )["avg_duration"]

                if avg_duration:
                    stats.append(
                        {
                            "airline": airline.name,
                            "average_duration": avg_duration.total_seconds()
                            / 3600,  # Convert to hours
                        }
                    )

        return Response(stats)


@extend_schema_view(
    list=extend_schema(description="List all airports"),
    retrieve=extend_schema(description="Retrieve a specific airport"),
    create=extend_schema(description="Create a new airport"),
    update=extend_schema(description="Update an airport"),
    destroy=extend_schema(description="Delete an airport"),
)
class AirportViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing airports.

    Provides CRUD operations:
    - GET /api/airports/ : List all airports
    - POST /api/airports/ : Create a new airport
    - GET /api/airports/{id}/ : Retrieve a specific airport
    - PUT /api/airports/{id}/ : Update an airport
    - DELETE /api/airports/{id}/ : Delete an airport

    Required fields:
    - name: Full name of the airport
    - iata_code: 3-letter IATA code (unique)
    - city: City where the airport is located
    - country: Country where the airport is located
    """

    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"])
    def available_airports(self, request):
        """Get airports that have turnarounds for a specific date"""
        date = request.query_params.get("date")

        if not date:
            return Response(
                {"error": "Date parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d").date()

            # Get airports with turnarounds on this date
            airports = Airport.objects.filter(
                turnaround__scheduled_start__date=date_obj
            ).distinct()

            serializer = AirportSerializer(airports, many=True)
            return Response(serializer.data)
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST,
            )


@extend_schema_view(
    list=extend_schema(description="List all flights"),
    retrieve=extend_schema(description="Retrieve a specific flight"),
    create=extend_schema(description="Create a new flight"),
    update=extend_schema(description="Update a flight"),
    destroy=extend_schema(description="Delete a flight"),
)
class FlightViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing flights.

    Provides CRUD operations:
    - GET /api/flights/ : List all flights
    - POST /api/flights/ : Create a new flight
    - GET /api/flights/{id}/ : Retrieve a specific flight
    - PUT /api/flights/{id}/ : Update a flight
    - DELETE /api/flights/{id}/ : Delete a flight

    Required fields:
    - flight_number: Unique identifier for the flight
    - airline: Reference to airline performing the flight
    - departure_airport: Reference to departure airport
    - arrival_airport: Reference to arrival airport
    - scheduled_departure: Scheduled departure time
    - scheduled_arrival: Scheduled arrival time

    Optional fields:
    - actual_departure: Actual departure time
    - actual_arrival: Actual arrival time
    """

    permission_classes = [IsAuthenticated]
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer


@extend_schema_view(
    list=extend_schema(description="List all turnarounds"),
    retrieve=extend_schema(description="Retrieve a specific turnaround"),
    create=extend_schema(description="Create a new turnaround"),
)
class TurnaroundViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing turnarounds (ground operations between flights).

    Provides operations:
    - GET /api/turnarounds/ : List all turnarounds
    - POST /api/turnarounds/ : Create a new turnaround
    - GET /api/turnarounds/{id}/ : Retrieve a specific turnaround

    Additional endpoints:
    - GET /api/turnarounds/by_date_and_airport/?date=YYYY-MM-DD&airport=XXX
      Get all turnarounds for a specific date and airport

    - GET /api/turnarounds/average_duration/?date=YYYY-MM-DD
      Get average turnaround duration for a specific date

    Required fields:
    - arrival_flight: Reference to the arriving flight
    - departure_flight: Reference to the departing flight
    - airport: Reference to the airport where turnaround occurs
    - scheduled_start: Scheduled start time
    - scheduled_end: Scheduled end time

    Optional fields:
    - actual_start: Actual start time
    - actual_end: Actual end time

    Note: Only GET and POST methods are allowed (no updates or deletions)
    """

    permission_classes = [IsAuthenticated]
    queryset = Turnaround.objects.all()
    serializer_class = TurnaroundSerializer
    http_method_names = ["get", "post"]

    @action(detail=False, methods=["get"])
    def by_date_and_airport(self, request):
        """Get turnarounds for a specific date and airport"""
        date = request.query_params.get("date")
        airport_code = request.query_params.get("airport_code")

        if not date or not airport_code:
            return Response(
                {"error": "Both date and airport_code are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d").date()
            airport = Airport.objects.get(iata_code=airport_code)

            turnarounds = Turnaround.objects.filter(
                scheduled_start__date=date_obj, airport=airport
            )

            serializer = self.get_serializer(turnarounds, many=True)
            return Response(serializer.data)
        except (ValueError, Airport.DoesNotExist):
            return Response(
                {"error": "Invalid date format or airport code"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=["get"])
    def average_duration(self, request):
        """
        Calculate average turnaround duration for a specific date.

        Query parameters:
        - date: Date in YYYY-MM-DD format

        Returns:
        - date: The requested date
        - average_duration_minutes: Average duration in minutes
        """
        date = request.query_params.get("date")

        if not date:
            return Response(
                {"error": "Date parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Calculate average duration
        avg_duration = Turnaround.objects.filter(scheduled_start__date=date).aggregate(
            avg_duration=Avg("departure_flight__scheduled_departure")
            - Avg("arrival_flight__scheduled_departure")
        )["avg_duration"]

        if avg_duration is None:
            return Response(
                {"error": "No turnarounds found for this date"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "date": date,
                "average_duration_minutes": avg_duration.total_seconds() / 60,
            }
        )

    @action(detail=False, methods=["get"])
    def turnaround_stats(self, request):
        """Get average turnaround duration by airline"""
        airlines = Airline.objects.all()
        stats = []

        for airline in airlines:
            # Calculate average duration for turnarounds involving this airline
            turnarounds = Turnaround.objects.filter(
                Q(arrival_flight__airline=airline)
                | Q(departure_flight__airline=airline)
            )
            if turnarounds.exists():
                avg_duration = turnarounds.aggregate(
                    avg_duration=Avg(
                        ExpressionWrapper(
                            F("scheduled_end") - F("scheduled_start"),
                            output_field=DurationField(),
                        )
                    )
                )["avg_duration"]

                if avg_duration:
                    stats.append(
                        {
                            "airline": airline.name,
                            "average_duration": avg_duration.total_seconds()
                            / 3600,  # Convert to hours
                        }
                    )

        return Response(stats)

    @action(detail=False, methods=["get"])
    def available_dates(self, request):
        """Get dates that have turnarounds scheduled"""
        dates = Turnaround.objects.dates("scheduled_start", "day")
        return Response([date.strftime("%Y-%m-%d") for date in dates])
