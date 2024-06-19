from django.db import models
from core.models import *
from django.core.validators import MinValueValidator, MaxValueValidator
from department.models import *
import datetime
from session.choices import TERMS_CHOICES
# Create your models here.

class Schedule(BaseModel):
    sunday_start_time = models.TimeField(null=True, blank=True)
    sunday_end_time = models.TimeField(null=True, blank=True)
    monday_start_time = models.TimeField(null=True, blank=True)
    monday_end_time = models.TimeField(null=True, blank=True)
    tuesday_start_time = models.TimeField(null=True, blank=True)
    tuesday_end_time = models.TimeField(null=True, blank=True)
    wednesday_start_time = models.TimeField(null=True, blank=True)
    wednesday_end_time = models.TimeField(null=True, blank=True)
    thursday_start_time = models.TimeField(null=True, blank=True)
    thursday_end_time = models.TimeField(null=True, blank=True)
    friday_start_time = models.TimeField(null=True, blank=True)
    friday_end_time = models.TimeField(null=True, blank=True)
    saturday_start_time = models.TimeField(null=True, blank=True)
    saturday_end_time = models.TimeField(null=True, blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    type = models.CharField(max_length=200)
    def __str__(self):
        days = [
            ('Sunday', self.sunday_start_time, self.sunday_end_time),
            ('Monday', self.monday_start_time, self.monday_end_time),
            ('Tuesday', self.tuesday_start_time, self.tuesday_end_time),
            ('Wednesday', self.wednesday_start_time, self.wednesday_end_time),
            ('Thursday', self.thursday_start_time, self.thursday_end_time),
            ('Friday', self.friday_start_time, self.friday_end_time),
            ('Saturday', self.saturday_start_time, self.saturday_end_time),
        ]

        non_null_days = [
            f"{day}: {start} - {end}" for day, start, end in days if start and end
        ]

        days_str = "; ".join(non_null_days)

        return f"Type: {self.type} | Schedule: {days_str} | Schedule_uid: {self.uid}"
    
class Section(BaseModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    section = models.PositiveIntegerField(null=False)
    faculty = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, null=True, blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['course', 'section','organization'], name='section_pk1'),
            models.UniqueConstraint(fields=['faculty', 'schedule', 'organization'], name='section_pk2')
        ]
    def save(self, *args, **kwargs):
        self.clean()  # Validate before saving
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Course: {self.course} | Section: {self.section} | Faculty: {self.faculty} | Schedule: {self.schedule}"
    
    
class Session(BaseModel):
    year = models.IntegerField(
        validators=[MinValueValidator(1900), MaxValueValidator(2100)]
        )
    
    term = models.CharField(choices=TERMS_CHOICES)
    advising_start = models.DateField()
    advising_end = models.DateField()
    term_start = models.DateField(null=True, blank=True)
    term_end = models.DateField(null=True, blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['year','term','organization'], name='session_pk1')
        ]
    
    def clean(self):
        if self.advising_start >= self.advising_end or self.advising_start < datetime.date.today():
            raise ValidationError("Invalid Time Entry.")

    def save(self, *args, **kwargs):
        self.clean()  # Validate before saving
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.term} {self.year}"
    