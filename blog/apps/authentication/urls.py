from django.urls import re_path

from .views import LoginView, RegisterView, UserView

app_name = 'authentication'

urlpatterns = [
    re_path(r'^user$', UserView.as_view(), name='retrieve_view'),
    re_path(r'^users$', RegisterView.as_view(), name='register_view'),
    re_path(r'^users/login$', LoginView.as_view(), name='login_view'),
]
