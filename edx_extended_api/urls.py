from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from views import UsersViewSet, UsersByUsernameViewSet


router = DefaultRouter()
router.register(r'users', UsersViewSet, base_name='users')
router.register(r'users_by_username', UsersByUsernameViewSet, base_name='users_by_username')

urlpatterns = [
    url(r'api/', include(router.urls)),
]
