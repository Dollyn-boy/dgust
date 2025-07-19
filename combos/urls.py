
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import combo_list, combo_detail 

urlpatterns = [
    path('', combo_list, name='combo_list'),
    path('<int:combo_id>/', combo_detail, name='combo_detail' )
]