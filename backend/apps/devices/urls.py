from django.urls import path
from .views import PassportPublicView, PassportClaimView, MyDevicesView

urlpatterns = [
    path(
        "passport/<uuid:qr_uuid>/", PassportPublicView.as_view(), name="passport_public"
    ),
    path(
        "passport/<uuid:qr_uuid>/claim/",
        PassportClaimView.as_view(),
        name="passport_claim",
    ),
    path("my/", MyDevicesView.as_view(), name="my_devices"),
]
