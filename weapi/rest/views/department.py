from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from department.models import *
from rest_framework.permissions import IsAuthenticated
from weapi.rest.serializers.department import *
from django.shortcuts import get_object_or_404
from custom_utilities.custom_permission import IsAdmin, IsStudent, IsFaculty, IsMember, IsAdminOrFaculty


class PrivateOrganizationDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = PrivateOrganizationDetailSerializer
    def get_object(self):
        organization_uid = self.kwargs.get('organization_uid')
        organization = get_object_or_404(Organization, uid=organization_uid)
        return organization
    permission_classes = [IsAdmin]
 

class PublicDepartmentListView(ListCreateAPIView):
    serializer_class = PublicDepartmentListSerializer
    def get_permissions(self):
        if self.request.method == 'POST': 
            return [IsAdmin()] 
        return [IsAuthenticated()] 
    def get_queryset(self):
        organization = get_organization(self.request)
        queryset = Department.objects.filter(organization=organization)
        return queryset


class PrivateDepartmentDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = PrivateDepartmentDetailSerializer
    permission_classes = [IsAdmin]
    def get_object(self):
        department_uid = self.kwargs.get('department_uid')
        department = get_object_or_404(Department, uid=department_uid)
        return department
    
class PublicCourseListView(ListCreateAPIView):
    serializer_class = PublicCourseListSerializer
    def get_permissions(self):
        if self.request.method == 'POST': 
            return [IsAdminOrFaculty()] 
        return [IsAuthenticated()] 
    def get_queryset(self):
        department_uid = self.kwargs.get('department_uid')
        organization = get_organization(self.request)
        queryset = Course.objects.filter(organization=organization, department__uid=department_uid)
        return queryset
   
class PrivateCourseDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = PrivateCourseDetailSerializer
    permission_classes = [IsAdminOrFaculty]
    def get_object(self):
        course_uid = self.kwargs.get('course_uid')
        organization = get_organization(self.request)
        course = get_object_or_404(Course, uid=course_uid, organization=organization)
        return course
    
# class PublicAllCourseListView(ListCreateAPIView):
#     serializer_class = PublicCourseListSerializer
#     def get_queryset(self):
#         organization_uid = self.kwargs.get('organization_uid')
#         queryset = Course.objects.filter(organization__uid=organization_uid)
#         return queryset
    
class PublicPrerequisiteListView(ListCreateAPIView):
    serializer_class = PublicPrerequisiteListSerializer
    def get_permissions(self):
        if self.request.method == 'POST': 
            return [IsAdminOrFaculty()] 
        return [IsAuthenticated()]
    def get_queryset(self):
        organization, course_uid = get_organization(self.request), self.kwargs.get('course_uid')
        queryset = Prerequisite.objects.filter(organization=organization, course__uid=course_uid)
        return queryset


class PrivatePrerequisiteDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = PrivatePrerequisiteDetailSerializer
    permission_classes = [IsAdminOrFaculty]
    def get_object(self):
        prerequisite_uid = self.kwargs.get('prerequisite_uid')
        organization = get_organization(self.request)
        prerequisite = get_object_or_404(Prerequisite, uid=prerequisite_uid, organization=organization)
        return prerequisite
    def get_queryset(self):
        organization, course_uid = get_organization(self.request), self.kwargs.get('course_uid')
        queryset = Prerequisite.objects.filter(organization=organization, course__uid=course_uid)
        return queryset
class PublicDegreePlanListView(ListCreateAPIView):
    serializer_class = PublicDegreePlanListSerializer
    def get_permissions(self):
        if self.request.method == 'POST': 
            return [IsAdminOrFaculty()] 
        return [IsMember()]
    def get_queryset(self):
        department_uid = self.kwargs.get('department_uid')
        organization = get_organization(self.request)
        queryset = Semester.objects.filter(organization=organization, department__uid=department_uid).order_by('semester_number')
        return queryset


class PrivateDegreePlanDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = PrivateDegreePlanDetailSerializer
    permission_classes = [IsAdminOrFaculty]
    def get_object(self):
        semester_uid, department_uid = self.kwargs.get('semester_uid'), self.kwargs.get('department_uid')
        organization = get_organization(self.request)
        plan = get_object_or_404(Semester, uid=semester_uid, organization=organization, department__uid=department_uid)
        return plan
    def get_queryset(self):
        department_uid = self.kwargs.get('department_uid')
        organization = get_organization(self.request)
        queryset = Semester.objects.filter(organization=organization, department__uid=department_uid).order_by('semester_number')
        return queryset
    
class PrivateOrganizationUserListView(ListCreateAPIView):
    serializer_class = PrivateOrganizationUserListSerializer
    def get_permissions(self):
        if self.request.method == 'POST': 
            return [IsAdmin()] 
        return [IsMember()] 
    def get_queryset(self):
        organization = get_organization(self.request)
        queryset = OrganizationUser.objects.filter(organization=organization)
        return queryset
    
class PrivateOrganizationUserDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = PrivateOrganizationUserDetailSerializer
    def get_object(self):
        organization = get_organization(self.request)
        user_uid = self.kwargs.get('user_uid')
        user = get_object_or_404(OrganizationUser, uid=user_uid, organization=organization)
        return user
    permission_classes = [IsAdmin]