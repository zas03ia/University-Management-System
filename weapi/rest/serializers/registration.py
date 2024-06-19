from rest_framework import serializers
from django.contrib.auth import get_user_model 
from core.models import User
UserModel = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):

    password = serializers.CharField(style={'input_type':'password'}, write_only=True)

    def create(self, validated_data):

        user = UserModel.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
        )

        return user

    class Meta:
        model = User
        fields = ( "email", "username", "password", )