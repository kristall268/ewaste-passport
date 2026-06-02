from django.contrib.gis.db import models as gis_models
from django.db import models
from django.conf import settings


class RecyclerCompany(models.Model):
    """Компания-утилизатор электронных отходов"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recycler_profile'
    )
    name = models.CharField(max_length=255,
                            verbose_name="Название компании переработчика")
    license_number = models.CharField(max_length=100,
                                      verbose_name="Номер лицензии на утилизацию")

    class Meta:
        verbose_name = "Компания-переработчик"
        verbose_name_plural = "Компании-переработчики"

    def __str__(self):
        return self.name


class CollectionPoint(models.Model):
    """Физическая точка/пункт приема электронного мусора"""
    company = models.ForeignKey(
        RecyclerCompany,
        on_delete=models.CASCADE,
        related_name='points',
        verbose_name="Компания"
    )
    address = models.CharField(max_length=255, verbose_name="Физический адрес")

    # Геопространственная точка PostGIS (содержит долготу и широту)
    location = gis_models.PointField(
        srid=4326,
        verbose_name="Геопозиция (координаты)"
    )

    working_hours = models.CharField(max_length=100, verbose_name="Часы работы")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    class Meta:
        verbose_name = "Пункт приема"
        verbose_name_plural = "Пункты приема"

    def __str__(self):
        return f"Точка: {self.address} ({self.company.name})"
