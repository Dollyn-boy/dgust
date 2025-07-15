from django.contrib import admin
from .models import Category,Product, PizzaBorder,PizzaFlavor, Option,OptionType

# Register your models here.
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(PizzaBorder)
admin.site.register(PizzaFlavor)
admin.site.register(Option)
admin.site.register(OptionType)