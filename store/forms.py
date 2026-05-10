from django import forms
from .models import Customer
from .models import Order

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'phone', 'email', 'address']

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer','branch' ,'created_by' , 'order_type', 'status', 'note']
