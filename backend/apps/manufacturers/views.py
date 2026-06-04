from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.devices.models import DeviceModel, DeviceUnit, Batch, DevicePassport
from .models import Manufacturer
from .permissions import IsManufacturer
from .serializers import (
    DeviceModelCreateSerializer,
    DeviceModelResponseSerializer,
    BatchCreateSerializer,
    BatchResponseSerializer,
)


class DeviceModelCreateView(APIView):
    """POST /api/v1/manufacturers/devices/"""

    permission_classes = [IsManufacturer]

    def _get_manufacturer(self, request):
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return Manufacturer.objects.get(api_key=api_key)
        return request.user.manufacturer_profile

    def post(self, request):
        serializer = DeviceModelCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "VALIDATION_ERROR", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        manufacturer = self._get_manufacturer(request)
        device_model = serializer.save(manufacturer=manufacturer)

        return Response(
            DeviceModelResponseSerializer(device_model).data,
            status=status.HTTP_201_CREATED,
        )


class BatchCreateView(APIView):
    """
    POST /api/v1/manufacturers/devices/{device_id}/batches/
    Загрузить партию серийных номеров для модели устройства.
    """

    permission_classes = [IsManufacturer]

    def _get_manufacturer(self, request):
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return Manufacturer.objects.get(api_key=api_key)
        return request.user.manufacturer_profile

    def post(self, request, device_id):
        # Проверить что модель существует и принадлежит этому производителю
        manufacturer = self._get_manufacturer(request)
        try:
            device_model = DeviceModel.objects.get(
                id=device_id, manufacturer=manufacturer
            )
        except DeviceModel.DoesNotExist:
            return Response(
                {"error": "NOT_FOUND", "message": "Device model not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = BatchCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "VALIDATION_ERROR", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serial_numbers = serializer.validated_data["serial_numbers"]
        manufactured_at = serializer.validated_data["manufactured_at"]

        # Проверить что серийные номера не зарегистрированы в этой модели ранее
        existing = DeviceUnit.objects.filter(
            device_model=device_model, serial_number__in=serial_numbers
        ).values_list("serial_number", flat=True)

        if existing:
            return Response(
                {
                    "error": "CONFLICT",
                    "message": "Some serial numbers already registered.",
                    "errors": {
                        "serial_numbers": [
                            f"{sn} already registered." for sn in existing
                        ]
                    },
                },
                status=status.HTTP_409_CONFLICT,
            )

        # Создать партию и экземпляры одной транзакцией
        batch = Batch.objects.create(
            device_model=device_model, manufactured_at=manufactured_at
        )

        units = DeviceUnit.objects.bulk_create(
            [
                DeviceUnit(
                    device_model=device_model,
                    batch=batch,
                    serial_number=sn,
                    manufactured_at=manufactured_at,
                )
                for sn in serial_numbers
            ]
        )

        # Создать паспорта для всех экземпляров сразу
        DevicePassport.objects.bulk_create(
            [DevicePassport(unit=unit) for unit in units]
        )

        return Response(
            BatchResponseSerializer(batch, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )
