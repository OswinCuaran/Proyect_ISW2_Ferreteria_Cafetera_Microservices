from django.core.validators import MinValueValidator
from django.db import models


class Supplier(models.Model):
    class PersonType(models.TextChoices):
        NATURAL = "NATURAL", "Natural"
        JURIDICA = "JURIDICA", "Juridica"

    nit = models.CharField(max_length=20, unique=True)
    person_type = models.CharField(max_length=10, choices=PersonType.choices)
    legal_name = models.CharField(max_length=150)
    trade_name = models.CharField(max_length=150, null=True, blank=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=120)
    address = models.CharField(max_length=150)
    city = models.CharField(max_length=60)
    delivery_days = models.PositiveIntegerField(
        default=1, validators=[MinValueValidator(1)]
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "suppliers"

    def __str__(self):
        return f"{self.nit} - {self.legal_name}"


class SupplierContact(models.Model):
    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, related_name="contacts"
    )
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=60, null=True, blank=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=120, null=True, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "supplier_contacts"

    def __str__(self):
        return f"{self.name} ({self.supplier_id})"