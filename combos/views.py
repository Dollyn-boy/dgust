# from django.shortcuts import render
# from .models import Combo, ComboItem
# from orders.models import Order
# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib import messages

# # Create your views here.
# def product_list(request):
#     combo = Combo.objects.filter(active=True).order_by('name')
    
#     current_order = None
#     if request.user.is_authenticated:
#         current_order = Order.objects.filter(user=request.user, status='pending').first()

#     if not current_order and request.user.is_authenticated:
#         messages.info(request, "Você precisa ter um carrinho ativo para adicionar produtos. Criando um novo para você.")
#         return redirect('create_order') 
    
#     return render(request, 'products/product_list.html', {
#         'products': products,
#         'order': current_order 
#     })