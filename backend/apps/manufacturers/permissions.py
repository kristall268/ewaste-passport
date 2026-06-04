from rest_framework.permissions import BasePermission
from .models import Manufacturer


class IsManufacturer(BasePermission):
    """
    Разрешает доступ если:
    - запрос содержит валидный X-API-Key производителя, ИЛИ
    - пользователь авторизован через JWT и имеет роль MANUFACTURER
    """

    def has_permission(self, request, view):
        # Способ 1: X-API-Key в заголовке
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return Manufacturer.objects.filter(api_key=api_key).exists()

        # Способ 2: JWT + роль
        return request.user.is_authenticated and request.user.role == "MANUFACTURER"
