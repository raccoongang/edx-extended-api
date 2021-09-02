# -*- coding: utf-8 -*-
from badges.utils import site_prefix
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from student import triboo_groups
from student.models import UserProfile
from student.roles import STUDIO_ADMIN_ACCESS_GROUP
from rest_framework.fields import empty
from rest_framework import serializers
from triboo_analytics.models import ANALYTICS_ACCESS_GROUP, ANALYTICS_LIMITED_ACCESS_GROUP
from openedx.core.djangoapps.models.course_details import CourseDetails
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from triboo_analytics.models import LearnerCourseJsonReport, LearnerBadgeJsonReport, CourseStatus


User = get_user_model()


def get_or_create_and_add_group(user_instance, group_name):
    group, _ = Group.objects.get_or_create(name=group_name)
    user_instance.groups.add(group)


def get_or_create_and_remove_group(user_instance, group_name):
    group, _ = Group.objects.get_or_create(name=group_name)
    user_instance.groups.remove(group)


def set_user_platform_role(platform_role, user):
    if platform_role == 'Super Platform Admin':
        user.is_superuser = True
        user.is_staff = True
    elif platform_role == 'Platform Admin':
        user.is_superuser = False
        user.is_staff = True
    elif platform_role == 'Studio Admin':
        user.is_superuser = False
        user.is_staff = False
        get_or_create_and_add_group(user, STUDIO_ADMIN_ACCESS_GROUP)
    elif platform_role == 'Learner':
        user.is_superuser = False
        user.is_staff = False
        get_or_create_and_remove_group(user, STUDIO_ADMIN_ACCESS_GROUP)
    user.save()


GROUP_ACTIONS = {
    True: get_or_create_and_add_group,
    False: get_or_create_and_remove_group,
}
ACCESSES_NAMES = {
    'internal_catalog_access': triboo_groups.CATALOG_DENIED_GROUP,
    'edflex_catalog_access': triboo_groups.EDFLEX_DENIED_GROUP,
    'crehana_catalog_access': triboo_groups.CREHANA_DENIED_GROUP,
    'anderspink_catalog_access': triboo_groups.ANDERSPINK_DENIED_GROUP,
    'learnlight_catalog_access': triboo_groups.LEARNLIGHT_DENIED_GROUP
}


class CharSerializerMethodField(serializers.SerializerMethodField):
    """
    Field that works as SerializerMethodField but supports writing.
    """
    default_error_messages = {
        'invalid': 'Enter a valid string.'
    }

    def __init__(self, method_name=None, **kwargs):
        self.method_name = method_name
        kwargs['read_only'] = False
        kwargs['source'] = '*'
        super(serializers.SerializerMethodField, self).__init__(**kwargs)

    def run_validation(self, data=empty):
        return {self.field_name: super(CharSerializerMethodField, self).run_validation(data)}

    def to_internal_value(self, data):
        if not isinstance(data, (str, unicode)):
            self.fail('invalid')
        return unicode(data).strip()


class BooleanSerializerMethodField(serializers.SerializerMethodField):

    def __init__(self, method_name=None, **kwargs):
        self.method_name = method_name
        kwargs['read_only'] = False
        kwargs['source'] = '*'
        super(serializers.SerializerMethodField, self).__init__(**kwargs)

    TRUE_VALUES = {
        't', 'T',
        'y', 'Y', 'yes', 'Yes', 'YES',
        'true', 'True', 'TRUE',
        'on', 'On', 'ON',
        '1', 1,
        True
    }
    FALSE_VALUES = {
        'f', 'F',
        'n', 'N', 'no', 'No', 'NO',
        'false', 'False', 'FALSE',
        'off', 'Off', 'OFF',
        '0', 0, 0.0,
        False
    }
    NULL_VALUES = {'null', 'Null', 'NULL', '', None}

    def run_validation(self, data=empty):
        return {self.field_name: super(BooleanSerializerMethodField, self).run_validation(data)}

    def to_internal_value(self, data):
        try:
            if data in self.TRUE_VALUES:
                return True
            elif data in self.FALSE_VALUES:
                return False
            elif data in self.NULL_VALUES and self.allow_null:
                return None
        except TypeError:  # Input is an unhashable type
            pass
        self.fail('invalid', input=data)


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta(object):
        model = UserProfile
        fields = (
            'service_id', 'language', 'location', 'year_of_birth', 'bio', 'goals', 'level_of_education', 'gender',
            'city', 'country', 'lt_custom_country', 'lt_area', 'lt_sub_area', 'lt_address', 'lt_address_2',
            'lt_phone_number', 'lt_gdpr', 'lt_company', 'lt_employee_id', 'lt_hire_date', 'lt_level', 'lt_job_code',
            'lt_job_description', 'lt_department', 'lt_supervisor', 'lt_learning_group', 'lt_exempt_status',
            'lt_is_tos_agreed', 'lt_comments', 'lt_ilt_supervisor'
        )


