from django.urls import path
from . import views
from .views import ProductListView


urlpatterns = [
    path('', views.dashboard),
    path('products', ProductListView.as_view())

]

