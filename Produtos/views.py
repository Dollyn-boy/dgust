from django.shortcuts import render, get_object_or_404
from Produtos.models import Produto

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

def detalhes_produto(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    return render(request, 'main/detalhes_produto.html', {'produto': produto})