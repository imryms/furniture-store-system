from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory
from .models import Customer, Order, OrderItem


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'phone', 'email', 'address']

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer', 'order_type', 'status', 'note']
        widgets ={
            'note': forms.Textarea(attrs={'rows':3})
        }
class OrderItemForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        quantity = cleaned_data.get('quantity')
        unit_price = cleaned_data.get('unit_price')

        if quantity and unit_price:
            cleaned_data['total_price'] = quantity * unit_price
        return cleaned_data

    class Meta:
        model = OrderItem
        fields = ['product_details', 'stock', 'quantity', 'unit_price']
        widgets = {
            'quantity' : forms.NumberInput(attrs={'min':0,'step':'0.01'}),
        }



OrderItemFormSet = inlineformset_factory(
    Order,
    OrderItem,
    form=OrderItemForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True
)





