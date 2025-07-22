from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product # Importe o modelo Product
from django.http import HttpResponse # Importe HttpResponse se for usá-lo em algum lugar
from orders.models import Order, OrderItem
from django.http import JsonResponse

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

# def product_detail(request, product_id):
#     product = get_object_or_404(Product, id=product_id, active=True)

#     current_order = None
#     if request.user.is_authenticated:
#         current_order = Order.objects.filter(user=request.user, status='pending').first()

#     if not current_order and request.user.is_authenticated:
#         messages.info(request, "Você precisa ter um carrinho ativo para adicionar este produto. Criando um novo para você.")
#         return redirect('create_order') 
    
#     pizza_borders = product.available_pizza_borders.all().order_by('name')
#     pizza_flavors = product.available_pizza_flavors.all().order_by('name')
#     option_types = product.available_option_types.all().prefetch_related('options').order_by('name')

#     if product.max_flavor_sections:
#         for pizza_flavor in pizza_flavors:
#             pizza_flavor.price = pizza_flavor.price / product.max_flavor_sections 

#     return render(request, 'products/product_detail.html', {
#         'product': product,
#         'order': current_order, # Pode ser None se o usuário não estiver logado
#         'pizza_borders': pizza_borders,
#         'pizza_flavors': pizza_flavors,
#         'option_types': option_types,
#     })

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, active=True)
    promotion = product.get_active_promotion()

    # Detectar se é pizza dinâmica (sem preço fixo e com seções de sabor)
    is_dynamic = product.price == 0 and product.max_flavor_sections and product.max_flavor_sections > 0
    estimated_price = product.get_estimated_base_price_for_display() if is_dynamic else product.price
    discounted_price = product.get_discounted_price() if promotion else None

    # Preparar dados para front-end
    response_data = {
        "id": product.id,
        "name": product.name,
        "category": product.category.name if product.category else '',
        "description": product.description,
        "image": product.image.url if product.image else '',
        "is_dynamic": is_dynamic,
        "estimated_price": float(estimated_price),
        "price": float(product.price),
        "has_promo": promotion is not None,
        "discounted_price": float(discounted_price) if discounted_price else None,
        "promo": {
            "name": promotion.name,
            "discount_value": round(promotion.discount_value, 2),
            "end_date": promotion.end_date.strftime("%d/%m/%Y %H:%M"),
        } if promotion else None,
        "max_flavor_sections": product.max_flavor_sections,
        "pizza_flavors": [],
        "pizza_borders": [],
        "option_types": []
    }

    # Recalcular preço proporcional de sabores, se necessário
    pizza_flavors = product.available_pizza_flavors.all().order_by('name')
    if product.max_flavor_sections:
        for flavor in pizza_flavors:
            flavor_price = flavor.price / product.max_flavor_sections
            response_data["pizza_flavors"].append({
                "id": flavor.id,
                "name": flavor.name,
                "price": round(flavor_price, 2)
            })
    else:
        for flavor in pizza_flavors:
            response_data["pizza_flavors"].append({
                "id": flavor.id,
                "name": flavor.name,
                "price": round(flavor.price, 2)
            })

    # Bordas
    for border in product.available_pizza_borders.all().order_by('name'):
        response_data["pizza_borders"].append({
            "id": border.id,
            "name": border.name,
            "price": float(border.price)
        })

    # Opções agrupadas por tipo
    option_types = product.available_option_types.all().prefetch_related('options').order_by('name')
    for opt_type in option_types:
        options = [{
            "id": opt.id,
            "name": opt.name,
            "price": float(opt.price)
        } for opt in opt_type.options.all()]
        response_data["option_types"].append({
            "id": opt_type.id,
            "name": opt_type.name,
            "options": options
        })

    return JsonResponse(response_data)