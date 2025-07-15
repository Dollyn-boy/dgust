from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
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
    

@login_required
def add_item_to_order(request, order_id):
    """
    Adiciona um item a um pedido existente, incluindo opções de borda, sabores e opções genéricas.
    Após a adição, redireciona o usuário de volta para a página de detalhes do produto.
    """
    order = get_object_or_404(Order, id=order_id, user=request.user, status='pending')

    if request.method == 'POST':
        try:
            product_id = request.POST.get('product_id')
            quantity = int(request.POST.get('quantity', 1))
            pizza_border_id = request.POST.get('pizza_border_id')
            pizza_flavor_ids = request.POST.getlist('pizza_flavor_ids') # Usar getlist para múltiplos valores
            option_ids = request.POST.getlist('option_ids') # Usar getlist para múltiplos valores

            if not product_id or quantity <= 0:
                messages.error(request, "ID do produto e quantidade são obrigatórios e devem ser válidos.")
                return redirect('product_detail', product_id=product_id)
            
            product = get_object_or_404(Product, id=product_id, active=True)

            # Calcular o preço base do item
            item_price = product.price * quantity

            # Adicionar preço da borda
            pizza_border = None
            if pizza_border_id:
                pizza_border = get_object_or_404(PizzaBorder, id=pizza_border_id)
                item_price += pizza_border.price * quantity

            # Criar ou obter o OrderItem
            order_item, created = OrderItem.objects.get_or_create(
                order=order,
                product=product,
                defaults={
                    'quantity': quantity,
                    'price': item_price, # Preço inicial, será ajustado com sabores e opções
                    'pizza_border': pizza_border
                }
            )

            if not created:
                # Se o item já existe, atualize a quantidade e o preço base
                order_item.quantity += quantity
                # Recalcula o preço base do item existente para evitar duplicação de preços de borda/sabor/opção
                # A melhor prática seria remover os sabores/opções antigos e readicionar, ou gerenciar o preço de forma mais granular.
                # Por simplicidade, vamos apenas adicionar o preço do novo conjunto de itens.
                # Para um sistema mais robusto, você precisaria de uma lógica mais complexa aqui.
                order_item.price += (product.price + (pizza_border.price if pizza_border else 0)) * quantity
                order_item.save()
            
            # Adicionar sabores da pizza (Many-to-Many)
            # Limpar sabores e opções existentes se o item não for novo, para evitar duplicação
            if not created:
                order_item.pizza_flavors.clear()
                order_item.options.clear()

            if pizza_flavor_ids:
                flavors_to_add = []
                for flavor_id in pizza_flavor_ids:
                    flavor = get_object_or_404(PizzaFlavor, id=flavor_id)
                    flavors_to_add.append(flavor)
                    # Adicionar o preço do sabor ao preço do item
                    item_price += flavor.price * quantity
                order_item.pizza_flavors.add(*flavors_to_add) # Adiciona múltiplos objetos

            # Adicionar opções genéricas (Many-to-Many)
            if option_ids:
                options_to_add = []
                for option_id in option_ids:
                    option = get_object_or_404(Option, id=option_id)
                    options_to_add.append(option)
                    # Adicionar o preço da opção ao preço do item
                    item_price += option.price * quantity
                order_item.options.add(*options_to_add) # Adiciona múltiplos objetos
            
            # Atualizar o preço final do order_item após adicionar todos os extras
            order_item.price = item_price
            order_item.save()

            # Recalcula o total do pedido
            order.total = sum(item.price for item in order.items.all()) # Soma os preços finais dos itens
            order.save()

            messages.success(request, f"'{product.name}' adicionado ao carrinho com sucesso!")
            return redirect('product_detail', product_id=product_id)
        
        except ValueError:
            messages.error(request, "Quantidade, borda, sabor ou opção inválida fornecida.")
            return redirect('product_detail', product_id=product_id)
        except Product.DoesNotExist:
            messages.error(request, "Produto não encontrado ou inativo.")
            return redirect('product_list') 
        except PizzaBorder.DoesNotExist:
            messages.error(request, "Borda de pizza não encontrada.")
            return redirect('product_detail', product_id=product_id)
        except PizzaFlavor.DoesNotExist:
            messages.error(request, "Sabor de pizza não encontrado.")
            return redirect('product_detail', product_id=product_id)
        except Option.DoesNotExist:
            messages.error(request, "Opção não encontrada.")
            return redirect('product_detail', product_id=product_id)
        except Exception as e:
            messages.error(request, f"Ocorreu um erro ao adicionar o item: {e}")
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
    """
    Finaliza um pedido, mudando seu status para 'completed'.
    Após a conclusão, redireciona o usuário para a tela de iniciar um novo pedido.
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if request.method == 'POST': # Garante que a ação só ocorre via POST
        if order.status == 'pending':
            order.status = 'completed'
            order.save()
            messages.success(request, "Seu pedido foi finalizado com sucesso!")
            # Redireciona para a view 'create_order' para que o usuário possa iniciar um novo pedido
            return redirect('create_order')
        else:
            messages.warning(request, "Não é possível completar um pedido que não está pendente.")
            return redirect('view_order', order_id=order.id) # Redireciona de volta para o pedido
    
    # Se a requisição não for POST (ex: alguém tentar acessar via GET), redireciona
    messages.error(request, "Método não permitido para finalizar pedido.")
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