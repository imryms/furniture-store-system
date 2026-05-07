from django.shortcuts import render
from .models import ProductDetails
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView


def dashboard(request):
    return render(request, 'dashboard.html')


class ProductListView(ListView):
    model = ProductDetails
    template_name = 'products/products.html'
    context_object_name = 'products'

    def get_queryset(self):
        query = self.request.GET.get('search', '')
        if query:
            return ProductDetails.objects.filter(
                product__name__icontains=query
            ) | ProductDetails.objects.filter(
                code__icontains=query
            ) | ProductDetails.objects.filter(
                color__icontains=query
            )
        return ProductDetails.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_branch'] = self.request.user.branch
        context['query'] = self.request.GET.get('search', '')
        return context
