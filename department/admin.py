from django.contrib import admin
from .models import Course, Department, Semester, Prerequisite

# Register your models here.
admin.site.register(Course)
admin.site.register(Department)
admin.site.register(Semester)
admin.site.register(Prerequisite)