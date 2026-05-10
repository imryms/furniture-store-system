from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Branch,
    User,
    Product,
    ProductDetails,
    Stock,
    Customer,
    Order,
    OrderItem,
    Category
)

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Branch Info', {'fields': ('branch',)}),
    )


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'branch', 'status', 'total_amount', 'created_at')
    inlines = [OrderItemInline]


class ProductDetailsInline(admin.TabularInline):
    model = ProductDetails
    extra = 1


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')
    inlines = [ProductDetailsInline]


class StockAdmin(admin.ModelAdmin):
    list_display = ('product_details', 'branch', 'quantity', 'location_type')


admin.site.register(Branch)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductDetails)
admin.site.register(Stock, StockAdmin)
admin.site.register(Customer)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(Category)

