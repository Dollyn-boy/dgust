from django.shortcuts import render
from django.shortcuts import render, get_list_or_404
from Produtos.models import Produto

def home(request):
    produtos = get_list_or_404(Produto)[:9]
    return render(request,'shared/home.html', {'produtos': produtos})