class UserSerializer(serializers.ModelSerializer):
    """Serializes user information. """
    language = serializers.CharField(source='profile.language', required=False)
    location = serializers.CharField(source='profile.location', required=False)
    year_of_birth = serializers.IntegerField(source='profile.year_of_birth', required=False)
    bio = serializers.CharField(source='profile.bio', required=False)
    goals = serializers.CharField(source='profile.goals', required=False)
    level_of_education = serializers.CharField(source='profile.level_of_education', required=False)
    name = serializers.CharField(source='profile.name', required=False)
    gender = serializers.CharField(source='profile.gender', required=False)
    city = serializers.CharField(source='profile.city', required=False)
    country = serializers.CharField(source='profile.country', required=False)
    lt_custom_country = serializers.CharField(source='profile.lt_custom_country', required=False)
    lt_area = serializers.CharField(source='profile.lt_area', required=False)
    lt_sub_area = serializers.CharField(source='profile.lt_sub_area', required=False)
    lt_address = serializers.CharField(source='profile.lt_address', required=False)
    lt_address_2 = serializers.CharField(source='profile.lt_address_2', required=False)
    lt_phone_number = serializers.CharField(source='profile.lt_phone_number', required=False)
    lt_gdpr = serializers.BooleanField(source='profile.lt_gdpr', required=False)
    lt_company = serializers.CharField(source='profile.lt_company', required=False)
    lt_employee_id = serializers.CharField(source='profile.lt_employee_id', required=False)
    lt_hire_date = serializers.DateField(source='profile.lt_hire_date', required=False)
    lt_level = serializers.CharField(source='profile.lt_level', required=False)
    lt_job_code = serializers.CharField(source='profile.lt_job_code', required=False)
    lt_job_description = serializers.CharField(source='profile.lt_job_description', required=False)
    lt_department = serializers.CharField(source='profile.lt_department', required=False)
    lt_supervisor = serializers.CharField(source='profile.lt_supervisor', required=False)
    lt_learning_group = serializers.CharField(source='profile.lt_learning_group', required=False)
    lt_exempt_status = serializers.BooleanField(source='profile.lt_exempt_status', required=False)
    lt_is_tos_agreed = serializers.BooleanField(source='profile.lt_is_tos_agreed', required=False)
    lt_comments = serializers.CharField(source='profile.lt_comments', required=False)
    lt_ilt_supervisor = serializers.BooleanField(source='profile.lt_ilt_supervisor', required=False)
    analytics_access = CharSerializerMethodField(required=False, allow_null=True)
    internal_catalog_access = BooleanSerializerMethodField(required=False)
    edflex_catalog_access = BooleanSerializerMethodField(required=False)
    crehana_catalog_access = BooleanSerializerMethodField(required=False)
    anderspink_catalog_access = BooleanSerializerMethodField(required=False)
    learnlight_catalog_access = BooleanSerializerMethodField(required=False)
    platform_role = CharSerializerMethodField(required=False, default='Learner')

    class Meta(object):
        model = User
        fields = (
            'email', 'username', 'first_name', 'last_name', 'language', 'location', 'year_of_birth', 'bio', 'goals',
            'level_of_education', 'name', 'gender', 'city', 'country', 'lt_custom_country', 'lt_area', 'lt_sub_area',
            'lt_address', 'lt_address_2', 'lt_phone_number', 'lt_gdpr', 'lt_company', 'lt_employee_id', 'lt_hire_date',
            'lt_level', 'lt_job_code', 'lt_job_description', 'lt_department', 'lt_supervisor', 'lt_learning_group',
            'lt_exempt_status', 'lt_is_tos_agreed', 'lt_comments', 'lt_ilt_supervisor', 'analytics_access',
            'internal_catalog_access', 'edflex_catalog_access', 'crehana_catalog_access', 'anderspink_catalog_access',
            'learnlight_catalog_access', 'platform_role'
        )

    def get_fields(self):
        fields = super(UserSerializer, self).get_fields()
        request = self.context.get('request', None)
        if request and getattr(request, 'method', None) == "POST":
            fields['email'].required = True
            fields['first_name'].required = True
            fields['last_name'].required = True
            fields['name'].required = True
        return fields

    def get_analytics_access(self, user):
        user_groups = user.groups.all()
        if not user_groups:
            return None
        if user.groups.filter(name=ANALYTICS_LIMITED_ACCESS_GROUP).exists():
            return "Restricted"
        if user.groups.filter(name=ANALYTICS_ACCESS_GROUP).exists():
            return "Full Access"

    def get_platform_role(self, user):
        if user.is_superuser and user.is_staff:
            return 'Super Platform Admin'
        elif user.is_staff:
            return 'Platform Admin'
        elif user.groups.filter(name=STUDIO_ADMIN_ACCESS_GROUP).exists():
            return 'Studio Admin'
        else:
            return 'Learner'

    def get_internal_catalog_access(self, user):
        return True if user.groups.filter(name=triboo_groups.CATALOG_DENIED_GROUP).exists() else False

    def get_edflex_catalog_access(self, user):
        return True if user.groups.filter(name=triboo_groups.EDFLEX_DENIED_GROUP).exists() else False

    def get_crehana_catalog_access(self, user):
        return True if user.groups.filter(name=triboo_groups.CREHANA_DENIED_GROUP).exists() else False

    def get_anderspink_catalog_access(self, user):
        return True if user.groups.filter(name=triboo_groups.ANDERSPINK_DENIED_GROUP).exists() else False

    def get_learnlight_catalog_access(self, user):
        return True if user.groups.filter(name=triboo_groups.LEARNLIGHT_DENIED_GROUP).exists() else False

    def create(self, validated_data):
        profile_data = validated_data.pop('profile', {})
        accesses_dict = {}
        validated_data_keys = validated_data.keys()
        analytics_access = validated_data.pop('analytics_access', False)
        platform_role = validated_data.pop('platform_role', 'Learner')

        for name, _ in ACCESSES_NAMES.items():
            if name in validated_data_keys:
                accesses_dict.update({
                    name: validated_data.pop(name)
                })

        user = User.objects.create(**validated_data)

        if analytics_access == 'Restricted':
            get_or_create_and_add_group(user, ANALYTICS_LIMITED_ACCESS_GROUP)
        elif analytics_access == 'Full Access':
            get_or_create_and_add_group(user, ANALYTICS_ACCESS_GROUP)

        set_user_platform_role(platform_role, user)

        [GROUP_ACTIONS[value](user, ACCESSES_NAMES[key]) for key, value in accesses_dict.items()]

        UserProfile.objects.create(user=user, **profile_data)
        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        accesses_dict = {}
        validated_data_keys = validated_data.keys()
        analytics_access = validated_data.pop('analytics_access', False)
        platform_role = validated_data.pop('platform_role', None)

        for name, _ in ACCESSES_NAMES.items():
            if name in validated_data_keys:
                accesses_dict.update({
                    name: validated_data.pop(name)
                })

        if analytics_access == 'Restricted':
            get_or_create_and_remove_group(instance, ANALYTICS_ACCESS_GROUP)
            get_or_create_and_add_group(instance, ANALYTICS_LIMITED_ACCESS_GROUP)
        elif analytics_access == 'Full Access':
            get_or_create_and_remove_group(instance, ANALYTICS_LIMITED_ACCESS_GROUP)
            get_or_create_and_add_group(instance, ANALYTICS_ACCESS_GROUP)
        elif analytics_access is None:
            get_or_create_and_remove_group(instance, ANALYTICS_LIMITED_ACCESS_GROUP)
            get_or_create_and_remove_group(instance, ANALYTICS_ACCESS_GROUP)

        set_user_platform_role(platform_role, user)

        [GROUP_ACTIONS[value](instance, ACCESSES_NAMES[key]) for key, value in accesses_dict.items()]
        User.objects.update_or_create(id=instance.id, defaults=validated_data)
        UserProfile.objects.update_or_create(user=instance, defaults=profile_data)
        return instance


