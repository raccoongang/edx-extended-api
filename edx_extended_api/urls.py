from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from views import CreateUserView


router = DefaultRouter()
router.register(r'create_user', CreateUserView, base_name='create_user')

urlpatterns = [
    url(r'api/', include(router.urls)),
]
