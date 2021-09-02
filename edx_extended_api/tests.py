from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from triboo_analytics.models import LearnerCourseJsonReport
from student.models import UserProfile, CourseEnrollment
from lms.djangoapps.course_api.tests.mixins import CourseApiFactoryMixin
from openedx.core.djangoapps.site_configuration.models import SiteConfiguration
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from xmodule.modulestore.django import modulestore
from xmodule.modulestore.tests.factories import CourseFactory, XMODULE_FACTORY_LOCK


User = get_user_model()
test_config_multi_org = {   # pylint: disable=invalid-name
    "course_org_filter": ["FooOrg", "BarOrg", "FooBarOrg"]
}


def create_mock_site_config():
    site, __ = Site.objects.get_or_create(domain="example.com", name="example.com")
    site_configuration, created = SiteConfiguration.objects.get_or_create(
        site=site,
        defaults={"enabled": True, "values": test_config_multi_org},
    )
    if not created:
        site_configuration.values = test_config_multi_org
        site_configuration.save()


class CreateUserTests(APITestCase):

    def setUp(self):
        create_mock_site_config()

        self.user = User.objects.create(
            username='edx',
            is_staff=True,
            is_superuser=True,
            email='edx@example.com'
        )
        UserProfile.objects.create(
            user=self.user,
            org="FooOrg"
        )
        self.client.force_authenticate(user=self.user)

    def test_successful_user_creation(self):
        url = reverse('edx_extended_api:users-list')
        data = {
            "username": "user1",
            "email": "user1@example.com",
            "first_name": "first1",
            "last_name": "last1",
            "name": "One"
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get('status'), 'user_created')
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(UserProfile.objects.count(), 2)
        self.assertTrue(User.objects.filter(username='user1').exists())
        self.assertTrue(UserProfile.objects.filter(name='One').exists())
        self.assertEqual(UserProfile.objects.get(user__username=data['username']).org, self.user.profile.org)

    def test_used_username_user_creation(self):
        url = reverse('edx_extended_api:users-list')
        data = {
            "username": "edx",
            "email": "user2@example.com",
            "first_name": "first2",
            "last_name": "last2",
            "name": "Second"
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data.get('status'), 'username_already_used')

    def test_used_email_user_creation(self):
        url = reverse('edx_extended_api:users-list')
        data = {
            "username": "user3",
            "email": "edx@example.com",
            "first_name": "first3",
            "last_name": "last3",
            "name": "Three"
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data.get('status'), 'email_already_used')


class UpdateUserTests(APITestCase):

    def setUp(self):
        create_mock_site_config()

        self.user = User.objects.create(
            username='edx',
            is_staff=True,
            is_superuser=True,
            email='edx@example.com'
        )
        UserProfile.objects.create(
            user=self.user,
            org="FooOrg"
        )
        self.client.force_authenticate(user=self.user)
        self.user1 = User.objects.create(
            username='user1',
            email='user1@example.com',
            first_name="first1",
            last_name="last1",
        )
        self.user1_profile = UserProfile.objects.create(
            user=self.user1,
            name='One',
            org="FooOrg"
        )

    def test_successful_user_update_by_id(self):
        url = reverse(
            'edx_extended_api:users-detail',
            kwargs={'pk': self.user1.id}
        )
        data = {
            "name": "New_one_by_id"
        }

        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('status'), 'user_updated')
        self.assertEqual(response.data.get('name'), 'New_one_by_id')

    def test_user_not_found_update_by_id(self):
        url = reverse(
            'edx_extended_api:users-detail',
            kwargs={'pk': 100}
        )
        data = {
            "name": "New_one_by_id"
        }

        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.get('status'), 'user_not_found')

    def test_user_inactive_update_by_id(self):
        self.user1.is_active = False
        self.user1.save()
        url = reverse(
            'edx_extended_api:users-detail',
            kwargs={'pk': self.user1.id}
        )
        data = {
            "name": "New_one_by_id"
        }

        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data.get('status'), 'user_inactive')

    def test_username_used_update_by_id(self):
        url = reverse(
            'edx_extended_api:users-detail',
            kwargs={'pk': self.user1.id}
        )
        data = {
            "username": "edx"
        }

        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data.get('status'), 'username_already_used')

    def test_email_used_update_by_id(self):
        url = reverse(
            'edx_extended_api:users-detail',
            kwargs={'pk': self.user1.id}
        )
        data = {
            "email": "edx@example.com"
        }

        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data.get('status'), 'email_already_used')

    def test_successful_user_update_by_username(self):
        url = reverse(
            'edx_extended_api:users_by_username-detail',
            kwargs={'username': self.user1.username}
        )
        data = {
            "name": "New_one_by_username"
        }

        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('status'), 'user_updated')
        self.assertEqual(response.data.get('name'), 'New_one_by_username')

    def test_user_not_found_update_by_username(self):
        url = reverse(
            'edx_extended_api:users_by_username-detail',
            kwargs={'username': 'not_existing_username'}
        )
        data = {
            "name": "New_one_by_id"
        }

        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.get('status'), 'user_not_found')

    def test_user_inactive_update_by_username(self):
        self.user1.is_active = False
        self.user1.save()
        url = reverse(
            'edx_extended_api:users_by_username-detail',
            kwargs={'username': self.user1.username}
        )
        data = {
            "name": "New_one_by_id"
        }

        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data.get('status'), 'user_inactive')

    def test_username_used_update_by_username(self):
        url = reverse(
            'edx_extended_api:users_by_username-detail',
            kwargs={'username': self.user1.username}
        )
        data = {
            "username": "edx"
        }

        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data.get('status'), 'username_already_used')

    def test_email_used_update_by_username(self):
        url = reverse(
            'edx_extended_api:users_by_username-detail',
            kwargs={'username': self.user1.username}
        )
        data = {
            "email": "edx@example.com"
        }

        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data.get('status'), 'email_already_used')


