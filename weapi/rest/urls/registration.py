from django.urls import path
from weapi.rest.views.registration import UserRegistrationView

urlpatterns = [
    path('/register', UserRegistrationView.as_view(), name='user_registration'),
]
