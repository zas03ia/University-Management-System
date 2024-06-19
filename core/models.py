from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from custom_utilities.base_model import *
from .managers import *
# Create your models here.

class User(AbstractUser):
    username = models.CharField(_("username"), max_length=150, unique=True, default='anonymous')
    email = models.EmailField(_("email address"), unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['username']

    objects = CustomUserManager()

    def __str__(self):
        return self.username 
    
class Organization(BaseModel):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    branch = models.PositiveSmallIntegerField(default=1)
    subdomain = models.CharField(max_length=50, unique=True, default='www')
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'description', 'branch'], name='organization_pk')
        ]
    def save(self, *args, **kwargs):
        self.subdomain = self.subdomain.lower() 
        super().save(*args, **kwargs)
    
    
class OrganizationUser(BaseModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.BooleanField(default=True)
    role = models.CharField(max_length=300)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['role', 'user', 'organization'], name='organization_user_pk1')
        ]
    
    