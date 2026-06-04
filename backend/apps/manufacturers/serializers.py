from rest_framework import serializers
from apps.devices.models import DeviceModel, DeviceUnit


class DeviceModelCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceModel
        fields = [
            "name",
            "category",
            "release_date",
            "material_composition",
            "eco_index",
            "manual_url",
        ]

    def validate_eco_index(self, value):
        if value is not None and not (0 <= value <= 100):
            raise serializers.ValidationError("Eco index must be between 0 and 100.")
        return value

    def validate_material_composition(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Must be a JSON object.")
        return value


class DeviceModelResponseSerializer(serializers.ModelSerializer):
    device_id = serializers.IntegerField(source="id")

    class Meta:
        model = DeviceModel
        fields = ["device_id", "name", "category"]


# ─── Партии ────────────────────────────────────────────────────────────────


class BatchCreateSerializer(serializers.Serializer):
    """Входные данные для POST /api/v1/manufacturers/devices/{id}/batches/"""

    serial_numbers = serializers.ListField(
        child=serializers.CharField(max_length=100),
        min_length=1,
    )
    manufactured_at = serializers.DateField()

    def validate_serial_numbers(self, value):
        # Дубликаты внутри одного запроса
        if len(value) != len(set(value)):
            raise serializers.ValidationError(
                "Serial numbers must be unique within the batch."
            )
        return value


class DeviceUnitSerializer(serializers.ModelSerializer):
    """Один экземпляр в ответе на загрузку партии."""

    qr_uuid = serializers.UUIDField(source="id")
    passport_url = serializers.SerializerMethodField()

    class Meta:
        model = DeviceUnit
        fields = ["serial_number", "qr_uuid", "passport_url"]

    def get_passport_url(self, obj):
        request = self.context.get("request")
        # Абсолютный URL на основе текущего хоста
        base = (
            request.build_absolute_uri("/")
            if request
            else "https://ewaste-passport.io/"
        )
        return f"{base.rstrip('/')}api/v1/devices/passport/{obj.id}/"


class BatchResponseSerializer(serializers.Serializer):
    """Ответ после успешной загрузки партии."""

    batch_id = serializers.IntegerField(source="id")
    device_id = serializers.IntegerField(source="device_model.id")
    count = serializers.SerializerMethodField()
    units = serializers.SerializerMethodField()

    def get_count(self, obj):
        return obj.units.count()

    def get_units(self, obj):
        request = self.context.get("request")
        return DeviceUnitSerializer(
            obj.units.all(), many=True, context={"request": request}
        ).data
