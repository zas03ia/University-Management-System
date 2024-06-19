from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView, RetrieveDestroyAPIView
from rest_framework import generics, mixins
from session.models import *
from rest_framework.permissions import IsAuthenticated
from weapi.rest.serializers.advising import *
from django.shortcuts import get_object_or_404
from custom_utilities.custom_permission import *
from custom_utilities.subdomain import *

class PrivateScheduleListView(ListCreateAPIView):
    serializer_class = PublicScheduleListSerializer
    permission_classes = [IsAdminOrFaculty]
    def get_queryset(self):
        organization = get_organization(self.request)
        queryset = Schedule.objects.filter(organization=organization)
        return queryset

class PrivateScheduleDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = PrivateScheduleDetailSerializer
    permission_classes = [IsAdminOrFaculty]
    def get_object(self):
        schedule_uid = self.kwargs.get('schedule_uid')
        schedule = get_object_or_404(Schedule, uid=schedule_uid)
        return schedule
    
class PrivateSectionListView(ListCreateAPIView):
    serializer_class = SectionSerializer
    def get_permissions(self):
        if self.request.method == 'POST': 
            return [IsAdmin()] 
        return [IsAuthenticated()] 
    def get_queryset(self):
        organization = get_organization(self.request)
        queryset = Section.objects.filter(organization=organization)
        return queryset
    
class PrivateSectionDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = SectionDetailSerializer
    permission_classes = [IsAdmin]
    def get_queryset(self):
        # Fetching necessary parameters from URL
        department_uid = self.kwargs.get('department_uid')
        course_uid = self.kwargs.get('course_uid')

        # Filter sections based on the department and course from the URL
        return Section.objects.filter(
            course__department__uid=department_uid,
            course__uid=course_uid
        )
    def get_object(self):
        section_uid = self.kwargs.get('section_uid')
        section = get_object_or_404(Section, uid=section_uid)
        return section
    
    
class PrivateSessionListView(ListCreateAPIView):
    serializer_class = SessionSerializer
    def get_permissions(self):
        if self.request.method == 'POST': 
            return [IsAdmin()] 
        return [IsAuthenticated()] 
    def get_queryset(self):
        organization=get_organization(self.request)
        queryset = Session.objects.filter(organization=organization)
        return queryset
    
class PrivateSessionDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = SessionSerializer
    permission_classes = [IsAdminOrFaculty]
    def get_object(self):
        session_uid = self.kwargs.get('session_uid')
        section = get_object_or_404(Session, uid=session_uid)
        return section
    
class PrivateAdminAdvisingListView(ListCreateAPIView):
    serializer_class = StudentSessionSerializer
    permission_classes = [IsAdminOrFaculty]
    def get_queryset(self):
        organization = get_organization(self.request)
        queryset = StudentSession.objects.filter(organization=organization)
        return queryset
    
    
class PrivateAdminAdvisingDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = StudentSessionSerializer
    permission_classes = [IsAdminOrFaculty]
    def get_object(self):
        student_session_uid = self.kwargs.get('student_session_uid')
        section = get_object_or_404(StudentSession, uid=student_session_uid)
        return section
    
class PrivateMyAdvisedCourseListView(ListCreateAPIView):
    serializer_class = MyAdvisedCourseSerializer
    def get_permissions(self):
        if self.request.method == 'POST': 
            return [StudentAdvising()] 
        return [IsStudent()]
    def get_queryset(self):
        organization = get_organization(self.request)
        queryset = StudentSession.objects.filter(organization=organization, student=self.request.user, session__term_start__lte=date.today(), session__term_end__gte=date.today())
        return queryset if queryset else ["No courses for current session"]
    
class PrivateMyAdvisedCourseDetailView(RetrieveDestroyAPIView):
    serializer_class = MyAdvisedCourseSerializer
    permission_classes = [StudentAdvising] 
    def get_object(self):
        advised_uid = self.kwargs.get('advised_uid')
        section = get_object_or_404(StudentSession, uid=advised_uid, organization=get_organization(self.request))
        return section
    
class PrivateFacultyScehduleListView(ListAPIView):
    serializer_class = SectionFacultySerializer
    permission_classes = [IsFaculty] 
    def get_queryset(self):
        organization = get_organization(self.request)
        queryset = Section.objects.filter(organization=organization, faculty=self.request.user)
        return queryset
    
class PrivateStudentGradesheetListView(ListAPIView):
    serializer_class = MyGradesheetSerializer
    permission_classes = [IsStudent] 
    def get_queryset(self):
        organization = get_organization(self.request)
        queryset = StudentSession.objects.filter(organization=organization, student= self.request.user)
        return queryset