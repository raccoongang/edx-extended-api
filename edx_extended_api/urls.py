from django.conf.urls import url
from views import CreateUserView

urlpatterns = [
    url(r'api/create_user', CreateUserView.as_view({'post': 'create'}), name='create_user')
]
