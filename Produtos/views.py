from django.shortcuts import render, get_object_or_404
from Produtos.models import Produto, Pizza
from django.http import Http404, JsonResponse

# Create your views here.
def listar_produto(request):
    produtos = Produto.objects.all()
    
    categorias = [
    ('pizza', 'Pizzas'),
    ('bebida', 'Bebidas'),
    ('sobremesa', 'Sobremesas'),
    ]
    
    context = {
        'produtos': produtos,
        'categorias': categorias,
    }
    return render(request, 'cardapio.html', context)

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

def detalhes_produto(request, produto_id):
    produto = Produto.objects.get(id=produto_id)
    return render(request, 'produto.html', {'produto': produto})