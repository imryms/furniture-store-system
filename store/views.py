from django.shortcuts import render
from .models import Product
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView


def dashboard(request):
    return render(request, 'dashboard.html')

class ProductListView(ListView):
    model = Product
    template_name: 'products.html'
    context_object_name= 'products'
    