class GetUserTests(APITestCase):

    def setUp(self):
        create_mock_site_config()

        self.user = User.objects.create(
            username='edx',
            is_staff=True,
            is_superuser=True,
            email='edx@example.com'
        )
        UserProfile.objects.create(
            user=self.user,
            org="FooOrg"
        )
        self.client.force_authenticate(user=self.user)
        self.user1 = User.objects.create(
            username='user1',
            email='user1@example.com',
            first_name="first1",
            last_name="last1",
        )
        self.user1_profile = UserProfile.objects.create(
            user=self.user1,
            name='One',
            org="FooOrg"
        )
        self.user2 = User.objects.create(
            username='user2',
            email='user2@example.com',
            first_name="first2",
            last_name="last2",
        )
        self.user2_profile = UserProfile.objects.create(
            user=self.user2,
            name='Two',
            org="FooOrg"
        )

    def test_get_users(self):
        url = reverse('edx_extended_api:users-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get("results")), 3)

    def test_get_users_org_filtering(self):
        self.user2_profile.org = ""
        self.user2_profile.save()
        url = reverse('edx_extended_api:users-list')

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get("results")), 2)

    def test_get_user_by_id(self):
        url = reverse(
            'edx_extended_api:users-detail',
            kwargs={'pk': self.user1.id}
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("username"), "user1")
        self.assertTrue(response.data.get("is_active"))

    def test_get_users_by_ids(self):
        url = "{}?{}".format(
            reverse('edx_extended_api:users-list'),
            "user_id={},{}".format(self.user1.id, self.user2.id)
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get("results")), 2)
        self.assertEqual(response.data.get("results")[0].get("user_id"), self.user1.id)
        self.assertEqual(response.data.get("results")[1].get("user_id"), self.user2.id)

    def test_get_user_by_id_not_found(self):
        url = reverse(
            'edx_extended_api:users-detail',
            kwargs={'pk': 123}
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.get("detail"), "Not found.")

    def test_get_user_by_username(self):
        url = reverse(
            'edx_extended_api:users_by_username-detail',
            kwargs={'username': self.user1.username}
        )

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("username"), "user1")
        self.assertTrue(response.data.get("is_active"))

    def test_get_users_by_usernames(self):
        url = "{}?{}".format(
            reverse('edx_extended_api:users_by_username-list'),
            "username={},{}".format(self.user1.username, self.user2.username)
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get("results")), 2)
        self.assertEqual(response.data.get("results")[0].get("username"), self.user1.username)
        self.assertEqual(response.data.get("results")[1].get("username"), self.user2.username)

    def test_get_user_by_username_not_found(self):
        url = reverse(
            'edx_extended_api:users_by_username-detail',
            kwargs={'username': 'not_existing_username'}
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.get("detail"), "Not found.")


