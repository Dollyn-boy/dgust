from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse # Importe HttpResponse se for usá-lo em algum lugar
from orders.models import Order, OrderItem

# O decorador @login_required foi removido desta view
def home(request):
    return render(request, 'core/base.html')