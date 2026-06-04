from rest_framework import serializers
from .models import DeviceModel, DeviceUnit, DevicePassport


class CollectionPointBriefSerializer(serializers.Serializer):
    """Краткая информация о пункте приёма для страницы паспорта."""

    id = serializers.IntegerField()
    name = serializers.CharField()
    address = serializers.CharField()
    distance_km = serializers.FloatField()
    accepted_categories = serializers.ListField(child=serializers.CharField())


class DeviceModelSerializer(serializers.ModelSerializer):
    manufacturer = serializers.CharField(source="manufacturer.name")

    class Meta:
        model = DeviceModel
        fields = [
            "name",
            "category",
            "manufacturer",
            "eco_index",
            "material_composition",
        ]


class PassportPublicSerializer(serializers.ModelSerializer):
    """
    Публичный сериализатор — открывается по QR-коду без авторизации.
    GET /api/v1/devices/passport/{uuid}/
    """

    qr_uuid = serializers.UUIDField(source="unit.id")
    serial_number = serializers.CharField(source="unit.serial_number")
    device = DeviceModelSerializer(source="unit.device_model")
    manufactured_at = serializers.DateField(source="unit.manufactured_at")
    disassembly_guide_url = serializers.URLField(source="unit.device_model.manual_url")

    # Ближайшие пункты приёма — заполняются во view через GeoService
    nearest_collection_points = serializers.SerializerMethodField()

    class Meta:
        model = DevicePassport
        fields = [
            "qr_uuid",
            "serial_number",
            "device",
            "status",
            "manufactured_at",
            "disassembly_guide_url",
            "nearest_collection_points",
        ]

    def get_nearest_collection_points(self, obj):
        # Список передаётся из view через context
        points = self.context.get("nearest_collection_points", [])
        return CollectionPointBriefSerializer(points, many=True).data


class PassportClaimSerializer(serializers.Serializer):
    """POST /api/v1/devices/passport/{uuid}/claim/ — привязать устройство к себе."""

    # Тело запроса пустое — всё берётся из URL и request.user
    pass


class MyDeviceSerializer(serializers.ModelSerializer):
    """GET /api/v1/devices/my/ — список устройств текущего пользователя."""

    qr_uuid = serializers.UUIDField(source="unit.id")
    serial_number = serializers.CharField(source="unit.serial_number")
    device_name = serializers.CharField(source="unit.device_model.name")
    claimed_at = serializers.DateTimeField(source="activated_at")

    class Meta:
        model = DevicePassport
        fields = [
            "qr_uuid",
            "serial_number",
            "device_name",
            "status",
            "claimed_at",
        ]