class DeactivateUserTests(APITestCase):

    def setUp(self):
        create_mock_site_config()

        self.user = User.objects.create(
            username='edx',
            is_staff=True,
            is_superuser=True,
            email='edx@example.com'
        )
        UserProfile.objects.create(
            user=self.user,
            org="FooOrg"
        )
        self.client.force_authenticate(user=self.user)
        self.user1 = User.objects.create(
            username='user1',
            email='user1@example.com',
            first_name="first1",
            last_name="last1",
        )
        self.user1_profile = UserProfile.objects.create(
            user=self.user1,
            name='One',
            org="FooOrg"
        )
        self.user2 = User.objects.create(
            username='user2',
            email='user2@example.com',
            first_name="first2",
            last_name="last2",
        )
        self.user2_profile = UserProfile.objects.create(
            user=self.user2,
            name='Two',
            org="FooOrg"
        )

    def test_deactivate_user_by_id(self):
        url = reverse(
            'edx_extended_api:users-detail',
            kwargs={'pk': self.user1.id}
        )

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("username"), self.user1.username)
        self.assertEqual(response.data.get("status"), "user_deactivated")
        self.assertEqual(response.data.get("user_id"), self.user1.id)

    def test_deactivate_users_by_ids(self):
        url = "{}?{}".format(
            reverse('edx_extended_api:users-list'),
            "user_id={},{}".format(self.user1.id, self.user2.id)
        )

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0].get("username"), self.user1.username)
        self.assertEqual(response.data[0].get("status"), "user_deactivated")
        self.assertEqual(response.data[0].get("user_id"), self.user1.id)

        self.assertEqual(response.data[1].get("username"), self.user2.username)
        self.assertEqual(response.data[1].get("status"), "user_deactivated")
        self.assertEqual(response.data[1].get("user_id"), self.user2.id)

    def test_deactivate_user_by_id_already_deactivated(self):
        self.user1.is_active = False
        self.user1.save()
        url = reverse(
            'edx_extended_api:users-detail',
            kwargs={'pk': self.user1.id}
        )

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("username"), self.user1.username)
        self.assertEqual(response.data.get("status"), "user_already_inactive")
        self.assertEqual(response.data.get("user_id"), self.user1.id)

    def test_deactivate_user_by_id_not_found(self):
        url = reverse(
            'edx_extended_api:users-detail',
            kwargs={'pk': 123}
        )

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.get("detail"), "Not found.")

    def test_deactivate_user_by_username(self):
        url = reverse(
            'edx_extended_api:users_by_username-detail',
            kwargs={'username': self.user1.username}
        )

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("username"), self.user1.username)
        self.assertEqual(response.data.get("status"), "user_deactivated")
        self.assertEqual(response.data.get("user_id"), self.user1.id)

    def test_deactivate_users_by_usernames(self):
        url = "{}?{}".format(
            reverse('edx_extended_api:users_by_username-list'),
            "username={},{}".format(self.user1.username, self.user2.username)
        )

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0].get("username"), self.user1.username)
        self.assertEqual(response.data[0].get("status"), "user_deactivated")
        self.assertEqual(response.data[0].get("user_id"), self.user1.id)

        self.assertEqual(response.data[1].get("username"), self.user2.username)
        self.assertEqual(response.data[1].get("status"), "user_deactivated")
        self.assertEqual(response.data[1].get("user_id"), self.user2.id)

    def test_deactivate_user_by_username_already_deactivated(self):
        self.user1.is_active = False
        self.user1.save()
        url = reverse(
            'edx_extended_api:users_by_username-detail',
            kwargs={'username': self.user1.username}
        )

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("username"), self.user1.username)
        self.assertEqual(response.data.get("status"), "user_already_inactive")
        self.assertEqual(response.data.get("user_id"), self.user1.id)

    def test_deactivate_user_by_username_not_found(self):
        url = reverse(
            'edx_extended_api:users_by_username-detail',
            kwargs={'username': 'not_existing_username'}
        )

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.get("detail"), "Not found.")


