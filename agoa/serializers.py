from rest_framework import serializers
from .models import Airline, Airport, Flight, Turnaround

class AirlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airline
        fields = '__all__'

class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = '__all__'

class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = '__all__'

class TurnaroundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Turnaround
        fields = '__all__' 