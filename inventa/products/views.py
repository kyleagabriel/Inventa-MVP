from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from .forms import ProductForm, PurchaseOrderForm, PurchaseOrderItemFormSet
from .models import Product, PurchaseOrder

# Create your views here.
def product_list(request):
    products = Product.objects.all().order_by("name")
    return render(request, "products/product_list.html", {"products": products})

def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("product_list")  
    else:
        form = ProductForm()
    return render(request, "products/add_product.html", {"form": form})

@require_POST
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()  # hard delete; swap to soft delete if you prefer
    return redirect("product_list")

def po_create(request):
    """Encode a new Purchase Order (header + multiple items)."""
    if request.method == "POST":
        form = PurchaseOrderForm(request.POST)
        formset = PurchaseOrderItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            po = form.save()
            formset.instance = po
            formset.save()
            messages.success(request, f"PO #{po.id} saved as draft.")
            return redirect("po_detail", pk=po.pk)
    else:
        form = PurchaseOrderForm()
        formset = PurchaseOrderItemFormSet()
    return render(request, "products/po_create.html", {"form": form, "formset": formset})

def po_detail(request, pk):
    """Read-only review page that shows totals and a Confirm button."""
    po = get_object_or_404(PurchaseOrder, pk=pk)
    return render(request, "products/po_detail.html", {"po": po})

@require_POST
def po_confirm(request, pk):
    """Confirm the PO and increase stock based on line items."""
    po = get_object_or_404(PurchaseOrder, pk=pk)
    po.confirm_and_increase_stock()
    messages.success(request, f"PO #{po.id} confirmed. Stock updated ✅")
    return redirect("product_list")  # or redirect back to po_detail