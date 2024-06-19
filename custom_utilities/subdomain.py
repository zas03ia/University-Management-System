from core.models import Organization
from rest_framework.exceptions import ValidationError

def get_organization(request):
    domain = request.headers.get('X-DOMAIN', None)
    if domain:
        organization = Organization.objects.get(subdomain=domain.title())
        return organization
    else:
        raise ValidationError('Invalid organization')
    
