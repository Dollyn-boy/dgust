from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone # Importe timezone
from promotions.models import Promotion
import decimal

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='products/', blank=True, null=True) 
    description = models.TextField(max_length=300, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    active = models.BooleanField(default=True)
    
    available_pizza_borders = models.ManyToManyField('PizzaBorder', blank=True, related_name='products_with_this_border')
    available_pizza_flavors = models.ManyToManyField('PizzaFlavor', blank=True, related_name='products_with_this_flavor')
    available_option_types = models.ManyToManyField('OptionType', blank=True, related_name='products_with_this_option_type')
    max_flavor_sections = models.PositiveIntegerField(
        null=True, blank=True, 
        help_text="Número máximo de seções de sabor para pizzas (ex: 2 para meio a meio, 4 para quatro sabores). Deixe em branco para produtos não-pizza."
    )
    
    promotions = models.ManyToManyField(Promotion, blank=True, related_name='products_on_promotion')

    def __str__(self):
        return f"{self.name} ({self.category.name})"

    # Método para obter a promoção ativa (se houver)
    def get_active_promotion(self):
        now = timezone.now()
        return self.promotions.filter(
            start_date__lte=now,
            end_date__gte=now,
            active=True
        ).first()
    
    # NOVO MÉTODO: Calcula um preço estimado base para exibição (sem descontos)
    def get_estimated_base_price_for_display(self):
        """
        Calculates an estimated base price for display purposes,
        especially for pizzas where product.price is 0 and price is based on flavors.
        This price does NOT include promotions or borders.
        """
        if self.price == 0 and self.max_flavor_sections is not None and self.max_flavor_sections > 0:
            estimated_flavor_cost = decimal.Decimal('0.00')
            # Pega os sabores mais baratos até o número máximo de seções
            cheapest_flavors = self.available_pizza_flavors.order_by('price')[:self.max_flavor_sections]
            
            # Soma os preços completos dos sabores.
            for flavor in cheapest_flavors:
                estimated_flavor_cost += flavor.price
            
            # Divide o custo total dos sabores pelo número de seções de sabor para obter o preço por pizza
            if self.max_flavor_sections > 0:
                estimated_flavor_cost = estimated_flavor_cost / decimal.Decimal(str(self.max_flavor_sections)) # Converter para Decimal
            
            return estimated_flavor_cost if estimated_flavor_cost > 0 else decimal.Decimal('0.00')
        
        return self.price # Para produtos não-pizza ou pizzas com preço base > 0

    # Método para obter o preço com desconto (se houver promoção ativa)
    # Sempre retorna um Decimal, calculando um preço estimado para pizzas com preço base 0.
    def get_discounted_price(self):
        # Usa o preço estimado base para o cálculo da promoção, se for pizza com preço 0
        current_price_for_display = self.get_estimated_base_price_for_display()

        active_promotion = self.get_active_promotion()
        if active_promotion:
            if active_promotion.discount_type == 'percentage':
                discount_amount = current_price_for_display * (active_promotion.discount_value / 100)
                current_price_for_display -= discount_amount
            # REMOVIDO: Lógica para 'fixed_amount'
            # elif active_promotion.discount_type == 'fixed_amount':
            #     current_price_for_display = max(decimal.Decimal('0.00'), current_price_for_display - active_promotion.discount_value)
        
        return current_price_for_display

    
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
