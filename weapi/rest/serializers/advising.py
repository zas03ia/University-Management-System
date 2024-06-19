from rest_framework import serializers
from session.models import *
from django.db.models import Subquery
from custom_utilities.helper import *
from datetime import date
from django.http import JsonResponse
from custom_utilities.subdomain import *
from advising.models import *

class PublicScheduleListSerializer(serializers.ModelSerializer):
    schedule_uid = serializers.CharField(source='uid', read_only=True)
    class Meta:
        model = Schedule
        fields = ['schedule_uid', 'type', 'sunday_start_time', 'sunday_end_time', 'monday_start_time',
                'monday_end_time', 'tuesday_start_time', 'tuesday_end_time', 'wednesday_start_time',
                'wednesday_end_time', 'thursday_start_time', 'thursday_end_time', 'friday_start_time',
                'friday_end_time', 'saturday_start_time', 'saturday_end_time']
    
    def create(self, validated_data):
        organization = get_organization(self.context.get('request'))
        try:
            existing_schedule = Schedule.objects.get(organization=organization, **validated_data)
            raise serializers.ValidationError("Schedule with the same attributes already exists")
        except Schedule.DoesNotExist:
            pass

        schedule = Schedule.objects.create(organization=organization, **validated_data)
        return schedule
        
    def validate(self, data):
        days = [
            'sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'
        ]
        
        if not any(data.get(f'{day}_start_time') or data.get(f'{day}_end_time') for day in days):
            raise serializers.ValidationError("At least one weekday must be included in the schedule.")
        
        for day in days:
            start_time_field = f'{day}_start_time'
            end_time_field = f'{day}_end_time'
            start_time = data.get(start_time_field)
            end_time = data.get(end_time_field)
            
            if (start_time and not end_time) or (end_time and not start_time):
                raise serializers.ValidationError(
                    f"Both start and end times must be provided for {day} if it is included in the schedule."
                )
        
        return data
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        always_include = {
            'schedule_uid': representation.get('schedule_uid'),
            'type': representation.get('type')
        }
        filtered_representation = {key: value for key, value in representation.items() if value is not None}
        filtered_representation.update(always_include)
        return filtered_representation
        
class PrivateScheduleDetailSerializer(serializers.ModelSerializer):
    schedule_uid = serializers.CharField(source='uid', read_only=True)
    class Meta:
        model = Schedule
        exclude = ['id', 'uid', 'organization']
        
    def validate(self, data):
        days = [
            'sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'
        ]
        
        if not any(data.get(f'{day}_start_time') or data.get(f'{day}_end_time') for day in days):
            raise serializers.ValidationError("At least one weekday must be included in the schedule.")
        
        for day in days:
            start_time_field = f'{day}_start_time'
            end_time_field = f'{day}_end_time'
            start_time = data.get(start_time_field)
            end_time = data.get(end_time_field)
            
            if (start_time and not end_time) or (end_time and not start_time):
                raise serializers.ValidationError(
                    f"Both start and end times must be provided for {day} if it is included in the schedule."
                )
        
        return data
    
    def update(self, instance, validated_data):
        if Schedule.objects.filter(**validated_data).exclude(id=instance.id).exists():
            raise serializers.ValidationError("Schedule with the same attributes already exists")
        try:
            for field in validated_data:
                setattr(instance, field, validated_data.get(field))
        except:
            raise serializers.ValidationError('Schedule update failed')
        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        always_include = {
            'schedule_uid': representation.get('schedule_uid'),
            'type': representation.get('type'),
            'created_at': representation.get('created_at'),
            'updated_at': representation.get('updated_at')
        }
        filtered_representation = {key: value for key, value in representation.items() if value is not None}
        filtered_representation.update(always_include)
        return filtered_representation

