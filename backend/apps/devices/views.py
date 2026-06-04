from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import DeviceUnit, DevicePassport
from .serializers import PassportPublicSerializer, MyDeviceSerializer


class PassportPublicView(APIView):
    """
    GET /api/v1/devices/passport/{qr_uuid}/
    Публичный — не требует авторизации.
    Открывается при сканировании QR-кода.
    """

    permission_classes = [AllowAny]

    def get(self, request, qr_uuid):
        try:
            unit = DeviceUnit.objects.select_related(
                "device_model",
                "device_model__manufacturer",
                "passport",
            ).get(pk=qr_uuid)
        except DeviceUnit.DoesNotExist:
            return Response(
                {"error": "NOT_FOUND", "message": "Passport not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Паспорт может ещё не существовать (устройство только произведено)
        passport, _ = DevicePassport.objects.get_or_create(unit=unit)

        # TODO: передать реальные ближайшие пункты через GeoService
        # когда будет реализован recyclers.services.GeoService
        nearest_points = []

        serializer = PassportPublicSerializer(
            passport, context={"nearest_collection_points": nearest_points}
        )
        return Response(serializer.data)


class PassportClaimView(APIView):
    """
    POST /api/v1/devices/passport/{qr_uuid}/claim/
    Привязать устройство к текущему пользователю.
    Требует JWT.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, qr_uuid):
        try:
            unit = DeviceUnit.objects.get(pk=qr_uuid)
        except DeviceUnit.DoesNotExist:
            return Response(
                {"error": "NOT_FOUND", "message": "Device not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        passport, created = DevicePassport.objects.get_or_create(unit=unit)

        # Устройство уже зарегистрировано на другого пользователя
        if (
            not created
            and passport.owner is not None
            and passport.owner != request.user
        ):
            return Response(
                {
                    "error": "CONFLICT",
                    "message": "Device already registered to another user.",
                },
                status=status.HTTP_409_CONFLICT,
            )

        passport.owner = request.user
        passport.status = DevicePassport.Status.IN_USE
        passport.activated_at = timezone.now()
        passport.save()

        return Response(
            {
                "message": "Device registered to your account.",
                "passport_id": passport.pk,
                "status": passport.status,
            }
        )


class MyDevicesView(APIView):
    """
    GET /api/v1/devices/my/
    Список устройств текущего пользователя.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        passports = DevicePassport.objects.filter(owner=request.user).select_related(
            "unit", "unit__device_model"
        )

        serializer = MyDeviceSerializer(passports, many=True)
        return Response(
            {
                "count": passports.count(),
                "results": serializer.data,
            }
        )
