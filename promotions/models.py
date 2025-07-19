from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone # Importe timezone

# Create your models here.
# --- Modelo Promotion (ATUALIZADO) ---
class Promotion(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Porcentagem'),
        # REMOVIDO: ('fixed_amount', 'Valor Fixo'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        validators=[MinValueValidator(0)],
        help_text="Valor do desconto (ex: 10 para 10%)." # Atualizado a descrição
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    active = models.BooleanField(default=True, help_text="Marque para ativar a promoção.")

    def __str__(self):
        return self.name

    def is_active(self):
        now = timezone.now()
        return self.active and self.start_date <= now and self.end_date >= now

    class Meta:
        ordering = ['-start_date']