class SectionSerializer(serializers.ModelSerializer):
    section_uid = serializers.CharField(source='uid', read_only=True)
    schedule_choices = serializers.ChoiceField(choices=[], write_only=True)
    instructor_choices = serializers.ChoiceField(choices=[], write_only=True)
    schedule = serializers.CharField(read_only=True)
    course_instructor = serializers.CharField(source='faculty', read_only=True)
    
    class Meta:
        model = Section
        fields = ['section_uid', 'section', 'course_instructor', 'instructor_choices', 'schedule', 'schedule_choices']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        view = self.context.get('view')
        self.organization = get_organization(self.context.get('request'))
        course_uid = view.kwargs.get('course_uid')
        self.course = Course.objects.get(uid=course_uid, organization=self.organization)
        if self.organization:
            schedules = Schedule.objects.filter(organization=self.organization)
            faculties = User.objects.filter(id__in=Subquery(OrganizationUser.objects.filter(organization=self.organization, role='Faculty').values('user'))) 
            self.fields['schedule_choices'].choices = [schedule for schedule in schedules]
            self.fields['instructor_choices'].choices = [faculty for faculty in faculties]
    
    def validate_course(self, value):
        if value:
            return value
        raise ValidationError('Invalid Organization')
   
    def create(self, validated_data):
        section = validated_data.pop('section')
        if Section.objects.filter(organization=self.organization, course=self.course, section=section).exists():
            raise serializers.ValidationError("Section {section} already exists for this course.")
        schedule_uid = validated_data.get('schedule_choices').uid
        self.schedule = Schedule.objects.get(organization=self.organization, uid = schedule_uid)
        self.faculty = validated_data.pop('instructor_choices')
        section = Section.objects.create(organization=self.organization, schedule=self.schedule,
                                         course=self.course, faculty=self.faculty, section=section)
        return section
        
    def validate(self, data):
        schedule_uid = data.get('schedule_choices').uid
        self.schedule = Schedule.objects.get(organization=self.organization, uid = schedule_uid)
        faculty_name = str(data.get('instructor_choices')).strip()
        self.faculty = User.objects.get(username=faculty_name)
        days = [
            'sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'
        ]
        schedules = Schedule.objects.filter(id__in=Subquery(Section.objects.filter(faculty=self.faculty.id).values('schedule')))
        for schedule in schedules:
            for day in days:
                start1 = getattr(self.schedule,f'{day}_start_time')
                start2 = getattr(schedule, f'{day}_start_time')
                end1 = getattr(self.schedule, f'{day}_end_time')
                end2 = getattr(schedule,f'{day}_end_time')
                print('times', start1, end1, start2, end2)
                if time_overlap(start1, end1, start2, end2):
                    raise serializers.ValidationError(f"For faculty: {self.faculty}, the new schedule conflicts with an existing schedule.")
        return data
    
        
class SectionDetailSerializer(serializers.ModelSerializer):
    section_uid = serializers.CharField(source='uid', read_only=True)
    schedule_choices = serializers.ChoiceField(choices=[], write_only=True)
    instructor_choices = serializers.ChoiceField(choices=[], write_only=True)
    schedule = serializers.CharField(read_only=True)
    course_instructor = serializers.CharField(source='faculty', read_only=True)
    
    class Meta:
        model = Section
        fields = ['section_uid', 'section', 'course_instructor', 'instructor_choices', 'schedule', 'schedule_choices']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        view = self.context.get('view')
        self.organization = get_organization(self.context.get('request'))
        course_uid = view.kwargs.get('course_uid')
        self.course = Course.objects.get(uid=course_uid, organization=self.organization)
        if self.organization:
            schedules = Schedule.objects.filter(organization=self.organization)
            faculties = User.objects.filter(id__in=Subquery(OrganizationUser.objects.filter(organization=self.organization, role='Faculty').values('user'))) 
            self.fields['schedule_choices'].choices = [schedule for schedule in schedules]
            self.fields['instructor_choices'].choices = [faculty for faculty in faculties]
    
    def validate_course(self, value):
        if value:
            return value
        raise ValidationError('Invalid Organization')
   
    
    def validate(self, data):
        schedule_uid = data.get('schedule_choices').uid
        self.schedule = Schedule.objects.get(organization=self.organization, uid = schedule_uid)
        faculty_name = str(data.get('instructor_choices')).strip()
        self.faculty = User.objects.get(username=faculty_name)
        days = [
            'sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'
        ]
        schedules = Schedule.objects.filter(id__in=Subquery(Section.objects.filter(faculty=self.faculty.id).values('schedule')))
        for schedule in schedules:
            for day in days:
                start1 = getattr(self.schedule,f'{day}_start_time')
                start2 = getattr(schedule, f'{day}_start_time')
                end1 = getattr(self.schedule, f'{day}_end_time')
                end2 = getattr(schedule,f'{day}_end_time')
                print('times', start1, end1, start2, end2)
                if time_overlap(start1, end1, start2, end2):
                    raise serializers.ValidationError(f"For faculty: {self.faculty}, the new schedule conflicts with an existing schedule.")
        return data
    
    def update(self, instance, validated_data):
        section = validated_data.pop('section')
        if Section.objects.filter(organization=instance.organization, course=instance.course, section=section).exclude(id=instance.id).exists():
            raise serializers.ValidationError(f"Section {section} already exists for this course.")
        try:
            schedule_uid = validated_data.get('schedule_choices').uid
            self.schedule = Schedule.objects.get(organization=self.organization, uid = schedule_uid)
            self.faculty = validated_data.pop('instructor_choices')
            instance.schedule = self.schedule
            instance.faculty = self.faculty
            instance.section = section
            instance.save()
            return instance
        except:
            raise serializers.ValidationError('Section update failed')

