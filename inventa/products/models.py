from decimal import Decimal, ROUND_HALF_UP
from django.db import models, transaction
from django.utils import timezone
from django.core.validators import MinValueValidator

# Create your models here.
class Product(models.Model):
    sku = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=255)
    quantity = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.sku} — {self.name}"
    
class PurchaseOrder(models.Model):
    # Supplier Info
    supplier_name = models.CharField(max_length=255)
    supplier_address = models.CharField(max_length=255, blank=True)

    # Business Info
    business_name = models.CharField(max_length=255)
    business_address = models.CharField(max_length=255, blank=True)

    # Payment Terms
    payment_terms = models.CharField(max_length=255, default="COD")

    # Date
    date = models.DateField(default=timezone.now)

    # Tax and totals
    tax_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("12.00"),
        help_text="Tax rate as a whole percent (e.g., 12.00 for 12%)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PO #{self.id} — {self.supplier_name} ({self.date})"

    # ---------- COMPUTED FIELDS ----------
    @property
    def subtotal(self):
        # Sum of all line totals (unit_price × qty)
        return sum((item.line_total for item in self.items.all()), Decimal("0.00"))

    @property
    def total_order_price(self):
        return self.subtotal

    def tax_value(self):
        # Convert tax_amount (12) → 0.12
        rate = self.tax_percent / Decimal("100")
        value = self.subtotal * rate
        return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @property
    def total_with_tax(self):
        rate = self.tax_percent / Decimal("100")  # convert to 0.12
        total = self.subtotal * (Decimal("1.00") + rate)
        return total.quantize(Decimal("0.01"))


    # ---------- STOCK LOGIC ----------
    @transaction.atomic
    def confirm_and_increase_stock(self):
        # Increases each product's stock based on PO items
        for item in self.items.select_related("product"):
            item.product.quantity = models.F("quantity") + item.quantity_received
            item.product.save(update_fields=["quantity"])

        # Refresh to resolve F() expressions
        for item in self.items.select_related("product"):
            item.product.refresh_from_db(fields=["quantity"])


class PurchaseOrderItem(models.Model):
    # Link to Purchase Order
    po = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name="items")

    # 🔗 Link to Product
    product = models.ForeignKey(Product, on_delete=models.PROTECT)

    # Snapshot fields (keep historical name/SKU for printing)
    product_sku = models.CharField(max_length=64, blank=True)
    product_name = models.CharField(max_length=255, blank=True)

    # Order details
    quantity_received = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))])

    def __str__(self):
        return f"PO#{self.po_id} • {self.product_sku or self.product.sku} x {self.quantity_received}"

    def save(self, *args, **kwargs):
        # Automatically copy product SKU and name for recordkeeping
        if not self.product_sku:
            self.product_sku = self.product.sku
        if not self.product_name:
            self.product_name = self.product.name
        super().save(*args, **kwargs)

    @property
    def line_total(self):
        # Total price per product
        return self.unit_price * self.quantity_received