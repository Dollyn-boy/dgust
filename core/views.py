from django.shortcuts import render,get_object_or_404, get_list_or_404
from Pedidos.models import ItemCarrinho, Pedido
from Produtos.models import Produto, Pizza, Borda, Sabor
from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST


# Create your views here.
def listar_produto(request):
    produtos = Produto.objects.all()
    
    categorias = [
    ('pizza', 'Pizzas'),
    ('bebida', 'Bebidas'),
    ('sobremesa', 'Sobremesas'),
    ('petisco', 'Petisco')
    ]
    
    context = {
        'produtos': produtos,
        'categorias': categorias,
    }
    return render(request, 'shared/home.html', context)

@require_POST
def comprar(request):
    pedido_id = 1

    produto_id = request.POST.get('produto_id')
    preco_final = request.POST.get('preco_final')
    quantidade = request.POST.get('quantidade')
    observacao = request.POST.get('observacao', '')

    sabores = request.POST.get('sabores_selecionados')  # ex: "1,3,5"
    borda_id = request.POST.get('borda_selecionada')

    # Validações básicas
    try:
        produto = get_object_or_404(Produto, pk=produto_id)
        quantidade = int(quantidade)
        preco_final = float(preco_final)
    except Exception as e:
        return JsonResponse({'error': 'Dados inválidos: ' + str(e)}, status=400)

    sabores_list = []
    if sabores:
        try:
            sabores_list = [int(s) for s in sabores.split(',') if s.strip()]
        except:
            return JsonResponse({'error': 'Sabores inválidos'}, status=400)

    borda_obj = None
    if borda_id:
        try:
            borda_obj = Borda.objects.get(pk=borda_id)
        except Borda.DoesNotExist:
            return JsonResponse({'error': 'Borda inválida'}, status=400)

    pedido = Pedido.objects.get(pk=pedido_id, status='Em andamento')
            
    itens_pedido = pedido.itens.filter(produto=produto)

    item_existente = None
    for item in itens_pedido:
        sabores_ids = list(item.sabores.values_list('id', flat=True))
        if borda_obj == item.borda and sorted(sabores_list) == sorted(sabores_ids):
            item_existente = item
            break

    if quantidade <= 0:
        if item_existente:
            item_existente.delete()
        return JsonResponse({
            'mensagem': 'Item removido do pedido',
            'pedido_id': pedido_id,
        })

    if item_existente:
        item_existente.quantidade = quantidade
        item_existente.preco_unitario = preco_final
        item_existente.observacao = observacao
        item_existente.save()
        item_existente.sabores.set(sabores_list)
    else:
        item_novo = ItemCarrinho.objects.create(
            pedido=pedido,
            produto=produto,
            quantidade=quantidade,
            preco_unitario=preco_final,
            observacao=observacao,
            borda=borda_obj
        )
        if sabores_list:
            item_novo.sabores.set(sabores_list)

    valor_total = pedido.valor_total()

    return redirect('listar_produtos')

def detalhes_pizza_json(request, pizza_id):
    try: 
        pizza = get_object_or_404(Pizza, id=pizza_id)
        data = {
            'nome' : pizza.nome,
            'descricao' : pizza.descricao,
            'preco' : pizza.preco,
            'imagem_url' : pizza.imagem.url if pizza.imagem else '',
            'max_sabores' : pizza.max_sabores,
            'sabores' : list(
                pizza.sabores_disponiveis.values('id', 'nome', 'descricao', 'preco_extra')
            )
,
            'bordas': list(
                pizza.bordas_disponiveis.values('id', 'nome', 'preco_extra')
            )

        }


        return JsonResponse(data)

    except Pizza.DoesNotExist:
        return Http404
    
def detalhes_produto_json(request, product_id):
    try: 
        produto = get_object_or_404(Produto, id=product_id)
        data = {
            'nome' : produto.nome,
            'descricao' : produto.descricao,
            'preco' : produto.preco,
            'imagem_url' : produto.imagem.url if produto.imagem else '',
        }


        return JsonResponse(data)
    
    except Produto.DoesNotExist:
        return Http404
    

@require_POST
def deletar_item_carrinho(request, item_id):
    print("chegou")
    try:
        item = ItemCarrinho.objects.get(pk=item_id)
        item.delete()
        return JsonResponse({'success': True})
    except ItemCarrinho.DoesNotExist:
        return JsonResponse({'error': 'Item não encontrado'}, status=404)

def detalhes_carrinho_json(request):
    try:
        pedido = Pedido.objects.get(pk=1, status='Em andamento')
    except Pedido.DoesNotExist:
        return JsonResponse({'error': 'Pedido não encontrado'}, status=404)

    itens = []
    for item in pedido.itens.all():
        itens.append({
            'id':item.id,
            'produto_id': item.produto.id,
            'produto_nome': item.produto.nome,
            'quantidade': item.quantidade,
            'preco_unitario': float(item.preco_unitario),
            'preco_total': float(item.preco_total()),
            'observacao': item.observacao,
            'sabores': list(item.sabores.values('id', 'nome')),
            'borda': {
                'id': item.borda.id,
                'nome': item.borda.nome,
                'preco_extra': float(item.borda.preco_extra)
            } if item.borda else None,
        })

    data = {
        'data' : pedido.data_pedido,
        'valor_total': float(pedido.valor_total()),
        'itens': itens
    }

    return JsonResponse(data)