from django import forms
from django.forms import inlineformset_factory
from .models import Product, PurchaseOrder, PurchaseOrderItem

class ProductForm(forms.ModelForm):
    quantity = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Enter quantity'})
    )

    class Meta:
        model = Product
        fields = ["sku", "name", "quantity"]

    def clean_quantity(self):
        # If user leaves it blank, treat it as 0
        qty = self.cleaned_data.get("quantity")
        return qty if qty is not None else 0
    
class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = [
            "supplier_name", "supplier_address",
            "business_name", "business_address",
            "date", "tax_percent", "payment_terms" 
        ]

class PurchaseOrderItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderItem
        fields = ["product", "quantity_received", "unit_price"]
        widgets = {
            "quantity_received": forms.NumberInput(attrs={"min": 1, "placeholder": "Qty"}),
            "unit_price": forms.NumberInput(attrs={"step": "0.01", "placeholder": "0.00"}),
        }

PurchaseOrderItemFormSet = inlineformset_factory(
    parent_model=PurchaseOrder,
    model=PurchaseOrderItem,
    form=PurchaseOrderItemForm,
    extra=0,          # one blank row by default
    can_delete=True,  # allow removing rows
    min_num=1,
    validate_min=True,
)