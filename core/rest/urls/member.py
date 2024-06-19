from django.urls import path
from core.rest.views.member import *

urlpatterns = [
    path('', PrivateMeView.as_view(), name='me'),
    path('/my_organizations', PrivateOrganizationListView.as_view(), name='my-organizations'),
    path('/my_organizations/<uuid:organization_uid>', PrivateOrganizationDestroyView.as_view(), name='my-organizations'),
    ]
