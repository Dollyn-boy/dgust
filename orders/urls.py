from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_order, name='create_order'),
    path('<int:order_id>/', views.view_order, name='view_order'),
    path('<int:order_id>/add-item/', views.add_item_to_order, name='add_item_to_order'),
    path('<int:order_id>/complete/', views.complete_order, name='complete_order'),
    path('<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),
    path('history/', views.order_history, name='order_history'),
    # Adicione outras URLs conforme necessário (ex: para remover itens, atualizar quantidade)
]