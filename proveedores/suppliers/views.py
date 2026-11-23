from django.db.models import Q
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .errors import error_response
from .models import Supplier
from .serializers import SupplierSerializer


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