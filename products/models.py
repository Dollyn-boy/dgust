from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    description = models.TextField(max_length=300, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    active = models.BooleanField(default=True)
    
    # Novos campos ManyToMany para associar opções diretamente ao produto
    available_pizza_borders = models.ManyToManyField('PizzaBorder', blank=True, related_name='products_with_this_border')
    available_pizza_flavors = models.ManyToManyField('PizzaFlavor', blank=True, related_name='products_with_this_flavor')
    available_option_types = models.ManyToManyField('OptionType', blank=True, related_name='products_with_this_option_type') 
    max_flavors = models.PositiveIntegerField(null=True, blank=True, help_text="Número máximo de seções de sabor para pizzas (ex: 2 para meio a meio, 4 para quatro sabores). Deixe em branco para produtos não-pizza.")
    

    def __str__(self):
        return f"{self.name} ({self.category.name})"
    
class PizzaBorder(models.Model):
    name = models.CharField(max_length=30)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.name}"


class PizzaFlavor(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField(max_length=300, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.name}"


class OptionType(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.name}"

    
class Option(models.Model):
    type = models.ForeignKey(OptionType, related_name="options", on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    description = models.TextField(max_length=300, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.name}"
