from django.contrib.auth import get_user_model
from student.models import UserProfile
from rest_framework import serializers


User = get_user_model()


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
    service_id = serializers.CharField(source='profile.service_id', required=False)
    language = serializers.CharField(source='profile.language', required=False)
    location = serializers.CharField(source='profile.location', required=False)
    year_of_birth = serializers.IntegerField(source='profile.year_of_birth', required=False)
    bio = serializers.CharField(source='profile.bio', required=False)
    goals = serializers.CharField(source='profile.goals', required=False)
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

    class Meta(object):
        model = User
        fields = (
            'email', 'username', 'first_name', 'last_name', 'service_id', 'language', 'location', 'year_of_birth',
            'bio', 'goals', 'gender', 'city', 'country', 'lt_custom_country', 'lt_area', 'lt_sub_area', 'lt_address',
            'lt_address_2', 'lt_phone_number', 'lt_gdpr', 'lt_company', 'lt_employee_id', 'lt_hire_date', 'lt_level',
            'lt_job_code', 'lt_job_description', 'lt_department', 'lt_supervisor', 'lt_learning_group',
            'lt_exempt_status', 'lt_is_tos_agreed', 'lt_comments', 'lt_ilt_supervisor'
        )

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        user = User.objects.create(**validated_data)
        UserProfile.objects.create(user=user, **profile_data)
        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile')
        User.objects.update_or_create(id=instance.id, defaults=validated_data)
        UserProfile.objects.update_or_create(user=instance, defaults=profile_data)
        return instance


class RetrieveListUserSerializer(UserSerializer):
    user_id = serializers.IntegerField(source='id')

    def __init__(self, *args, **kwargs):
        self.Meta.fields += ('user_id', 'is_active')
        super(RetrieveListUserSerializer, self).__init__(*args, **kwargs)
