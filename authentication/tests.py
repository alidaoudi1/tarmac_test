from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status

class AuthenticationTests(APITestCase):
    def setUp(self):
        # Create a test user
        self.test_user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
        # Define test data
        self.valid_login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        self.valid_register_data = {
            'username': 'newuser',
            'password': 'StrongPass123!',
            'email': 'newuser@example.com'
        }

    def test_login_success(self):
        """Test successful login"""
        url = reverse('secure-login')
        response = self.client.post(url, self.valid_login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])
        self.assertIn('user', response.data)

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        url = reverse('secure-login')
        invalid_data = {
            'username': 'testuser',
            'password': 'wrongpass'
        }
        response = self.client.post(url, invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)

    def test_login_missing_fields(self):
        """Test login with missing fields"""
        url = reverse('secure-login')
        incomplete_data = {'username': 'testuser'}
        response = self.client.post(url, incomplete_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_success(self):
        """Test successful registration"""
        url = reverse('secure-register')
        response = self.client.post(url, self.valid_register_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'newuser')
        
        # Verify user was created in database
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_existing_username(self):
        """Test registration with existing username"""
        url = reverse('secure-register')
        existing_user_data = self.valid_register_data.copy()
        existing_user_data['username'] = 'testuser'
        
        response = self.client.post(url, existing_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_weak_password(self):
        """Test registration with weak password"""
        url = reverse('secure-register')
        weak_password_data = self.valid_register_data.copy()
        weak_password_data['password'] = '123'
        
        response = self.client.post(url, weak_password_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Check that the response contains the password error
        self.assertIn('password', response.data)
        self.assertEqual(response.data['password'][0].code, 'min_length')  # Check for the specific error code

    def test_register_missing_fields(self):
        """Test registration with missing required fields"""
        url = reverse('secure-register')
        incomplete_data = {'username': 'newuser'}
        response = self.client.post(url, incomplete_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

