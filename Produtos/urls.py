# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_produto, name='cardapio_completo'), # TODO Criar uma view específica para o cardápio.
    path('<int:produto_id>', views.detalhes_produto, name='detalhes_produto'),
    path('<int:pizza_id>/json/', views.detalhes_pizza_json, name='detalhes_pizza_json'),
]
