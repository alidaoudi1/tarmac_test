from django.urls import path
from .views import SecureLoginView, SecureRegisterView

urlpatterns = [
    path('login/', SecureLoginView.as_view(), name='secure-login'),
    path('register/', SecureRegisterView.as_view(), name='secure-register'),
] 