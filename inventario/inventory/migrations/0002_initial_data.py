from django.db import migrations

MOVEMENT_TYPES = [
    ("ENTRADA_COMPRA", "Entrada por compra a proveedor", "ENTRADA"),
    ("DEVOLUCION_CLIENTE", "Devolución de un cliente", "ENTRADA"),
    ("SALIDA_VENTA_MOSTRADOR", "Venta de mostrador", "SALIDA"),
    ("SALIDA_VENTA_MAYORISTA", "Venta mayorista", "SALIDA"),
    ("DEVOLUCION_PROVEEDOR", "Devolución a proveedor", "SALIDA"),
    ("AJUSTE_POSITIVO", "Ajuste positivo de inventario", "ENTRADA"),
    ("AJUSTE_NEGATIVO", "Ajuste negativo de inventario", "SALIDA"),
    ("TRASLADO_SALIDA", "Salida por traslado entre bodegas", "SALIDA"),
    ("TRASLADO_ENTRADA", "Entrada por traslado entre bodegas", "ENTRADA"),
]

WAREHOUSES = [
    ("MZL", "Bodega central Manizales", "Manizales", "Cra. 23 # 65-10", "6068801234", True),
    ("PER", "Bodega Pereira", "Pereira", "Av. 30 de Agosto # 40-12", "6063401122", False),
    ("ARM", "Bodega Armenia", "Armenia", "Cra. 14 # 18-25", "6067412233", False),
]

def seed(apps, schema_editor):
    MovementType = apps.get_model("inventory", "MovementType")
    Warehouse = apps.get_model("inventory", "Warehouse")
    for code, name, nature in MOVEMENT_TYPES:
        MovementType.objects.update_or_create(code=code, defaults={"name": name, "nature": nature})
    for code, name, city, address, phone, is_main in WAREHOUSES:
        Warehouse.objects.update_or_create(code=code, defaults={
            "name": name, "city": city, "address": address, "phone": phone, "is_main": is_main,
        })

class Migration(migrations.Migration):
    dependencies = [
        ("inventory", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed, migrations.RunPython.noop),
    ]
