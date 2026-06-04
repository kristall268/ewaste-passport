from django.apps import AppConfig

class ManufacturersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.manufacturers'  # Полнотекстовый путь к модулю
    label = 'manufacturers'      # Короткое имя для связей вроде 'users.User'
