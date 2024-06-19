from django.db import models
from custom_utilities.base_model import BaseModel
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from core.models import *

# Create your models here.

class Department(BaseModel):
    name = models.CharField(max_length=200)
    description = models.TextField()
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'description', 'organization'], name='department_pk')
        ]
class Course(BaseModel):
    course_code = models.TextField(
        max_length=6,
        validators=[
            RegexValidator(
                regex='^[A-Z]{3}[0-9]{3}$',
                message='Course code must be in the format AAA999 (3 letters followed by 3 digits)',
            )
        ]
         
    )
    name = models.CharField(max_length=300)
    description = models.TextField()
    status = models.BooleanField(default=True)
    credit = models.PositiveIntegerField(default=3)
    since = models.DateField()
    till =  models.DateField(null=True, blank=True, default=None)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['course_code','name', 'description', 'organization'], name='course_pk')
        ]
    
    def clean(self):
        if self.till!=None and self.since >= self.till:
            raise ValidationError("Time Entry Error")

    def save(self, *args, **kwargs):
        self.clean()  # Validate before saving
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.course_code
    
class Semester(BaseModel):
    semester_number = models.PositiveSmallIntegerField(default=None)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    # class Meta:
    #     constraints = [
    #         models.UniqueConstraint(fields=['course', 'department', 'organization'], name='semester_pk')
    #     ]
    

class Prerequisite(BaseModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE,  related_name='course')
    prerequisite = models.ForeignKey(Course, on_delete=models.CASCADE,  related_name='prerequisite')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['course', 'prerequisite', 'organization'], name='prerequisite_pk1')
        ]
        
    def clean(self):
        if self.course_id == self.prerequisite_id:
            raise ValidationError("Course and prerequisite cannot be the same.")

    def save(self, *args, **kwargs):
        self.clean() 
        super().save(*args, **kwargs)
