from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from views import UsersViewSet, UsersByUsernameViewSet, CoursesViewSet, UserProgressViewSet, UserProgressByUsernameViewSet


router = DefaultRouter()
router.register(r'users', UsersViewSet, base_name='users')
router.register(r'users_by_username', UsersByUsernameViewSet, base_name='users_by_username')
router.register(r'courses', CoursesViewSet, base_name='courses')
router.register(r'user_progress_report', UserProgressViewSet, base_name='user_progress_report')
router.register(
    r'user_progress_report_by_username', UserProgressByUsernameViewSet, base_name='user_progress_report_by_username'
)

urlpatterns = [
    url(r'api/', include(router.urls)),
]
