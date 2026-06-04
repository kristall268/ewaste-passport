from django.contrib.gis.db import models as gis_models
from django.db import models
from django.conf import settings
from apps.devices.models import DeviceUnit


class RecyclerCompany(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recycler_profile",
    )
    name = models.CharField(
        max_length=255, verbose_name="Название компании переработчика"
    )
    license_number = models.CharField(
        max_length=100, verbose_name="Номер лицензии на утилизацию"
    )

    class Meta:
        verbose_name = "Компания-переработчик"
        verbose_name_plural = "Компании-переработчики"

    def __str__(self):
        return self.name


class CollectionPoint(models.Model):
    company = models.ForeignKey(
        RecyclerCompany,
        on_delete=models.CASCADE,
        related_name="points",
        verbose_name="Компания",
    )

    # ДОБАВИТЬ: name — API.md возвращает "name": "EcoPoint Mitte"
    name = models.CharField(max_length=255, verbose_name="Название пункта приёма")

    address = models.CharField(max_length=255, verbose_name="Физический адрес")

    location = gis_models.PointField(srid=4326, verbose_name="Геопозиция (координаты)")

    # БЫЛО: working_hours = CharField(max_length=100)
    # СТАЛО: JSONField — API.md возвращает {"mon-fri": "09:00-18:00", "sat": "...", "sun": "closed"}
    working_hours = models.JSONField(
        default=dict,
        verbose_name="Часы работы",
        help_text='Пример: {"mon-fri": "09:00-18:00", "sat": "10:00-15:00", "sun": "closed"}',
    )

    # ДОБАВИТЬ: accepted_categories — API.md возвращает список категорий
    accepted_categories = models.JSONField(
        default=list,
        verbose_name="Принимаемые категории устройств",
        help_text='Пример: ["laptop", "phone", "tablet"]',
    )

    # ДОБАВИТЬ: is_certified — API.md возвращает "is_certified": true
    is_certified = models.BooleanField(default=False, verbose_name="Сертифицирован")

    is_active = models.BooleanField(default=True, verbose_name="Активен")

    class Meta:
        verbose_name = "Пункт приёма"
        verbose_name_plural = "Пункты приёма"

    def __str__(self):
        return f"{self.name} ({self.company.name})"


class RecyclingRecord(models.Model):
    """
    НОВАЯ МОДЕЛЬ — факт приёмки устройства переработчиком.
    Описана в ARCHITECTURE.md, используется в POST /recyclers/accept/ (API.md).
    """

    unit = models.ForeignKey(
        DeviceUnit,
        on_delete=models.CASCADE,
        related_name="recycling_records",
        verbose_name="Экземпляр устройства",
    )
    collection_point = models.ForeignKey(
        CollectionPoint,
        on_delete=models.CASCADE,
        related_name="records",
        verbose_name="Пункт приёма",
    )
    recycled_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата приёмки")
    notes = models.TextField(blank=True, verbose_name="Примечания")

    class Meta:
        verbose_name = "Запись об утилизации"
        verbose_name_plural = "Записи об утилизации"

    def __str__(self):
        return f"Приёмка {self.unit.serial_number} @ {self.collection_point.name}"
