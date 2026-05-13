from django.views import View
from django.contrib import messages
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from .models import Customer,Product , Order, ProductDetails, Stock
from .forms import CustomerForm, OrderForm, OrderItem, OrderItemForm, OrderItemFormSet
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
from django.forms import inlineformset_factory


#----------------------------------------------------------

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

    def get_queryset(self):
        queryset = Order.objects.all().order_by('-created_at')
        q = self.request.GET.get("q", "").strip()
        if q:
            if "-" in q:
                q = q.split("-")[-1].lstrip("0") or "0"
            queryset = queryset.filter(id__icontains=q)
        return queryset


class OrderCreateView(View):
    template_name = "orders/order_create.html"

    def get_formset(self, data=None):
        OrderItemFormSet = inlineformset_factory(
            Order,
            OrderItem,
            form=OrderItemForm,
            extra=0,
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

                    for item in order.items.all():
                        if item.stock:
                            item.stock.quantity -= item.quantity
                            item.stock.save(update_fields=['quantity'])

                    order.total_amount = sum(item.total_price for item in order.items.all())
                    order.save(update_fields=["total_amount"])

                messages.success(request, f"Order #{order.id} created successfully.")
                return redirect("order_list")

            except Exception as e:
                messages.error(request, f"Error: {e}")

        return render(request, self.template_name, {"form": form, "formset": formset, "title": "Create New Order"})


# Order Update
class OrderUpdateView(View):
    template_name = "orders/order_create.html"

    def get_formset(self, data=None, instance=None):
        OrderItemFormSet = inlineformset_factory(
            Order,
            OrderItem,
            form=OrderItemForm,
            extra=0,
            can_delete=True,
            min_num=1,
            validate_min=True
        )
        return OrderItemFormSet(data=data, instance=instance, prefix="items")

    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        form = OrderForm(instance=order)
        customer_form = CustomerForm(instance=order.customer)
        formset = self.get_formset(instance=order)
        return render(request, self.template_name, {
            "form": form,
            "customer_form": customer_form,
            "formset": formset,
            "order": order,
            "title": f"Update Order #{order.id}",
            "submit_label": "Save Changes",
        })

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)

        if "add_item" in request.POST:
            post_data = request.POST.copy()
            total_forms = int(post_data.get("items-TOTAL_FORMS", 1))
            post_data["items-TOTAL_FORMS"] = str(total_forms + 1)
            form = OrderForm(post_data, instance=order)
            customer_form = CustomerForm(post_data, instance=order.customer)
            formset = self.get_formset(data=post_data, instance=order)
            return render(request, self.template_name, {
                "form": form,
                "customer_form": customer_form,
                "formset": formset,
                "order": order,
                "title": f"Update Order #{order.id}",
                "submit_label": "Save Changes",
            })

        form = OrderForm(request.POST, instance=order)
        customer_form = CustomerForm(request.POST, instance=order.customer)
        formset = self.get_formset(data=request.POST, instance=order)

        if form.is_valid() and customer_form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    customer_form.save()
                    form.save()
                    formset.save()

                    order.total_amount = sum(item.total_price for item in order.items.all())
                    order.save(update_fields=["total_amount"])

                messages.success(request, f"Order #{order.id} updated successfully.")
                return redirect("order_list")

            except Exception as e:
                messages.error(request, f"Error: {e}")

        return render(request, self.template_name, {
            "form": form,
            "customer_form": customer_form,
            "formset": formset,
            "order": order,
            "title": f"Update Order #{order.id}",
            "submit_label": "Save Changes",
        })


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

from django.db.models import Count, Sum
@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customer_orders = Order.objects.filter(customer=customer).order_by('-created_at')
    total_spent = customer_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    last_order = customer_orders.first()
    context = {
        'customer': customer,
        'orders': customer_orders,
        'total_spent': total_spent,
        'last_order': last_order,
    }

    return render(
        request,
        "customers/customer_detail.html",
        context,
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
