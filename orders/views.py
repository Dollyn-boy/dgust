from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem
from combos.models import Combo, ComboItem
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
    """
    Adiciona um item (Produto ou Combo) a um pedido existente.
    Após a adição, redireciona o usuário de volta para a página de detalhes do item.
    """
    order = get_object_or_404(Order, id=order_id, user=request.user, status='pending')

    if request.method == 'POST':
        item_type = request.POST.get('item_type') # 'product' ou 'combo'
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity', 1))
        observation = request.POST.get('observation', '').strip()

        if not item_id or quantity <= 0:
            messages.error(request, "ID do item e quantidade são obrigatórios e devem ser válidos.")
            return redirect('product_list') # Redireciona para a lista de produtos como fallback

        try:
            if item_type == 'product':
                product = get_object_or_404(Product, id=item_id, active=True)
                combo = None # Garante que combo é None para produtos
                active_promotion = product.get_active_promotion()

                pizza_border_id = request.POST.get('pizza_border_id')
                pizza_flavor_ids = request.POST.getlist('pizza_flavor_ids')
                number_of_flavor_sections = int(request.POST.get('number_of_flavor_sections', 1))

                option_ids = []
                for key in request.POST:
                    if key.startswith('option_type_'):
                        option_id = request.POST.get(key)
                        if option_id:
                            option_ids.append(option_id)
                
                # Validações para produtos normais
                if product.max_flavor_sections:
                    if number_of_flavor_sections <= 0 or number_of_flavor_sections > product.max_flavor_sections:
                        messages.error(request, f"Número de seções de sabor inválido para este produto. Máximo permitido: {product.max_flavor_sections}.")
                        return redirect('product_detail', product_id=product.id)
                    if pizza_flavor_ids and len(pizza_flavor_ids) > number_of_flavor_sections:
                        messages.error(request, f"Você selecionou mais sabores ({len(pizza_flavor_ids)}) do que o número de seções permitido ({number_of_flavor_sections}).")
                        return redirect('product_detail', product_id=product.id)
                    if product.max_flavor_sections > 1 and number_of_flavor_sections > 1 and not pizza_flavor_ids:
                        messages.error(request, "Você deve selecionar pelo menos um sabor para pizzas com múltiplos sabores.")
                        return redirect('product_detail', product_id=product.id)

                current_item_price = product.price * quantity

                pizza_border = None
                if pizza_border_id:
                    pizza_border = get_object_or_404(PizzaBorder, id=pizza_border_id)
                    current_item_price += pizza_border.price * quantity

                total_flavors_price = 0
                selected_flavors = []
                if pizza_flavor_ids:
                    for flavor_id in pizza_flavor_ids:
                        flavor = get_object_or_404(PizzaFlavor, id=flavor_id)
                        selected_flavors.append(flavor)
                        # A divisão por seção ocorre aqui no cálculo do preço do item
                        total_flavors_price += (flavor.price / number_of_flavor_sections) * quantity
                current_item_price += total_flavors_price

                selected_options = []
                for option_id in option_ids:
                    option = get_object_or_404(Option, id=option_id)
                    selected_options.append(option)
                    current_item_price += option.price * quantity

                # NOVO: Aplicar desconto da promoção ao preço do item (apenas porcentagem)
                if active_promotion:
                    # Como só há promoção por porcentagem agora
                    discount_amount = current_item_price * (active_promotion.discount_value / 100)
                    current_item_price -= discount_amount
                
                order_item = OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=current_item_price,
                    pizza_border=pizza_border,
                    applied_promotion=active_promotion, # Salvar a promoção aplicada
                    observation=observation
                )

                order_item.pizza_flavors.set(selected_flavors)
                order_item.options.set(selected_options)

                # 🔧 Atualiza o total do pedido após adicionar item
                order.total = sum(item.price for item in order.items.all())
                order.save()

                messages.success(request, f"'{product.name}' adicionado ao carrinho com sucesso!")
                return redirect('product_detail', product_id=product.id)

            elif item_type == 'combo':
                combo = get_object_or_404(Combo, id=item_id, active=True)
                product = None # Garante que product é None para combos

                # Calcular o preço do combo com base nos seus itens e desconto
                final_combo_price_per_unit = combo.price 
                
                current_item_price = final_combo_price_per_unit * quantity

                order_item = OrderItem.objects.create(
                    order=order,
                    combo=combo, 
                    quantity=quantity,
                    price=current_item_price,
                    pizza_border=None,
                    applied_promotion=None, # Promoções de produto não se aplicam a combos aqui
                    observation=observation
                )

                # 🔧 Atualiza o total do pedido após adicionar combo
                order.total = sum(item.price for item in order.items.all())
                order.save()
                messages.success(request, f"Combo '{combo.name}' adicionado ao carrinho com sucesso!")
                return redirect('combo_detail', combo_id=combo.id) 

            else:
                messages.error(request, "Tipo de item inválido.")
                return redirect('product_list')

        except ValueError:
            messages.error(request, "Dados de entrada inválidos (quantidade, borda, sabor ou opção).")
            if item_type == 'product':
                return redirect('product_detail', product_id=item_id)
            elif item_type == 'combo':
                return redirect('combo_detail', combo_id=item_id)
            return redirect('product_list')
        except Product.DoesNotExist:
            messages.error(request, "Produto não encontrado ou inativo.")
            return redirect('product_list') 
        except PizzaBorder.DoesNotExist:
            messages.error(request, "Borda de pizza não encontrada.")
            return redirect('product_detail', product_id=item_id)
        except PizzaFlavor.DoesNotExist:
            messages.error(request, "Sabor de pizza não encontrado.")
            return redirect('product_detail', product_id=item_id)
        except Option.DoesNotExist:
            messages.error(request, "Opção não encontrada.")
            return redirect('product_detail', product_id=item_id)
        except Combo.DoesNotExist:
            messages.error(request, "Combo não encontrado ou inativo.")
            return redirect('product_list')
        except Exception as e:
            messages.error(request, f"Ocorreu um erro ao adicionar o item: {e}")
            if item_type == 'product':
                return redirect('product_detail', product_id=item_id)
            elif item_type == 'combo':
                return redirect('combo_detail', combo_id=item_id)
            return redirect('product_list')
    
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

            # 🔍 Recupera e imprime todos os pedidos do usuário
            all_orders = Order.objects.filter(user=request.user).prefetch_related('items', 'items__product', 'items__combo')
            for o in all_orders:
                print(f"\n=== Pedido #{o.id} ===")
                print(f"Status: {o.status}")
                print(f"Criado em: {o.created_at}")
                print(f"Atualizado em: {o.updated_at}")
                print(f"Total: R$ {o.total:.2f}")
                
                for item in o.items.all():
                    if item.product:
                        print(f" - Produto: {item.product.name}")
                        print(f"   Quantidade: {item.quantity}")
                        print(f"   Preço: R$ {item.price:.2f}")
                        print(f"   Observação: {item.observation}")
                        # Se for pizza, mostrar sabores, borda e opções
                        if item.product.category.name == 'Pizza':
                            if item.pizza_border:
                                print(f"   Borda: {item.pizza_border.name}")
                            flavors = ", ".join([f.name for f in item.pizza_flavors.all()])
                            print(f"   Sabores: {flavors}")
                        options = ", ".join([opt.name for opt in item.options.all()])
                        print(f"   Opções: {options}")
                    elif item.combo:
                        print(f" - Combo: {item.combo.name}")
                        print(f"   Quantidade: {item.quantity}")
                        print(f"   Preço: R$ {item.price:.2f}")
                        print(f"   Observação: {item.observation}")
                        # Listar itens do combo, se desejar
                        combo_items = item.combo.combo_items.all()
                        for ci in combo_items:
                            print(f"     • {ci.quantity}× {ci.product.name}")
                    else:
                        print(f" - Item desconhecido")

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