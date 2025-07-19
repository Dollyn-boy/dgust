from django.db import models
from products.models import Product

class Combo(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=300, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00) 
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class ComboItem(models.Model):
    combo = models.ForeignKey(Combo, on_delete=models.CASCADE, related_name='combo_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='is_part_of_combos')
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('combo', 'product')

    def __str__(self):
        return f"{self.quantity}x {self.product.name} em {self.combo.name}"