class RetrieveListUserSerializer(UserSerializer):
    user_id = serializers.IntegerField(source='id')

    class Meta(object):
        model = User
        fields = UserSerializer.Meta.fields + ('user_id', 'is_active')


class CourseSerializer(serializers.ModelSerializer):
    overview_url = serializers.SerializerMethodField()
    card_image_url = serializers.SerializerMethodField()
    banner_image_url = serializers.SerializerMethodField()
    instructors = serializers.SerializerMethodField()
    course_category = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    countries = serializers.SerializerMethodField()
    learning_groups = serializers.SerializerMethodField()

    class Meta(object):
        model = CourseOverview
        fields = (
            'id', 'display_name', 'overview_url', 'start', 'card_image_url', 'banner_image_url', 'short_description',
            'instructors', 'effort', 'language', 'course_category', 'tags', 'countries', 'learning_groups', 'modified'
        )

    def get_overview_url(self, course):
        return u'{}{}'.format(
            site_prefix(),
            reverse('about_course', kwargs={'course_id': unicode(course.id)})
        )

    def get_card_image_url(self, course):
        return u'{}{}'.format(
            site_prefix(),
            CourseDetails.fetch(course.id).course_image_asset_path
        )

    def get_banner_image_url(self, course):
        return u'{}{}'.format(
            site_prefix(),
            CourseDetails.fetch(course.id).banner_image_asset_path
        )

    def get_instructors(self, course):
        return CourseDetails.fetch(course.id).instructor_info.get("instructors", [])

    def get_course_category(self, course):
        return CourseDetails.fetch(course.id).course_category

    def get_tags(self, course):
        return CourseDetails.fetch(course.id).vendor

    def get_countries(self, course):
        return CourseDetails.fetch(course.id).course_country

    def get_learning_groups(self, course):
        return CourseDetails.fetch(course.id).enrollment_learning_groups


