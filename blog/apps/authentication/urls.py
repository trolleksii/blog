from django.urls import re_path

from .views import LoginAPIView, RegisterAPIView, UserAPIView

app_name = 'authentication'

urlpatterns = [
    re_path(r'^user$', UserAPIView.as_view(), name='retrieve_view'),
    re_path(r'^users$', RegisterAPIView.as_view(), name='register_view'),
    re_path(r'^users/login$', LoginAPIView.as_view(), name='login_view'),
]
