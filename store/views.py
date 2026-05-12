from django.views import View
from django.contrib import messages
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from .models import Customer,Product , Order, ProductDetails, Stock
from .forms import CustomerForm, OrderForm, OrderItem, OrderItemForm, OrderItemFormSet
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    DeleteView,
    UpdateView,
)
from django.db.models import Count
from django.utils import timezone
from django.forms import inlineformset_factory


def dashboard(request):
    today = timezone.now().date()
    user_branch = request.user.branch

    todays_orders = Order.objects.filter(
        branch=user_branch, created_at__date=today
    ).order_by("-created_at")

    low_stock = Stock.objects.filter(
        branch=user_branch, location_type="showroom", quantity=0
    )

    top_products = (
        ProductDetails.objects.filter(orderitem__order__branch=user_branch)
        .annotate(order_count=Count("orderitem"))
        .order_by("-order_count")[:1]
    )

    context = {
        "todays_orders": todays_orders,
        "todays_count": todays_orders.count(),
        "low_stock": low_stock,
        "top_products": top_products,
    }
    return render(request, "dashboard.html", context)


class ProductListView(ListView):
    model = Product
    template_name = "products.html"
    context_object_name = "products"


# Order List View
class OrderListView(ListView):
    model = Order
    template_name = "orders/orders.html"
    context_object_name = "orders"


# Create Order
from django.views import View
from django.shortcuts import render, redirect
from django.forms import inlineformset_factory
from django.db import transaction
from django.contrib import messages

from .models import Order, OrderItem
from .forms import OrderForm, OrderItemForm


class OrderCreateView(View):
    template_name = "orders/order_create.html"

    def get_formset(self, data=None):
        OrderItemFormSet = inlineformset_factory(
            Order,
            OrderItem,
            form=OrderItemForm,
            extra=1,
            can_delete=True,
            min_num=1,
            validate_min=True
        )
        return OrderItemFormSet(data=data, prefix="items")

    def get(self, request):
        form = OrderForm()
        formset = self.get_formset()
        return render(request, self.template_name, {"form": form, "formset": formset, "title": "Create New Order"})

    def post(self, request):
        if "add_item" in request.POST:
            post_data = request.POST.copy()
            total_forms = int(post_data.get("items-TOTAL_FORMS", 1))
            post_data["items-TOTAL_FORMS"] = str(total_forms + 1)
            form = OrderForm(post_data)
            formset = self.get_formset(data=post_data)
            return render(request, self.template_name, {"form": form, "formset": formset, "title": "Create New Order"})

        form = OrderForm(request.POST)
        formset = self.get_formset(data=request.POST)

        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    order = form.save(commit=False)
                    order.branch = request.user.branch
                    order.created_by = request.user
                    order.save()

                    formset.instance = order
                    formset.save()

                    order.total_amount = sum(item.total_price for item in order.items.all())
                    order.save(update_fields=["total_amount"])

                messages.success(request, f"Order #{order.id} created successfully.")
                return redirect("order_list")

            except Exception as e:
                messages.error(request, f"Error: {e}")

        return render(request, self.template_name, {"form": form, "formset": formset, "title": "Create New Order"})


# Order Update
class OrderUpdateView(UpdateView):
    model = Order
    form_class = OrderForm
    template_name = "orders/order_create.html"
    success_url = "/orders/"
    pk_url_kwarg = "pk"


# Order Delete
class OrderDeleteView(DeleteView):
    model = Order
    template_name = "orders/order_detail.html"
    success_url = "/orders/"
    pk_url_kwarg = "pk"


# Order Detail
class OrderDetailView(DetailView):
    model = Order
    template_name = "orders/order_detail.html"
    context_object_name = "order"
    pk_url_kwarg = "pk"


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
    if request.method == "POST":
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.email = request.POST.get("email")
        if hasattr(user, "branch"):
            user.branch = request.POST.get("branch")
        user.save()
        return redirect("profile_view")

    return render(request, "profile.html")


class ProductDetailView(DetailView):
    model = ProductDetails
    template_name = "products/product_detail.html"
    context_object_name = "product"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["stocks"] = self.object.stock_set.all()
        context["variants"] = ProductDetails.objects.filter(product=self.object.product)
        return context
