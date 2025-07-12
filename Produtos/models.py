from django.db import models

# Create your models here.
class Produto(models.Model):
    CATEGORIA_CHOICES = [
        ('pizza', 'Pizza'),
        ('bebida', 'Bebida'),
        ('sobremesa', 'Sobremesa'),
        ('petisco', 'Petisco')
        # adicione mais conforme necessário
    ]

    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    preco = models.DecimalField(max_digits=6, decimal_places=2)
    imagem = models.ImageField(upload_to='produtos/', blank=True, null=True)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES, default='pizza')

    def __str__(self):
        return self.nome

class Sabor(models.Model):
    nome = models.CharField(max_length=100)
    preco_extra = models.DecimalField(max_digits=5, decimal_places=2, default=0) 
    descricao = models.TextField(blank=True)

    def __str__(self):
        return self.nome

class Borda(models.Model):
    nome = models.CharField(max_length=100)
    preco_extra = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def __str__(self):
        return self.nome

class Pizza(Produto):
    max_sabores = models.PositiveIntegerField(default=1)
    sabores_disponiveis = models.ManyToManyField(Sabor)
    bordas_disponiveis = models.ManyToManyField(Borda, blank=True)
