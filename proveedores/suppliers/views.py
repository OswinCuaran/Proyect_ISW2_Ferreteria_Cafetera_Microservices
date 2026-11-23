from django.db import transaction
from django.db.models import Q
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .errors import error_response
from .models import Supplier
from .serializers import ContactSerializer, SupplierSerializer


def find_supplier(pk):
    return Supplier.objects.filter(pk=pk).first()

def supplier_not_found(request):
    return error_response(request, 404, "NO_ENCONTRADO", "El proveedor no existe")


# ---------- GET / y POST / ----------

@api_view(["GET", "POST"])
def supplier_list(request):
    if request.method == "GET":
        return list_suppliers(request)
    return create_supplier(request)


def list_suppliers(request):
    suppliers = Supplier.objects.all().order_by("id")

    search = request.query_params.get("search")
    if search:
        suppliers = suppliers.filter(
            Q(nit__icontains=search) | Q(legal_name__icontains=search)
        )

    is_active = request.query_params.get("is_active")
    if is_active is not None:
        if is_active.lower() not in ("true", "false"):
            return error_response(
                request, 400, "DATOS_INVALIDOS",
                "El filtro is_active debe ser true o false",
            )
        suppliers = suppliers.filter(is_active=is_active.lower() == "true")

    return Response(SupplierSerializer(suppliers, many=True).data)


def create_supplier(request):
    serializer = SupplierSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    nit = serializer.validated_data["nit"]
    if Supplier.objects.filter(nit=nit).exists():
        return error_response(
            request, 409, "DUPLICADO", f"El NIT {nit} ya esta registrado"
        )

    serializer.save()
    return Response(serializer.data, status=201)


# ---------- GET /{id} y PUT /{id} ----------

@api_view(["GET", "PUT"])
def supplier_detail(request, pk):
    supplier = find_supplier(pk)
    if supplier is None:
        return supplier_not_found(request)

    if request.method == "GET":
        return Response(SupplierSerializer(supplier).data)

    serializer = SupplierSerializer(supplier, data=request.data)
    serializer.is_valid(raise_exception=True)

    nit = serializer.validated_data["nit"]
    if Supplier.objects.filter(nit=nit).exclude(pk=supplier.pk).exists():
        return error_response(
            request, 409, "DUPLICADO", f"El NIT {nit} pertenece a otro proveedor"
        )

    serializer.save()
    return Response(serializer.data)


# ---------- PATCH /{id}/deactivate ----------

@api_view(["PATCH"])
def supplier_deactivate(request, pk):
    supplier = find_supplier(pk)
    if supplier is None:
        return supplier_not_found(request)

    # No se borra: se desactiva para conservar el historial
    supplier.is_active = False
    supplier.save()
    return Response(SupplierSerializer(supplier).data)


# ---------- GET /{id}/contacts y POST /{id}/contacts ----------

@api_view(["GET", "POST"])
def supplier_contacts(request, pk):
    supplier = find_supplier(pk)
    if supplier is None:
        return supplier_not_found(request)

    if request.method == "GET":
        contacts = supplier.contacts.order_by("id")
        return Response(ContactSerializer(contacts, many=True).data)

    serializer = ContactSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    # Solo puede haber un contacto principal por proveedor
    with transaction.atomic():
        if serializer.validated_data.get("is_primary"):
            supplier.contacts.filter(is_primary=True).update(is_primary=False)
        serializer.save(supplier=supplier)

    return Response(serializer.data, status=201)