from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'АДМИНИСТРАТОР/РЕГУЛЯТОР'
        MANUFACTURER = 'MANUFACTURER', 'ПРОИЗВОДИТЕЛЬ'
        RECYCLER = 'RECYCLER', 'ПЕРЕРАБОТЧИК'
        USER = 'USER', 'КОНЕЧНЫЙ ПОЛЬЗОВАТЕЛЬ'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER,
        verbose_name="Роль в системе"
    )

    # Поле для интеграции с Telegram Mini App
    telegram_id = models.BigIntegerField(
        unique=True,
        null=True,
        blank=True,
        verbose_name="Telegram ID"
    )

    # Для B2B-пользователей email будет основным полем авторизации
    email = models.EmailField(
        unique=True,
        verbose_name="Email адрес"
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
