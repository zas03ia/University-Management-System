from django.urls import path
from weapi.rest.views.advising import *

urlpatterns = [
    path('/schedules', 
      PrivateScheduleListView.as_view(), name='schedules'),
    path('/schedules/<uuid:schedule_uid>', 
      PrivateScheduleDetailView.as_view(), name='schedule-detail'),
    path('/departments/<uuid:department_uid>/courses/<uuid:course_uid>/sections', 
        PrivateSectionListView.as_view(), name='sections'),
    path('/departments/<uuid:department_uid>/courses/<uuid:course_uid>/sections/<uuid:section_uid>', 
        PrivateSectionDetailView.as_view(), name='section-detail'),
    path('/sessions', 
        PrivateSessionListView.as_view(), name='sessions'),
    path('/sessions/<uuid:session_uid>', 
        PrivateSessionDetailView.as_view(), name='session-detail'),
    path('/admin_advising_panel', 
        PrivateAdminAdvisingListView.as_view(), name='admin-access-advising-panel'),
    path('/admin_advising_panel/<uuid:student_session_uid>', 
        PrivateAdminAdvisingDetailView.as_view(), name='admin-access-session-detail'),
    path('/student_advising_panel', 
        PrivateMyAdvisedCourseListView.as_view(), name='student-access-advising-panel'),
    path('/student_advising_panel/<uuid:advised_uid>', 
        PrivateMyAdvisedCourseDetailView.as_view(), name='student-access-advising-panel'),
    path('/faculty_roster', 
        PrivateFacultyScehduleListView.as_view(), name='faculty-roster'),
    #  path('/student_gradesheet', 
    #     PrivateStudentGradesheetListView.as_view(), name='student-gradesheet'),

]
