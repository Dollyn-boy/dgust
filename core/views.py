from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse # Importe HttpResponse se for usá-lo em algum lugar
from orders.models import Order, OrderItem
from products.models import Category, Product
from combos.models import Combo

# O decorador @login_required foi removido desta view
def home(request):
    current_order = None
    if request.user.is_authenticated:
        current_order = Order.objects.filter(user=request.user, status='pending').first()

    if not current_order and request.user.is_authenticated:
        messages.info(request, "Você precisa ter um carrinho ativo para adicionar produtos. Criando um novo para você.")
        return redirect('create_order') 
    
    products = Product.objects.all()
    categories = Category.objects.all()
    combos = Combo.objects.all()
    print(combos.first().image.url)
     
    return render(request, 'core/home.html', {
        "order": current_order,
        'products': products,
        'categories': categories,
        'combos': combos
    } )
