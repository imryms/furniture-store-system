from django.shortcuts import render
from .models import Product
from .models import Order
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView


def dashboard(request):
    return render(request, 'dashboard.html')

class ProductListView(ListView):
    model = Product
    template_name: 'products.html'
    context_object_name= 'products'


class OrderListView(ListView):
    model = Order
    template_name: 'orders/orders.html'
    context_object_name = 'orders'

