from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product # Importe o modelo Product
from django.http import HttpResponse # Importe HttpResponse se for usá-lo em algum lugar
from orders.models import Order, OrderItem

# O decorador @login_required foi removido desta view
def product_list(request):
    products = Product.objects.filter(active=True).order_by('name')

    current_order = None
    if request.user.is_authenticated:
        current_order = Order.objects.filter(user=request.user, status='pending').first()

    if not current_order and request.user.is_authenticated:
        messages.info(request, "Você precisa ter um carrinho ativo para adicionar produtos. Criando um novo para você.")
        return redirect('create_order') 
    
    return render(request, 'products/product_list.html', {
        'products': products,
        'order': current_order 
    })

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, active=True)

    current_order = None
    if request.user.is_authenticated:
        current_order = Order.objects.filter(user=request.user, status='pending').first()

    if not current_order and request.user.is_authenticated:
        messages.info(request, "Você precisa ter um carrinho ativo para adicionar este produto. Criando um novo para você.")
        return redirect('create_order') 
    
    pizza_borders = product.available_pizza_borders.all().order_by('name')
    pizza_flavors = product.available_pizza_flavors.all().order_by('name')
    option_types = product.available_option_types.all().prefetch_related('options').order_by('name')

    return render(request, 'products/product_detail.html', {
        'product': product,
        'order': current_order, # Pode ser None se o usuário não estiver logado
        'pizza_borders': pizza_borders,
        'pizza_flavors': pizza_flavors,
        'option_types': option_types,
    })