class CoursesTests(CourseApiFactoryMixin, APITestCase):

    def setUp(self):
        create_mock_site_config()

        XMODULE_FACTORY_LOCK.enable()

        if not CourseOverview.objects.all() and modulestore().get_courses():
            CourseOverview.load_from_module_store(modulestore().get_courses()[0].id)
        else:
            self.create_course()

        self.user = User.objects.create(
            username='edx',
            is_staff=True,
            is_superuser=True,
            email='edx@example.com'
        )
        UserProfile.objects.create(
            user=self.user,
            org="FooOrg"
        )
        self.client.force_authenticate(user=self.user)

    def test_get_courses(self):
        test_course = CourseOverview.objects.first()
        test_course.org = "FooOrg"
        test_course.save()
        url = reverse('edx_extended_api:courses-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get("results")), 1)
        self.assertEqual(len(response.data.get("results")[0].keys()), 15)

    def test_get_course_without_org(self):
        test_course = CourseOverview.objects.first()
        test_course.org = ""
        test_course.save()
        url = reverse('edx_extended_api:courses-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("results"), [])


class UserProgressReportTests(CourseApiFactoryMixin, APITestCase):

    def setUp(self):
        create_mock_site_config()
        XMODULE_FACTORY_LOCK.enable()
        if not CourseOverview.objects.all() and modulestore().get_courses():
            CourseOverview.load_from_module_store(modulestore().get_courses()[0].id)
        else:
            self.create_course()

        test_course = CourseOverview.objects.first()

        self.user = User.objects.create(
            username='edx',
            is_staff=True,
            is_superuser=True,
            email='edx@example.com'
        )
        UserProfile.objects.create(
            user=self.user,
            org="FooOrg"
        )
        self.client.force_authenticate(user=self.user)
        self.user1 = User.objects.create(
            username='user1',
            email='user1@example.com',
            first_name="first1",
            last_name="last1",
        )
        self.user1_profile = UserProfile.objects.create(
            user=self.user1,
            name='One',
            org="FooOrg"
        )
        self.user2 = User.objects.create(
            username='user2',
            email='user2@example.com',
            first_name="first2",
            last_name="last2",
        )
        self.user2_profile = UserProfile.objects.create(
            user=self.user2,
            name='Two',
            org="FooOrg"
        )
        CourseEnrollment.objects.create(
            user=self.user1,
            course=test_course
        )
        CourseEnrollment.objects.create(
            user=self.user2,
            course=test_course
        )
        LearnerCourseJsonReport.objects.create(
            user=self.user1,
            course_id=test_course.id,
            org="FooOrg"
        )
        LearnerCourseJsonReport.objects.create(
            user=self.user2,
            course_id=test_course.id,
            org="FooOrg"
        )

    def test_get_user_progress_report_by_id(self):
        test_course = CourseOverview.objects.first()
        test_course.org = "FooOrg"
        test_course.save()
        url = reverse(
            'edx_extended_api:user_progress_report-detail',
            kwargs={'pk': self.user1.id}
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("username"), self.user1.username)
        self.assertEqual(len(response.data.get("courses")), 1)
        self.assertEqual(len(response.data.get("courses")[0].keys()), 9)

    def test_get_users_progress_reports_by_ids(self):
        CourseOverview.objects.update(org="FooOrg")
        url = "{}?{}".format(
            reverse('edx_extended_api:user_progress_report-list'),
            "?user_id={},{}".format(self.user1.id, self.user2.id)
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get("results")), 3)

    def test_get_user_progress_report_without_org_by_id(self):
        LearnerCourseJsonReport.objects.update(org="")
        CourseOverview.objects.update(org="")
        self.user1_profile.org = ""
        self.user1_profile.save()
        url = reverse(
            'edx_extended_api:user_progress_report-detail',
            kwargs={'pk': self.user1.id}
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.get("detail"), "Not found.")

    def test_get_user_progress_report_by_username(self):
        test_course = CourseOverview.objects.first()
        test_course.org = "FooOrg"
        test_course.save()
        url = reverse(
            'edx_extended_api:user_progress_report_by_username-detail',
            kwargs={'username': self.user1.username}
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("username"), self.user1.username)
        self.assertEqual(len(response.data.get("courses")), 1)
        self.assertEqual(len(response.data.get("courses")[0].keys()), 9)

    def test_get_users_progress_reports_by_usernames(self):
        test_course = CourseOverview.objects.first()
        test_course.org = "FooOrg"
        test_course.save()
        url = "{}?{}".format(
            reverse('edx_extended_api:user_progress_report_by_username-list'),
            "?username={},{}".format(self.user1.username, self.user2.username)
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get("results")), 3)

    def test_get_user_progress_report_without_org_by_username(self):
        LearnerCourseJsonReport.objects.update(org="")
        CourseOverview.objects.update(org="")
        self.user1_profile.org = ""
        self.user1_profile.save()
        url = reverse(
            'edx_extended_api:user_progress_report_by_username-detail',
            kwargs={'username': self.user1.username}
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.get("detail"), "Not found.")
