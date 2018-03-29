from django.urls import path, include

urlpatterns = [
    path('api/', include('apps.authentication.urls')),
    path('api/', include('apps.posts.urls')),
    path('api/', include('apps.profiles.urls')),
]
