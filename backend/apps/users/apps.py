from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'  # Полнотекстовый путь к модулю
    label = 'users'      # Короткое имя для связей вроде 'users.User'
