from django.db import models
from ..Produtos.models import Produtos

# Create your models here.

class Promocao(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    desconto_percentual = models.FloatField()
    produtos = models.ManyToManyField(Produtos, blank=True)
    data_inicio = models.DateTimeField()
    data_fim = models.DateTimeField()

    def __str__(self):
        return self.nome