class LearnerBadgeJsonReportSerializer(serializers.ModelSerializer):
    badge = serializers.SerializerMethodField()

    class Meta(object):
        model = LearnerBadgeJsonReport
        fields = ('badge', 'score', 'success', 'success_date')

    def get_badge(self, obj):
        return u'%s ▸ %s' % (obj.badge.grading_rule, obj.badge.section_name)


class LearnerCourseJsonReportSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    course_title = serializers.SerializerMethodField()
    badges = serializers.SerializerMethodField()

    class Meta(object):
        model = LearnerCourseJsonReport
        fields = (
            'course_id', 'status', 'progress', 'current_score', 'total_time_spent',
            'enrollment_date', 'completion_date', 'course_title', 'badges'
        )

    def get_status(self, obj):
        try:
            return CourseStatus.verbose_names[obj.status]
        except IndexError:
            return None

    def get_course_title(self, obj):
        course_overview = CourseOverview.objects.filter(id=obj.course_id).first()
        return course_overview and course_overview.display_name or obj.course_id

    def get_badges(self, obj):
        badges = LearnerBadgeJsonReport.objects.filter(user_id=obj.user_id, badge__course_id=obj.course_id)
        return LearnerBadgeJsonReportSerializer(badges, many=True).data


class UserProgressSerializer(RetrieveListUserSerializer):
    name = serializers.CharField(source='profile.name')
    courses = serializers.SerializerMethodField()

    class Meta(object):
        model = User
        fields = ('user_id', 'username', 'name', 'courses')

    def get_courses(self, user):
        courses = LearnerCourseJsonReportSerializer.Meta.model.objects.filter(user=user)
        return LearnerCourseJsonReportSerializer(courses, many=True).data
