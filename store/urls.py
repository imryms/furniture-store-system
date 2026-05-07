from django.urls import path
from . import views
from .views import ProductListView

urlpatterns = [
    path("", views.dashboard),
    path("products", ProductListView.as_view()),
    path("orders/", views.OrderListView.as_view()),
    path("", views.dashboard, name="dashboard"),
    path("customers/", views.customer_list, name="customer_list"),
    path("customers/add/", views.customer_create, name="customer_create"),
    path("customers/edit/<int:pk>/", views.customer_update, name="customer_update"),
    path("customers/delete/<int:pk>/", views.customer_delete, name="customer_delete"),
    path("customers/<int:pk>/", views.customer_detail, name="customer_detail"),
    path("products/", ProductListView.as_view()),
]
