from django.db import models
from products.models import Product, PizzaBorder, PizzaFlavor, Option # Removido OptionType, pois não é usado diretamente aqui
from django.contrib.auth.models import User

# Seus modelos Category, Product, PizzaBorder, PizzaFlavor, OptionType, Option
# (Assumindo que estão definidos em products.models ou outro arquivo importado)

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pendente'),
        ('completed', 'Concluído'),
        ('cancelled', 'Cancelado'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    # cupom = models.ForeignKey(Cupom, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    class Meta:
        # unique_together = ('user', 'status') # unique_together é menos flexível que UniqueConstraint com condition
        constraints = [
            models.UniqueConstraint(fields=['user'], condition=models.Q(status='pending'), name='unique_pending_order_per_user')
        ]


    def __str__(self):
        return f"Pedido #{self.id} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='order_items')
    pizza_border = models.ForeignKey(PizzaBorder, on_delete=models.SET_NULL, null=True, blank=True, related_name='order_items')
    pizza_flavors = models.ManyToManyField(PizzaFlavor, related_name='order_items', blank=True)
    # promotion = models.ForeignKey(Promotion, on_delete=models.SET_NULL, null=True, blank=True, related_name='order_items') # Assumindo que Promotion existe
    options = models.ManyToManyField(Option, related_name='order_items', blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subitems')
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        # Correção para lidar com product que pode ser None
        product_name = self.product.name if self.product else "Produto Removido"
        return f"{product_name} (Pedido #{self.order.id})"
