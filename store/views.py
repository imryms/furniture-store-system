from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    DeleteView,
    UpdateView,
)
from django.db.models import Count
from django.utils import timezone
from .models import Customer, Order, ProductDetails, Stock, Product
from .forms import CustomerForm, OrderForm

# Dashboard
@login_required
def dashboard(request):
    today = timezone.now().date()
    user_branch = request.user.branch

    todays_orders = Order.objects.filter(
        branch=user_branch,
        created_at__date=today
    ).order_by('-created_at')

    low_stock = Stock.objects.filter(
        branch=user_branch,
        location_type='showroom',
        quantity=0
    )

    top_products = ProductDetails.objects.filter(
        orderitem__order__branch=user_branch
    ).annotate(
        order_count=Count('orderitem')
    ).order_by('-order_count')[:1]

    context = {
        'todays_orders': todays_orders,
        'todays_count': todays_orders.count(),
        'low_stock': low_stock,
        'top_products': top_products,
    }
    return render(request, 'dashboard.html', context)


# Order
class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "orders/orders.html"
    context_object_name = "orders"


class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'orders/order_create.html'
    success_url = '/orders/'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.branch = self.request.user.branch
        return super().form_valid(form)


class OrderUpdateView(LoginRequiredMixin, UpdateView):
    model = Order
    form_class = OrderForm
    template_name = 'orders/order_create.html'
    success_url = '/orders/'
    pk_url_kwarg = 'pk'


class OrderDeleteView(LoginRequiredMixin, DeleteView):
    model = Order
    template_name = 'orders/order_detail.html'
    success_url = '/orders/'
    pk_url_kwarg = 'pk'


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'
    pk_url_kwarg = 'pk'


# Customer
@login_required
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


@login_required
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


@login_required
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


@login_required
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == "POST":
        customer.delete()
        return redirect("customer_list")
    return render(
        request, "customers/customer_confirm_delete.html", {"customer": customer}
    )


@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customer_orders = Order.objects.filter(customer=customer)
    return render(
        request,
        "customers/customer_detail.html",
        {"customer": customer, "orders": customer_orders},
    )


# Product
class ProductListView(LoginRequiredMixin, ListView):
    model = ProductDetails
    template_name = "products/products.html"
    context_object_name = "products"

    def get_queryset(self):
        queryset = ProductDetails.objects.all()

        query = self.request.GET.get("search", "")
        color = self.request.GET.get("color", "")
        category = self.request.GET.get("category", "")

        if query:
            queryset = queryset.filter(
                product__name__icontains=query
            ) | queryset.filter(
                code__icontains=query
            )

        if color:
            queryset = queryset.filter(color__icontains=color)

        if category:
            queryset = queryset.filter(product__category__id=category)

        stock_filter = self.request.GET.get("stock", "")

        if stock_filter == "available":
            queryset = queryset.filter(
            stock__branch=self.request.user.branch,
            stock__location_type='showroom',
            stock__quantity__gt=0
        ).distinct()

        elif stock_filter == "out_of_stock":
            queryset = queryset.filter(
                stock__branch=self.request.user.branch,
                stock__location_type='showroom',
                stock__quantity=0
            ).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_branch"] = self.request.user.branch
        context["query"] = self.request.GET.get("search", "")
        context["selected_color"] = self.request.GET.get("color", "")
        context["selected_category"] = self.request.GET.get("category", "")
        context["colors"] = ProductDetails.objects.values_list("color", flat=True).distinct()
        context["selected_stock"] = self.request.GET.get("stock", "")
        from .models import Category
        context["categories"] = Category.objects.all()
        return context


class ProductDetailView(LoginRequiredMixin, DetailView):
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


# Profile
@login_required
def profile_view(request):
    user = request.user
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.save()
        return redirect('profile_view')

    return render(request, 'profile.html', {'user': user})
