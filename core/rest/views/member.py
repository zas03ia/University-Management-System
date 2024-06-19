from rest_framework.generics import ListCreateAPIView, RetrieveDestroyAPIView, ListAPIView
from core.models import *
from rest_framework.permissions import IsAuthenticated
from core.rest.serializers.member import *
from django.shortcuts import get_object_or_404
from custom_utilities.custom_permission import IsAdmin, IsStudent, IsFaculty, IsMember, IsSuperUser
from django.db.models import Subquery
from weapi.rest.serializers.department import PrivateOrganizationDetailSerializer

class PrivateMeView(ListAPIView):
    serializer_class = UserShowSerializer
    def get_queryset(self):
        queryset = User.objects.filter(id=self.request.user.id)
        return queryset

class PrivateOrganizationListView(ListCreateAPIView):
    queryset = Organization.objects.filter()
    serializer_class = PrivateOrganizationListSerializer
    def get_permissions(self):
        if self.request.method == 'POST': 
            return [IsSuperUser()] 
        return [IsAuthenticated()]
    def get_queryset(self):
        if self.request.user.is_superuser:
            queryset = Organization.objects.filter()
            return queryset
        else:
            queryset = Organization.objects.filter(id__in=Subquery(OrganizationUser.objects.filter(user=self.request.user).values('organization')))
            return queryset
        



class PrivateOrganizationDestroyView(RetrieveDestroyAPIView):
    serializer_class = PrivateOrganizationDetailSerializer
    def get_object(self):
        organization_uid = self.kwargs.get('organization_uid')
        organization = get_object_or_404(Organization, uid=organization_uid)
        return organization
    permission_classes = [IsSuperUser] 