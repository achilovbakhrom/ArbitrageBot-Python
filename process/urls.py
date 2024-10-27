from django.urls import path
from .views import start_heavy_task

urlpatterns = [
    path("start_heavy_task/", start_heavy_task),
]