class SessionSerializer(serializers.ModelSerializer):
    session_uid = serializers.CharField(source='uid', read_only=True)
    
    class Meta:
        model = Session
        fields = ['session_uid', 'year', 'term', 'term_start', 'term_end', 'advising_start', 'advising_end']

    def validate(self, data):
        advising_start = data.get('advising_start')
        advising_end  = data.get('advising_end')
        year = data.get('year')
        if advising_start > advising_end:
            raise serializers.ValidationError("Advising start time must be before advising end time.")
        if year < advising_start.year:
            raise serializers.ValidationError("Please provide a valid year")
        return data
    
    def create(self, validated_data):
        organization = get_organization(self.context.get('request'))
        if Session.objects.filter(organization=organization, **validated_data).exists():
            raise serializers.ValidationError("Session {existing_session} already exists.")
        session = Session.objects.create(organization=organization, **validated_data)
        return session
    
    def update(self, instance, validated_data):
        if Session.objects.filter(organization=instance.organization, **validated_data).exclude(id=instance.id).exists():
            raise serializers.ValidationError("Session {existing_session} already exists for this course.")
        try:
            for field in validated_data:
                setattr(instance, field, validated_data.get(field))
        except:
            raise serializers.ValidationError('Session update failed')
        instance.save()
        return instance
    
class StudentSessionSerializer(serializers.ModelSerializer):
    studentsession_uid = serializers.CharField(source='uid', read_only=True)
    session_taken = serializers.CharField(source='session',read_only=True)
    course_details = serializers.ChoiceField(choices=[], write_only=True)
    session = serializers.ChoiceField(choices=[], write_only=True)
    student_to_take = serializers.ChoiceField(choices=[], write_only=True)
    course_info = serializers.SerializerMethodField(read_only=True)
    student = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = StudentSession
        fields = ['studentsession_uid', 'session','session_taken', 'course_details', 'student', 'course_info', 'student_to_take']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        organization = get_organization(self.context.get('request'))
        sections = Section.objects.filter(organization=organization)
        sessions = Session.objects.filter(organization=organization, term_end__gte=date.today())
        organization_users = OrganizationUser.objects.filter(organization=organization, role='Student')
        students = User.objects.filter(id__in=Subquery(OrganizationUser.objects.filter(organization=organization, role='Student').values('user')))
        self.fields['course_details'].choices = [f'{str(section)} | section_uid: {section.uid}' for section in sections]
        self.fields['session'].choices = [f'{str(session)} | uid: {session.uid}' for session in sessions]
        self.fields['student_to_take'].choices = [f'{str(student)} | uid: {org.uid}' for student,org in zip(students, organization_users)]
        
    def get_course_info(self, obj):
        return str(obj.section)
    def get_student(self, obj):
        return str(obj.student)
    def create(self, validated_data):
        request = self.context.get('request')
        organization = get_organization(request)
        org_user = OrganizationUser.objects.values('user').get(uid=validated_data.get('student_to_take').split('|')[-1].split(':')[-1].strip())
        student = User.objects.get(id=org_user['user'])
        section = Section.objects.get(uid=validated_data.pop('course_details').split('|')[-1].split(':')[-1].strip())
        session = Session.objects.get(uid=validated_data.get('session').split('|')[-1].split(':')[-1].strip())
        try:
            x = StudentSession.objects.get(organization=organization, student=student, section=section, session=session)
            raise serializers.ValidationError("{student} already enrolled in course")
        except:
            pass
        session = StudentSession.objects.create(organization=organization,section=section, student=student, session=session)
        return session
    def validate(self, data):
        section_uid = data.get('course_details').split('|')[-1].split(':')[-1].strip()
        section = Section.objects.get(uid=section_uid)
        
        self.schedules=Schedule.objects.filter(id__in=
                                            Subquery(Section.objects.filter(id__in=
                                            Subquery(StudentSession.objects.filter(student=self.context['request'].user).values('section')
                                                     )
                                                                            ).values('schedule')
                                                    )
                                            )
        days = [
            'sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'
        ]
        self.new_schedule = Schedule.objects.get(id=section.schedule.id)
        for schedule in self.schedules:
            for day in days:
                start1 = getattr(self.new_schedule,f'{day}_start_time')
                start2 = getattr(schedule, f'{day}_start_time')
                end1 = getattr(self.new_schedule, f'{day}_end_time')
                end2 = getattr(schedule,f'{day}_end_time')
                if time_overlap(start1, end1, start2, end2):
                    raise serializers.ValidationError(f"{section} conflicts with existing schedule.")
        return data
    
    def update(self, instance, validated_data):
        try:
            org_user = OrganizationUser.objects.values('user').get(uid=validated_data.get('student_to_take').split('|')[-1].split(':')[-1].strip())
            student = User.objects.get(id=org_user['user'])
            section = Section.objects.get(uid=validated_data.pop('course_details').split('|')[-1].split(':')[-1].strip())
            session = Session.objects.get(uid=validated_data.get('session').split('|')[-1].split(':')[-1].strip())       
        except:
            raise serializers.ValidationError('Invalid Information')
        try:
            x = StudentSession.objects.get(organization=instance.organization, section=section, student=student, session=session).exclude(id=instance.id)
            raise serializers.ValidationError(f'Course already taken by {student}')
        except:
            pass
        try:
            instance.student= student
            instance.section = section
            instance.session = session
            instance.save()
        except:
            raise serializers.ValidationError('Update failed')
        return instance
    
