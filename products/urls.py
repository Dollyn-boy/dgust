
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import product_detail, product_list 

urlpatterns = [
    path('', product_list, name='product_list' ),
    path('<int:product_id>/', product_detail, name='product_detail' )
]