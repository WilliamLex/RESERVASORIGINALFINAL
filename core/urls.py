from django.contrib import admin
from django.urls import path
from django.urls.conf import include
from .views import IndexView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", IndexView.as_view(), name="index"),
    path("cuenta/", include("accounts.urls", namespace="accounts")),
    path("clientes/", include("clientes.urls", namespace="clientes")),
    path("reservas/", include("reservas.urls", namespace="reservas")),
]
