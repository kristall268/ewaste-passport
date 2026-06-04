from django.urls import path
from .views import DeviceModelCreateView, BatchCreateView, BatchQRCodesView

urlpatterns = [
    path(
        "devices/", DeviceModelCreateView.as_view(), name="manufacturer_device_create"
    ),
    path(
        "devices/<int:device_id>/batches/",
        BatchCreateView.as_view(),
        name="batch_create",
    ),
    path(
        "batches/<int:batch_id>/qr-codes.zip",
        BatchQRCodesView.as_view(),
        name="batch_qr_codes",
    ),
]
