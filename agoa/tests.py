from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import Airline, Airport, Flight, Turnaround
from datetime import datetime, timedelta
from django.utils import timezone

class AgoaAPITests(APITestCase):
    def setUp(self):
        """Initialize test data"""
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.force_authenticate(user=self.user)
        
        # Create test airline
        self.airline = Airline.objects.create(
            name='Test Airline',
            iata_code='TA'
        )
        
        # Create test airports
        self.airport_cdg = Airport.objects.create(
            name='Paris Charles de Gaulle',
            iata_code='CDG',
            city='Paris',
            country='France'
        )
        self.airport_jfk = Airport.objects.create(
            name='John F. Kennedy',
            iata_code='JFK',
            city='New York',
            country='USA'
        )
        
        # Create test flight
        self.flight = Flight.objects.create(
            flight_number='TA123',
            airline=self.airline,
            departure_airport=self.airport_cdg,
            arrival_airport=self.airport_jfk,
            scheduled_departure=timezone.now(),
            scheduled_arrival=timezone.now() + timedelta(hours=8)
        )

    # Airline Tests
    def test_list_airlines(self):
        """Test retrieving airlines list"""
        url = reverse('airline-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['iata_code'], 'TA')

    def test_create_airline(self):
        """Test creating a new airline"""
        url = reverse('airline-list')
        data = {
            'name': 'New Airline',
            'iata_code': 'NA'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Airline.objects.count(), 2)

    # Airport Tests
    def test_list_airports(self):
        """Test retrieving airports list"""
        url = reverse('airport-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_create_airport(self):
        """Test creating a new airport"""
        url = reverse('airport-list')
        data = {
            'name': 'Los Angeles International',
            'iata_code': 'LAX',
            'city': 'Los Angeles',
            'country': 'USA'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Airport.objects.count(), 3)

    # Flight Tests
    def test_list_flights(self):
        """Test retrieving flights list"""
        url = reverse('flight-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_flight(self):
        """Test creating a new flight"""
        url = reverse('flight-list')
        data = {
            'flight_number': 'TA456',
            'airline': self.airline.id,
            'departure_airport': self.airport_cdg.id,
            'arrival_airport': self.airport_jfk.id,
            'scheduled_departure': timezone.now().isoformat(),
            'scheduled_arrival': (timezone.now() + timedelta(hours=8)).isoformat()
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Flight.objects.count(), 2)

    # Turnaround Tests
    def test_create_turnaround(self):
        """Test creating a new turnaround"""
        url = reverse('turnaround-list')
        data = {
            'arrival_flight': self.flight.id,
            'departure_flight': self.flight.id,  # Not realistic but ok for test
            'airport': self.airport_jfk.id,
            'scheduled_start': timezone.now().isoformat(),
            'scheduled_end': (timezone.now() + timedelta(hours=2)).isoformat()
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_turnaround_by_date_and_airport(self):
        """Test retrieving turnarounds by date and airport"""
        # First create a turnaround
        turnaround = Turnaround.objects.create(
            arrival_flight=self.flight,
            departure_flight=self.flight,
            airport=self.airport_jfk,
            scheduled_start=timezone.now(),
            scheduled_end=timezone.now() + timedelta(hours=2)
        )
        
        url = reverse('turnaround-by-date-and-airport')
        response = self.client.get(url, {
            'date': timezone.now().strftime('%Y-%m-%d'),
            'airport': self.airport_jfk.iata_code
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    # Authentication Tests
    def test_login(self):
        """Test user login"""
        url = reverse('secure-login')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)

    def test_register(self):
        """Test user registration"""
        url = reverse('secure-register')
        data = {
            'username': 'newuser',
            'password': 'newpass123',
            'email': 'newuser@example.com'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', response.data)

    def test_unauthorized_access(self):
        """Test that unauthorized users cannot access the API"""
        self.client.force_authenticate(user=None)
        url = reverse('airline-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED) 