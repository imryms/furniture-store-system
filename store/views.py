from django.shortcuts import render
from .models import Product
from .models import Order
from django.shortcuts import render, redirect, get_object_or_404
from .models import Customer, Order, ProductDetails, Stock
from .forms import CustomerForm
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    DeleteView,
    UpdateView,
)
from django.db.models import Count


def dashboard(request):
    today = timezone.now().date()
    user_branch = request.user.branch

    todays_orders = Order.objects.filter(
        branch = user_branch,
        created_at__date =today
    ).order_by('-created_at')

    low_stock = Stock.objects.filter(
        branch=user_branch,
        location_type = 'showroom',
        quantity=0
    )

    top_products = ProductDetails.objects.filter(
        orderitem__order__branch=user_branch
    ).annotate(
        order_count = Count('orderitem')
    ).order_by('-order_count')[:3]

    context = {
        'todays_orders':todays_orders,
        'todays_count': todays_orders.count(),
        'low_stock': low_stock,
        'top_products':top_products,
    }
    return render(request, 'dashboard.html', context)



class ProductListView(ListView):
    model = Product
    template_name= "products.html"
    context_object_name = "products"


class OrderListView(ListView):
    model = Order
    template_name= "orders/orders.html"
    context_object_name = "orders"


def customer_list(request):
    return render(request, "customers/customer_list.html")


# Search - List Customer
def customer_list(request):
    search_query = request.GET.get("search", "")
    if search_query:
        customers = Customer.objects.filter(
            name__icontains=search_query
        ) | Customer.objects.filter(phone__icontains=search_query)
    else:
        customers = Customer.objects.all()
    return render(
        request,
        "customers/customer_list.html",
        {"customers": customers, "query": search_query},
    )


# 2. Add Customer
def customer_create(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("customer_list")
    else:
        form = CustomerForm()
    return render(
        request,
        "customers/customer_form.html",
        {"form": form, "title": "Add New Customer"},
    )


# 3. Edit Customer
def customer_update(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == "POST":
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect("customer_list")
    else:
        form = CustomerForm(instance=customer)
    return render(
        request,
        "customers/customer_form.html",
        {"form": form, "title": "Edit Customer"},
    )


# 4. Delete Customer
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == "POST":
        customer.delete()
        return redirect("customer_list")
    return render(
        request, "customers/customer_confirm_delete.html", {"customer": customer}
    )


# 5. Customer Detail
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customer_orders = Order.objects.filter(customer=customer)
    return render(
        request,
        "customers/customer_detail.html",
        {"customer": customer, "orders": customer_orders},
    )


class ProductListView(ListView):
    model = ProductDetails
    template_name = "products/products.html"
    context_object_name = "products"

    def get_queryset(self):
        query = self.request.GET.get("search", "")
        if query:
            return (
                ProductDetails.objects.filter(product__name__icontains=query)
                | ProductDetails.objects.filter(code__icontains=query)
                | ProductDetails.objects.filter(color__icontains=query)
            )
        return ProductDetails.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_branch"] = self.request.user.branch
        context["query"] = self.request.GET.get("search", "")
        return context

from django.contrib.auth.decorators import login_required

@login_required
def profile_view(request):
    user = request.user
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        if hasattr(user, 'branch'):
            user.branch = request.POST.get('branch')
        user.save()
        return redirect('profile_view')

    return render(request, 'profile.html')

class ProductDetailView(DetailView):
    model = ProductDetails
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stocks'] = self.object.stock_set.all()
        context['variants'] = ProductDetails.objects.filter(
            product=self.object.product
        )
        return context
