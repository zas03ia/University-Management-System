from rest_framework import permissions
from rest_framework.generics import CreateAPIView
from django.contrib.auth import get_user_model
from weapi.rest.serializers.registration import UserRegistrationSerializer

class UserRegistrationView(CreateAPIView):

    model = get_user_model()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegistrationSerializer