from rest_framework import serializers
from department.models import *
from custom_utilities.subdomain import *

class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']

class PrivateOrganizationDetailSerializer(serializers.ModelSerializer):
    organization_uid = serializers.CharField(source='uid', read_only=True)
    class Meta:
        model = Organization
        fields = ['organization_uid', 'name', 'description', 'branch', 'subdomain', 'created_at', 'updated_at'] 

class PrivateOrganizationUserListSerializer(serializers.ModelSerializer):
    user = UserListSerializer(read_only=True)
    username = serializers.CharField(write_only=True)
    organization_user_uid = serializers.CharField(source='uid', read_only=True)
    active_status = serializers.CharField(source='status')
    class Meta:
        model = OrganizationUser
        fields = ['organization_user_uid','user', 'username', 'role', 'active_status']
    def create(self, validated_data):
        username = validated_data.pop('username').strip()
        try:
            user_instance = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist")
        organization = get_organization(self.context.get('request'))
        if OrganizationUser.objects.filter(user=user_instance, organization=organization, **validated_data).exists():
            raise serializers.ValidationError("User already exists with this role in the organization")
        try:
            organization_user = OrganizationUser.objects.create(user=user_instance, organization=organization, **validated_data)
            return organization_user
        except:
            raise serializers.ValidationError("Organization user already exists with this")
        
         
class PrivateOrganizationUserDetailSerializer(serializers.ModelSerializer):
    user = UserListSerializer(read_only=True)
    organization_user_uid = serializers.CharField(source='uid', read_only=True)
    active_status = serializers.CharField(source='status')
    class Meta:
        model = OrganizationUser
        fields = ['organization_user_uid', 'user', 'role', 'active_status', 'created_at', 'updated_at']

class PublicDepartmentListSerializer(serializers.ModelSerializer):
    department_uid = serializers.CharField(source='uid', read_only=True)
    class Meta:
        model = Department
        fields = ['department_uid', 'name', 'description']
    
    def validate_uid(self, value):
        if value:
            return value
        raise ValidationError('Please enter a valid uid')
        
    def create(self, validated_data):
        organization = get_organization(self.context.get('request'))
        if Department.objects.filter(organization=organization, **validated_data).exists():
            raise serializers.ValidationError("Department already exists")
        try:
            department = Department.objects.create(organization=organization, **validated_data)
            return department
        except:
            raise serializers.ValidationError("Department creation failed")
        
class PrivateDepartmentDetailSerializer(serializers.ModelSerializer):
    department_uid = serializers.CharField(source='uid', read_only=True)
    class Meta:
        model = Department
        fields = ['department_uid', 'name', 'description', 'created_at', 'updated_at']
#########################################################################################
     
class PublicCourseListSerializer(serializers.ModelSerializer):
    course_uid = serializers.CharField(source='uid', read_only=True)
    course_active_since = serializers.CharField(source='since')
    course_active_till = serializers.CharField(source='till', required=False)
    active_status = serializers.CharField(source='status')
    class Meta:
        model = Course
        fields = ['course_uid', 'course_code', 'name', 'description', 'active_status', 'credit', 'course_active_since', 'course_active_till']
    def create(self, validated_data):
        department_uid = self.context['view'].kwargs.get('department_uid')
        if department_uid:
            try:
                organization = get_organization(self.context.get('request'))
                department = Department.objects.get(uid=department_uid, organization=organization)
                course = Course.objects.create(organization=organization, department=department, **validated_data)
                return course
            except Department.DoesNotExist:
                raise serializers.ValidationError("Course creation failed")
        else:
            raise serializers.ValidationError("Department not found in request")
        
class PrivateCourseDetailSerializer(serializers.ModelSerializer):
    course_uid = serializers.CharField(source='uid', read_only=True)
    class Meta:
        model = Course
        exclude = ['id', 'organization', 'department','uid']

        
class PublicPrerequisiteListSerializer(serializers.ModelSerializer):
    prerequisite = serializers.SerializerMethodField(read_only=True)
    prerequisite_uid = serializers.CharField(source='uid', read_only=True)
    prerequisite_course_code = serializers.CharField(write_only=True)
    class Meta:
        model = Prerequisite
        fields = ['prerequisite_uid', 'prerequisite_course_code', 'prerequisite']
        
    def create(self, validated_data):
        course_uid, prerequisite_course_code = self.context['view'].kwargs.get('course_uid'), validated_data.get('prerequisite_course_code').upper().strip()
        if course_uid:
            organization = get_organization(self.context.get('request'))
            try:
                course = Course.objects.get(uid=course_uid, organization=organization)
            except Course.DoesNotExist:
                raise serializers.ValidationError("Invalid course")
            try:
                prerequisite = Course.objects.get(course_code=prerequisite_course_code, organization=organization)
            except Course.DoesNotExist:
                raise serializers.ValidationError("Invalid prerequisite")
            if Prerequisite.objects.filter(organization=organization, course=course, prerequisite=prerequisite).exists():
                raise serializers.ValidationError(f"{prerequisite_course_code} is already added as a prerequisite")
            try:
                prerequisite_instance = Prerequisite.objects.create(organization=organization, course=course, prerequisite=prerequisite)
                return prerequisite_instance
            except:
                raise serializers.ValidationError("Could not add prerequisite for this course")
        else:
            raise serializers.ValidationError("Course UID not found in request")
    def get_prerequisite(self, obj):
        prerequisite = obj.prerequisite
        return {'course_code':prerequisite.course_code, 'course_uid':prerequisite.uid}
    
        
        
        
class PrivatePrerequisiteDetailSerializer(serializers.ModelSerializer):
    prerequisite = PrivateCourseDetailSerializer(read_only=True)
    prerequisite_course_code = serializers.CharField(write_only=True)
    class Meta:
        model = Prerequisite
        fields = ('uid', 'prerequisite', 'prerequisite_course_code')
        
    def update(self, instance, validated_data):
        # Update organization instance
        prerequisite_course_code = validated_data.get('prerequisite_course_code').upper().strip()
        if prerequisite_course_code:
            try:
                prerequisite = Course.objects.get(course_code=prerequisite_course_code, organization=instance.organization)
            except Course.DoesNotExist:
                raise serializers.ValidationError("Invalid prerequisite")
            if Prerequisite.objects.filter(course=instance.course, organization=instance.organization, prerequisite=prerequisite).exclude(id=instance.id).exists():
                raise serializers.ValidationError(f"{prerequisite_course_code} is already added as a prerequisite")
            try:
                instance.prerequisite = prerequisite
                instance.save()
                
            except:
                raise serializers.ValidationError("Could not update prerequisite for this course")
            return instance
 
class PublicDegreePlanCourseListSerializer(serializers.ModelSerializer):
    course_uid = serializers.CharField(source='uid', read_only=True)
    class Meta:
        model = Course
        fields = ['course_uid', 'course_code']
 
 
class PublicDegreePlanListSerializer(serializers.ModelSerializer):
    course = PublicDegreePlanCourseListSerializer(read_only=True)
    semester_instance_uid = serializers.CharField(source='uid', read_only=True)
    course_code = serializers.CharField(write_only=True)
    class Meta:
        model = Semester
        fields = ('semester_instance_uid', 'semester_number', 'course', 'course_code') 
    def create(self, validated_data):
        department_uid =self.context["view"].kwargs.get("department_uid")
        course_code = validated_data["course_code"].upper().strip()
        if department_uid and course_code:
            organization = get_organization(self.context.get('request'))
            try:
                course = Course.objects.get(course_code=course_code)
            except Course.DoesNotExist:
                raise serializers.ValidationError("Course does not exist")
            try:
                department = Department.objects.get(uid=department_uid)
            except Department.DoesNotExist:
                raise serializers.ValidationError("Department does not exist")
            if Semester.objects.filter(course=course, organization=organization, department=department).exists():
                raise serializers.ValidationError("Course already exists in the department's degree plan")
            try:
                plan = Semester.objects.create(course=course, organization=organization, department=department, semester_number=validated_data["semester_number"])
                return plan
            except:
                raise serializers.ValidationError("Could not add this course to degree plan.")
        else:
            raise serializers.ValidationError("Organization|Course code not found")
        
        
class PrivateDegreePlanDetailSerializer(serializers.ModelSerializer):
    course = PublicDegreePlanCourseListSerializer(read_only=True)
    semester_instance_uid = serializers.CharField(source='uid', read_only=True)
    course_code = serializers.CharField(write_only=True)
    class Meta:
        model = Semester
        exclude = ['id', 'department', 'organization']
        
    def update(self, instance, validated_data):
        course_code = validated_data.get('course_code').upper().strip()
        if course_code:
            try:
                course = Course.objects.get(course_code=course_code, organization=instance.organization, department=instance.department)
            except Course.DoesNotExist:
                raise serializers.ValidationError("Course does not exist")
            if Semester.objects.filter(course__course_code=course_code, organization=instance.organization, department=instance.department).exclude(id=instance.id).exists():
                raise serializers.ValidationError("Course already exists in this degree plan")
            try:
                instance.course = course
                instance.semester_number= validated_data.get('semester_number', instance.semester_number)
                instance.save()
            except:
                raise serializers.ValidationError("Could not update this course in degree plan")
            return instance
        else:
            raise serializers.ValidationError("Course code must be provided")
        