class MyAdvisedCourseSerializer(serializers.ModelSerializer):
    studentsession_uid = serializers.CharField(source='uid', read_only=True)
    session = serializers.CharField(read_only=True)
    course_details = serializers.ChoiceField(choices=[], write_only=True)
    course_info = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = StudentSession
        fields = ['studentsession_uid', 'session', 'course_details','course_info']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.organization = get_organization(self.context.get('request'))
        sections = Section.objects.filter(organization=self.organization.id)
        self.fields['course_details'].choices = [f'{str(section)} | section_uid: {section.uid}' for section in sections]

    def get_course_info(self, obj):
        return str(obj.section)
    
    def create(self, validated_data):
        request = self.context.get('request')
        organization = get_organization(request)
        student = request.user
        section = Section.objects.get(uid=str(validated_data.pop('course_details')).split('|')[-1].split(':')[-1].strip())
        session = Session.objects.filter(organization=organization, advising_start__lte=date.today(), advising_end__gte=date.today()).first()
        if StudentSession.objects.filter(organization=organization, student=student, session=session).exists():
            raise serializers.ValidationError("Course already taken.")
        session = Session.objects.create(organization=organization, student=student, section=section, session=session)
        return session
    def validate(self, data):
        section_uid = data.get('course_details').split('|')[-1].split(':')[-1].strip()
        section = Section.objects.get(uid=section_uid)
        self.schedules=Schedule.objects.filter(id__in=
                                            Subquery(Section.objects.filter(id__in=
                                            Subquery(StudentSession.objects.filter(student=self.context['request'].user).values('section')
                                                     )
                                                                            ).values('schedule')
                                                    )
                                            )
        days = [
            'sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'
        ]
        self.new_schedule = Schedule.objects.get(id=section.schedule.id)
        for schedule in self.schedules:
            for day in days:
                start1 = getattr(self.new_schedule,f'{day}_start_time')
                start2 = getattr(schedule, f'{day}_start_time')
                end1 = getattr(self.new_schedule, f'{day}_end_time')
                end2 = getattr(schedule,f'{day}_end_time')
                if time_overlap(start1, end1, start2, end2):
                    raise serializers.ValidationError(f"{str(section).split('|')[0]} | {str(section).split('|')[1]} conflicts with existing schedule.")
        return data
    
class MyGradesheetSerializer(serializers.ModelSerializer):
    course = serializers.CharField(source='session',read_only=True)
    class Meta:
        model = StudentSession
        fields = ['course','gpa']
        
class SectionFacultySerializer(serializers.ModelSerializer):
    section = serializers.SerializerMethodField()
    course = serializers.SerializerMethodField()
    schedule = serializers.SerializerMethodField()
    class Meta:
        model = Section
        fields = ['course','section','schedule']
        
    def get_section(self, obj):
        return str(obj.section)
    def get_course(self, obj):
        return str(obj.course)
        
    def get_schedule(self, obj):
        return str(obj.schedule)