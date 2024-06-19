from rest_framework.permissions import BasePermission
from core.models import OrganizationUser
from custom_utilities.subdomain import get_organization
from session.models import Session
from datetime import date

class IsInRole(BasePermission):
    allowed_roles = []

    def has_permission(self, request, view):
        user = request.user
        if user.is_authenticated:
            organization= get_organization(request) 
            organization_user = OrganizationUser.objects.filter(user=user, organization=organization).first()
            if organization_user:
                return organization_user.role in self.allowed_roles
        return False
    
class StudentAdvising(BasePermission):
    allowed_roles = []

    def has_permission(self, request, view):
        user = request.user
        if user.is_authenticated:
            organization= get_organization(request) 
            organization_user = OrganizationUser.objects.filter(user=user, organization=organization).first()
            session = Session.objects.filter(organization=organization, advising_start__lte=date.today(), advising_end__gte=date.today()).first()
            if organization_user and session:
                return organization_user.role == 'Student'
        return False
    
class IsAdminOrSuperUser(BasePermission):
    allowed_roles = []

    def has_permission(self, request, view):
        user = request.user
        if user.is_authenticated:
            organization= get_organization(request) 
            organization_user = OrganizationUser.objects.filter(user=user, organization=organization).first()
            if organization_user:
                superuser = request.user and request.user.is_superuser
                return organization_user.role=='Admin' or superuser
        return False

class IsStudent(IsInRole):
    allowed_roles = ['Student']

class IsFaculty(IsInRole):
    allowed_roles = ['Faculty']

class IsAdmin(IsInRole):
    allowed_roles = ['Admin']
    
class IsAdminOrFaculty(IsInRole):
    allowed_roles = ['Admin', 'Faculty']

class IsMember(IsInRole):
    allowed_roles = ['Student', 'Faculty', 'Admin']

class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser

