from django.db import models

class Warehouse(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=60)
    address = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    is_main = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = "warehouses"
        ordering = ["id"]

class MovementType(models.Model):
    ENTRADA = "ENTRADA"
    SALIDA = "SALIDA"
    NATURES = [(ENTRADA, "Entrada"), (SALIDA, "Salida")]
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=80)
    nature = models.CharField(max_length=7, choices=NATURES)
    class Meta:
        db_table = "movement_types"

class Stock(models.Model):
    pk = models.CompositePrimaryKey("warehouse_id", "product_id")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name="stock")
    product_id = models.IntegerField()
    quantity = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    minimum_stock = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    alert_sent = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = "stock"

class Transfer(models.Model):
    id = models.AutoField(primary_key=True)
    origin_warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name="transfers_out")
    destination_warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name="transfers_in")
    user_id = models.BigIntegerField()
    notes = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = "transfers"

class Movement(models.Model):
    id = models.BigAutoField(primary_key=True)
    movement_type = models.ForeignKey(MovementType, on_delete=models.PROTECT)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT)
    product_id = models.IntegerField()
    transfer = models.ForeignKey(Transfer, on_delete=models.PROTECT, null=True, blank=True, related_name="movements")
    quantity = models.DecimalField(max_digits=12, decimal_places=3)
    resulting_balance = models.DecimalField(max_digits=12, decimal_places=3)
    reference = models.CharField(max_length=50, null=True, blank=True)
    reason = models.CharField(max_length=255, null=True, blank=True)
    user_id = models.BigIntegerField()
    correlation_id = models.CharField(max_length=36)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = "movements"
        indexes = [models.Index(fields=["product_id", "warehouse", "created_at"])]
    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise PermissionError("Un movimiento del kardex no se puede modificar")
        super().save(*args, **kwargs)
    def delete(self, *args, **kwargs):
        raise PermissionError("Un movimiento del kardex no se puede borrar")
