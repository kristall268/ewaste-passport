from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/", include("apps.users.urls")),
    path("api/v1/devices/", include("apps.devices.urls")),
    path("api/v1/manufacturers/", include("apps.manufacturers.urls")),
    path("api/v1/recyclers/", include("apps.recyclers.urls")),
    path("api/v1/collection-points/", include("apps.recyclers.urls_collection")),
]
