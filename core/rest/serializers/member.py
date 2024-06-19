from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from custom_utilities.custom_permission import *
from django.db.models import Subquery
from core.models import *
from django.http import HttpResponse
from rest_framework.exceptions import ValidationError
from custom_utilities.subdomain import *
from django.db import transaction
    
class UserShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']

class PrivateOrganizationListSerializer(serializers.ModelSerializer):
    organization_uid = serializers.CharField(source='uid', read_only=True)
    organization_subdomain = serializers.CharField(source='subdomain', write_only=True)
    subdomain = serializers.SerializerMethodField(read_only=True)
    username = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(style={'input_type':'password'}, write_only=True)
    admins = serializers.SerializerMethodField(read_only=True)
    def get_subdomain(self, obj):
        return str(obj.subdomain).lower() if obj.subdomain else None
    def get_admins(self, obj):
        users = User.objects.filter(id__in=Subquery(OrganizationUser.objects.filter(organization__uid=obj.uid, role='Admin').values('user')))
        return [f'Username: {user.username} | Email: {user.email}' for user in users]
    class Meta:
        model = Organization
        fields = ['organization_uid', 'name', 'description', 'branch', 'organization_subdomain', 'subdomain', 'username', 'email', 'password','admins']  
        
    def create(self, validated_data):
        try:
            with transaction.atomic():
                user=None
                if not User.objects.filter(email=validated_data['email'], username=validated_data['username']).exists():
                    try:
                        user = User.objects.create_user(email=validated_data['email'], username=validated_data['username'], password=validated_data['password'])
                    except:
                        raise serializers.ValidationError("User creation failed")
                if Organization.objects.filter(name=validated_data['name'].title().strip(), description=validated_data['description'].title().strip(), subdomain=validated_data['subdomain'].title().strip()).exists():
                    raise serializers.ValidationError("Organization already exists")
                try:
                    organization = Organization.objects.create(name=validated_data['name'], description=validated_data['description'], branch=validated_data['branch'], subdomain=validated_data['subdomain'])
                except:
                    raise serializers.ValidationError("Organization creation failed")
                if OrganizationUser.objects.filter(organization=organization, user=user, role='Admin').exists():
                    raise serializers.ValidationError("Organization user already exists with this role")
                OrganizationUser.objects.create(organization=organization, user=user, role='Admin', status=True)
            return organization
        except Exception as e:
            raise serializers.ValidationError({"detail": str(e)})
    
