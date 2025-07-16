from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem
from products.models import Product, PizzaBorder, PizzaFlavor, Option

# Create your views here.
@login_required
def create_order(request):
    if request.method == 'POST':
        existing_order = Order.objects.filter(user=request.user, status='pending').first()

        if existing_order:
            messages.info(request, "Você já tem um pedido ativo. Continue suas compras ou finalize o pedido atual.")
            return redirect('view_order', order_id=existing_order.id)
        else:
            try:
                new_order = Order.objects.create(user=request.user, total=0.00, status='pending')
                messages.success(request, "Um novo carrinho de compras foi criado para você!")
                return redirect('view_order', order_id=new_order.id)
                
            except Exception as e:
                messages.error(request, f"Ocorreu um erro ao criar o pedido: {e}")
                return redirect('home') # Ou para uma página de erro

    existing_order = Order.objects.filter(user=request.user, status='pending').first()
    if existing_order:
        return redirect('view_order', order_id=existing_order.id)
    else:
        return render(request, 'orders/create_order.html') # Crie este template se necessário
    

def remove_item_from_order(request, order_id, item_id):
    order = get_object_or_404(Order, id=order_id, user=request.user, status='pending')

    if request.method == 'POST':
        try:
            item = get_object_or_404(OrderItem, id=item_id, order=order)

            item.delete()

            order.total = sum(i.price for i in order.items.all())
            order.save()

            messages.success(request, "Item removido com sucesso!")
            return redirect('view_order', order_id=order.id)

        except (OrderItem.DoesNotExist, ValueError) as e:
            messages.error(request, f"Erro ao remover item: {e}")
            return redirect('view_order', order_id=order.id)
        except Exception as e:
            messages.error(request, f"Ocorreu um erro inesperado: {e}")
            return redirect('view_order', order_id=order.id)

    messages.error(request, "Método não permitido para remover item. Use POST.")
    return redirect('view_order', order_id=order.id)


@login_required
def add_item_to_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user, status='pending')

    if request.method == 'POST':
        try:
            product_id = request.POST.get('product_id')
            quantity = int(request.POST.get('quantity', 1))
            pizza_border_id = request.POST.get('pizza_border_id')
            pizza_flavor_ids = request.POST.getlist('pizza_flavor_ids')
            option_ids = request.POST.getlist('option_ids')

            if not product_id or quantity <= 0:
                messages.error(request, "ID do produto e quantidade são obrigatórios e devem ser válidos.")
                return redirect('product_detail', product_id=product_id)

            product = get_object_or_404(Product, id=product_id, active=True)

            # Preço base
            item_price = product.price * quantity

            # Borda
            pizza_border = None
            if pizza_border_id:
                pizza_border = get_object_or_404(PizzaBorder, id=pizza_border_id)
                item_price += pizza_border.price * quantity

            # Sabores
            flavors_to_add = []
            if pizza_flavor_ids:
                for flavor_id in pizza_flavor_ids:
                    flavor = get_object_or_404(PizzaFlavor, id=flavor_id)
                    flavors_to_add.append(flavor)
                    # Dividir preço por número máximo de sabores, se definido
                    if product.max_flavors:
                        item_price += (flavor.price / product.max_flavors) * quantity
                    else:
                        item_price += flavor.price * quantity

            # Opções genéricas
            options_to_add = []
            if option_ids:
                for option_id in option_ids:
                    option = get_object_or_404(Option, id=option_id)
                    options_to_add.append(option)
                    item_price += option.price * quantity

            # Cria SEM verificar se já existe
            order_item = OrderItem.objects.create(
                order=order,
                product=product,
                pizza_border=pizza_border,
                quantity=quantity,
                price=item_price
            )

            # ManyToMany devem ser adicionados após criar
            if flavors_to_add:
                order_item.pizza_flavors.add(*flavors_to_add)
            if options_to_add:
                order_item.options.add(*options_to_add)

            # Atualizar total do pedido
            order.total = sum(item.price for item in order.items.all())
            order.save()

            messages.success(request, f"'{product.name}' adicionado ao carrinho com sucesso!")
            return redirect('product_detail', product_id=product_id)

        except (ValueError, Product.DoesNotExist, PizzaBorder.DoesNotExist,
                PizzaFlavor.DoesNotExist, Option.DoesNotExist) as e:
            messages.error(request, f"Erro ao adicionar item: {e}")
            return redirect('product_detail', product_id=product_id)
        except Exception as e:
            messages.error(request, f"Ocorreu um erro inesperado: {e}")
            return redirect('product_detail', product_id=product_id)

    messages.error(request, "Método não permitido para adicionar item. Use POST.")
    return redirect('product_list')


@login_required
def view_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status != 'pending':
        messages.warning(request, "Este pedido não está mais ativo e não pode ser modificado.")
        return redirect('order_history')

    return render(request, 'orders/view_order.html', {'order': order})

    
@login_required
def complete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if request.method == 'POST':
        if order.status == 'pending':
            order.status = 'completed'
            order.save()
            messages.success(request, "Seu pedido foi finalizado com sucesso!")

            items = get_list_or_404(OrderItem, order=order)

            """
            TODO: Integração com API
            """

            return redirect('create_order')
        else:
            messages.warning(request, "Não é possível completar um pedido que não está pendente.")
            return redirect('view_order', order_id=order.id)

    messages.error(request, "Método não permitido. Use POST para finalizar o pedido.")
    return redirect('view_order', order_id=order.id)
    

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if request.method == 'POST': # Garante que a ação só ocorre via POST
        if order.status == 'pending':
            order.status = 'cancelled'
            order.save()
            messages.info(request, "Seu pedido foi cancelado.")  
            return redirect('create_order')
        else:
            messages.warning(request, "Não é possível cancelar um pedido que não está pendente.")
            return redirect('view_order', order_id=order.id) # Redireciona de volta para o pedido
        
    
    messages.error(request, "Método não permitido para cancelar pedido.")
    return redirect('view_order', order_id=order.id)

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).exclude(status='pending').order_by('-created_at')
    return render(request, 'orders/order_history.html', {'orders': orders})