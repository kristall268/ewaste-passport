from django.db import models
from apps.manufacturers.models import Manufacturer
import uuid

class Batch(models.Model):
    manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.CASCADE,
        related_name="batches",
        verbose_name="Производитель"
    )
    name = models.CharField(max_length=255, verbose_name="Назначение партии/модели (Например ProBook X15)")
    release_date = models.DateField(verbose_name="Дата выпуска партии")

    components_spec = models.JSONField(
        verbose_name="Спецификация материалов и компонентов (WEEE data)",
        help_text="Данные о содержании пластика, металлов, батарей и опасных веществ."
    )
    manual_url = models.URLField(blank=True, null=True, verbose_name="Ссылка на PDF-инструкцию по разборке")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Партия устройств"
        verbose_name_plural = "Партий устройств"
    def __str__(self):
        return f"{self.name} от ({self.manufacturer.name})"


class Device(models.Model):
    class Status(models.TextChoices):
        PRODUCED = 'PRODUCED', 'ПРОИЗВЕДЕНО'
        IN_USE = 'IN_USE', "В ИСПОЛЬЗОВАНИИ"
        PLANNED = "PLANNED", "ЗАПЛАНИРОВАНО"
        COLLECTED = "COLLECTED", "СОБРАНО В ПУНКТЕ ПРИЕМА"
        RECYCLED = "RECYCLED", "УТИЛИЗИРОВАНО/ПЕРЕРАБОТАНО"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    batch = models.ForeignKey(
        Batch,
        on_delete=models.CASCADE,
        related_name="devices",
        verbose_name="Партия"
    )

    serial_number = models.CharField(max_length=100, verbose_name = "Серийный номер производителя")

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PRODUCED,
        verbose_name="Статус жизненного цикла"
    )
    status_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Устройства (Цифровой паспорт)"
        verbose_name_plural = "Устройства (Цифровые паспорта)"
        unique_together = ("batch", "serial_number")
    def __str__(self):
        return f"Паспорт {self.id} | SN: {self.serial_number}"
