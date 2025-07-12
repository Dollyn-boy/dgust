"""
URL configuration for dgust_site project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from core.views import listar_produto, detalhes_pizza_json, detalhes_produto_json, comprar, detalhes_carrinho_json, deletar_item_carrinho
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', listar_produto, name='listar_produtos'),
    path('pizza/<int:pizza_id>/json/', detalhes_pizza_json, name='detalhes_pizza_json'),
    path('produto/<int:product_id>/json/', detalhes_produto_json, name='detalhes_produto_json'),
    path('comprar/', comprar, name='comprar'),
    path('carrinho/json', detalhes_carrinho_json, name='detalhes_carrinho_json' ),
    path('carrinho/deletar/<int:item_id>/', deletar_item_carrinho, name='deletar_item_carrinho'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)