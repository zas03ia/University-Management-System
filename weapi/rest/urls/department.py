from django.urls import path
from weapi.rest.views.department import *

urlpatterns = [
    path('/organization_detail_<uuid:organization_uid>', PrivateOrganizationDetailView.as_view(), name='organization-detail'),
    path('/departments', PublicDepartmentListView.as_view(), name='departments'),
    path('/departments/<uuid:department_uid>', PrivateDepartmentDetailView.as_view(), name='department-detail'),
    path('/departments/<uuid:department_uid>/courses', PublicCourseListView.as_view(), name='department-courses'),
    path('/departments/<uuid:department_uid>/courses/<uuid:course_uid>', PrivateCourseDetailView.as_view(), name='department-course-detail'),
    # path('/allcourses', PublicAllCourseListView.as_view(), name='organization-courses'),
    path('/departments/<uuid:department_uid>/courses/<uuid:course_uid>/prerequisites', PublicPrerequisiteListView.as_view(), name='course-prerequisites'),
    path('/departments/<uuid:department_uid>/courses/<uuid:course_uid>/prerequisites/<uuid:prerequisite_uid>', PrivatePrerequisiteDetailView.as_view(), name='course-prerequisite-detail'),
    path('/departments/<uuid:department_uid>/degree_plan', PublicDegreePlanListView.as_view(), name='department-degree-plan'),
    path('/departments/<uuid:department_uid>/degree_plan/<uuid:semester_uid>', PrivateDegreePlanDetailView.as_view(), name='department-degree-plan-detail'),
    path('/organization_users', PrivateOrganizationUserListView.as_view(), name='organization-users'),
    path('/organization_users/<uuid:user_uid>', PrivateOrganizationUserDetailView.as_view(), name='organization-user-detail'),
]
