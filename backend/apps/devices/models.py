from django.db import models
from django.conf import settings
from apps.manufacturers.models import Manufacturer
import uuid


class DeviceModel(models.Model):
    """
    Модель/тип устройства (например, 'ProBook X15').
    Соответствует 'Device' из ARCHITECTURE.md (не путать с экземпляром).
    Переименовано, чтобы не конфликтовать с именем 'Device' для паспорта.
    """

    manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.CASCADE,
        related_name="device_models",
        verbose_name="Производитель",
    )
    name = models.CharField(max_length=255, verbose_name="Название модели")

    # БЫЛО: category отсутствовал — API.md и ARCHITECTURE.md требуют его
    category = models.CharField(max_length=100, verbose_name="Категория устройства")

    release_date = models.DateField(verbose_name="Дата выпуска модели")

    # material_composition остаётся JSONField — правильно по архитектуре
    material_composition = models.JSONField(
        verbose_name="Состав материалов (WEEE data)",
        help_text="Пластик, металлы, батареи, опасные вещества.",
    )

    # ДОБАВИТЬ: eco_index — упомянут в API.md
    eco_index = models.PositiveSmallIntegerField(
        null=True, blank=True, verbose_name="Экологический индекс (0-100)"
    )

    manual_url = models.URLField(
        blank=True, null=True, verbose_name="PDF-инструкция по разборке"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Модель устройства"
        verbose_name_plural = "Модели устройств"

    def __str__(self):
        return f"{self.name} ({self.manufacturer.name})"


class DeviceUnit(models.Model):
    """
    Конкретный физический экземпляр устройства.
    БЫЛО: называлось 'Device', совмещало роль модели и экземпляра.
    СТАЛО: разделено — DeviceModel (тип) + DeviceUnit (экземпляр).
    """

    # UUID — публичный идентификатор, идёт в QR-код
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    device_model = models.ForeignKey(
        DeviceModel,
        on_delete=models.CASCADE,
        related_name="units",
        verbose_name="Модель устройства",
    )

    serial_number = models.CharField(max_length=100, verbose_name="Серийный номер")

    # ДОБАВИТЬ: дата производства конкретного экземпляра
    manufactured_at = models.DateField(
        null=True, blank=True, verbose_name="Дата производства"
    )

    class Meta:
        verbose_name = "Экземпляр устройства"
        verbose_name_plural = "Экземпляры устройств"
        unique_together = ("device_model", "serial_number")

    def __str__(self):
        return f"SN: {self.serial_number} | {self.device_model.name}"


class DevicePassport(models.Model):
    """
    Паспорт конкретного экземпляра: владелец, статус, история.
    БЫЛО: статус и владелец были смешаны прямо в 'Device'.
    СТАЛО: отдельная модель, как описано в ARCHITECTURE.md.
    """

    class Status(models.TextChoices):
        PRODUCED = "PRODUCED", "ПРОИЗВЕДЕНО"
        IN_USE = "IN_USE", "В ИСПОЛЬЗОВАНИИ"
        PLANNED = "PLANNED", "ЗАПЛАНИРОВАНО"
        COLLECTED = "COLLECTED", "СОБРАНО В ПУНКТЕ ПРИЕМА"
        RECYCLED = "RECYCLED", "УТИЛИЗИРОВАНО/ПЕРЕРАБОТАНО"

    unit = models.OneToOneField(
        DeviceUnit,
        on_delete=models.CASCADE,
        related_name="passport",
        verbose_name="Экземпляр устройства",
    )

    # Владелец — nullable, паспорт работает без регистрации (см. ARCHITECTURE.md)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="owned_devices",
        verbose_name="Владелец",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PRODUCED,
        verbose_name="Статус жизненного цикла",
    )

    activated_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Дата активации"
    )
    status_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Паспорт устройства"
        verbose_name_plural = "Паспорта устройств"

    def __str__(self):
        return f"Паспорт {self.unit.id} | {self.get_status_display()}"
