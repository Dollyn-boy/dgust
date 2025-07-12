from django.db import models
from Produtos.models import Produto, Sabor, Borda
# Create your models here.

class Pedido(models.Model):
    data_pedido = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='Em andamento')  # pode ser 'Em andamento', 'Concluído', etc.

    def __str__(self):
        return f"Pedido #{self.id} - {self.status}"

    def valor_total(self):
        return sum(item.preco_total() for item in self.itens.all())


class ItemCarrinho(models.Model):
    #carrinho = models.ForeignKey(Carrinho, related_name='itens', on_delete=models.CASCADE)
    pedido = models.ForeignKey(Pedido, related_name='itens', on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)
    preco_unitario = models.DecimalField(max_digits=6, decimal_places=2)  # guarda preço na hora da adição
    observacao = models.TextField(blank=True)

    # só se for pizza:
    sabores = models.ManyToManyField(Sabor, blank=True)
    borda = models.ForeignKey(Borda, null=True, blank=True, on_delete=models.SET_NULL)

    def preco_total(self):
        return self.quantidade * self.preco_unitario

    def __str__(self):
        return f"{self.quantidade} x {self.produto.nome} (Carrinho {self.carrinho.id})"
