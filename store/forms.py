from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory
from .models import Customer, Order, OrderItem, Stock



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

class StockChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.location_type} ({obj.quantity} pcs)"


class OrderItemForm(forms.ModelForm):

    stock = StockChoiceField(queryset=Stock.objects.none(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        product_details_id = None

        if self.instance and self.instance.pk:
            product_details_id = self.instance.product_details_id

        if self.data:
            prefix_key = f'{self.prefix}-product_details' if self.prefix else 'product_details'
            product_details_id = self.data.get(prefix_key) or product_details_id

        self.fields['unit_price'].widget.attrs['readonly'] = True

        if product_details_id:
            self.fields['stock'].queryset = Stock.objects.filter(
                product_details_id=product_details_id
            )
            try:
                from .models import ProductDetails
                pd = ProductDetails.objects.get(pk=product_details_id)
                self.fields['unit_price'].initial = pd.price
                self.initial['unit_price'] = pd.price

                if self.data:
                    price_key = f'{self.prefix}-unit_price' if self.prefix else 'unit_price'
                    if not self.data.get(price_key):
                        self.data = self.data.copy()
                        self.data[price_key] = str(pd.price)
            except Exception:
                pass
        else:
            self.fields['stock'].queryset = Stock.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        product_details = cleaned_data.get('product_details')
        quantity = cleaned_data.get('quantity')

        if product_details:
            cleaned_data['unit_price'] = product_details.price

        if quantity and cleaned_data.get('unit_price'):
            cleaned_data['total_price'] = quantity * cleaned_data['unit_price']

        return cleaned_data

    class Meta:
        model = OrderItem
        fields = ['product_details', 'stock', 'quantity', 'unit_price']
        widgets = {
            'quantity': forms.NumberInput(attrs={'min': 1, 'step': '1'}),
            'unit_price': forms.NumberInput(attrs={'min': 0, 'step': '0.01'}),
        }


OrderItemFormSet = inlineformset_factory(
    Order,
    OrderItem,
    form=OrderItemForm,
    extra=0,
    can_delete=True,
    min_num=1,
    validate_min=True
)
