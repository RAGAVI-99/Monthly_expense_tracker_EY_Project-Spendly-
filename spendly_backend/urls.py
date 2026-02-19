# spendly_backend/urls.py
from django.contrib import admin
from django.urls import path, include, re_path
from .views import frontend_index, frontend_static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    path("", frontend_index),
    re_path(r"^(styles\.css|app\.js)$", frontend_static),
]
