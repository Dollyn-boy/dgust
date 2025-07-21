from django.urls import path
from .views import register_or_login, logout_view, profile

urlpatterns = [
    path('login/', register_or_login, name='register_or_login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile, name='user_profile_data'),
]