from django.contrib import admin
from .models import Produto
from .models import Pizza, Sabor, Borda
# Register your models here.

admin.site.register(Produto)
admin.site.register(Pizza)
admin.site.register(Sabor)
admin.site.register(Borda)