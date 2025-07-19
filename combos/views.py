from django.shortcuts import render
from .models import Combo, ComboItem
from orders.models import Order
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

def combo_list(request):
    combos = Combo.objects.filter(active=True).order_by('name')

    current_order = None
    if request.user.is_authenticated:
        current_order = Order.objects.filter(user=request.user, status='pending').first()

    if not current_order and request.user.is_authenticated:
        messages.info(request, "Você precisa ter um carrinho ativo para adicionar combos. Criando um novo para você.")
        return redirect('create_order')
    
    return render(request, 'combos/combo_list.html', {
        'combos': combos,
        'order': current_order
    })


def combo_detail(request, combo_id):
    combo = get_object_or_404(Combo, id=combo_id, active=True)
    combo_items = combo.combo_items.all().select_related('product') # Busca os itens do combo

    current_order = None
    if request.user.is_authenticated:
        current_order = Order.objects.filter(user=request.user, status='pending').first()

    if not current_order and request.user.is_authenticated:
        messages.info(request, "Você precisa ter um carrinho ativo para adicionar este combo. Criando um novo para você.")
        return redirect('create_order') 
    
    return render(request, 'combos/combo_detail.html', { # NOVO TEMPLATE
        'combo': combo,
        'combo_items': combo_items,
        'order': current_order,
    })