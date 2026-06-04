import uuid
from django.db import models
from django.conf import settings


class Manufacturer(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="manufacturer_profile",
        verbose_name="Пользователь-Владелец",
    )
    name = models.CharField(max_length=255, verbose_name="Название компании")
    country = models.CharField(max_length=100, verbose_name="Страна регистрации")
    website = models.URLField(max_length=255, verbose_name="Веб-сайт")

    api_key = models.UUIDField(
        default=uuid.uuid4, unique=True, editable=False, verbose_name="API ключ"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    weee_number = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True,
        verbose_name="WEEE-регистрационный номер",
    )

    class Meta:
        verbose_name = "Производитель"
        verbose_name_plural = "Производители"

    def __str__(self):
        return self.name
