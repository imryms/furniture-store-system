from django.urls import path
from . import views
from .views import ProductListView, ProductDetailView

urlpatterns = [
    path("", views.dashboard),
    path("products", ProductListView.as_view()),
    path("", views.dashboard, name="dashboard"),
    path("customers/", views.customer_list, name="customer_list"),
    path("customers/add/", views.customer_create, name="customer_create"),
    path("customers/edit/<int:pk>/", views.customer_update, name="customer_update"),
    path("customers/delete/<int:pk>/", views.customer_delete, name="customer_delete"),
    path("customers/<int:pk>/", views.customer_detail, name="customer_detail"),
    path("products/", ProductListView.as_view()),

    #Orders
    path("orders/", views.OrderListView.as_view(),name='order_list'),
    path("orders/create/", views.OrderCreateView.as_view(), name="order_create"),
    path("orders/details/<int:pk>/", views.OrderDetailView.as_view(), name="order_detail"),
    path("orders/update/<int:pk>/", views.OrderUpdateView.as_view(), name="order_update"),
    path("orders/delete/<int:pk>/", views.OrderDeleteView.as_view(), name="order_delete"),
    path('', views.dashboard, name='dashboard'),
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/add/', views.customer_create, name='customer_create'),
    path('customers/edit/<int:pk>/', views.customer_update, name='customer_update'),
    path('customers/delete/<int:pk>/', views.customer_delete, name='customer_delete'),
    path('customers/<int:pk>/', views.customer_detail, name='customer_detail'),
    path('products/', ProductListView.as_view()),
    path('profile/', views.profile_view, name='profile_view'),
    path("orders/", views.OrderListView.as_view()),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
]

