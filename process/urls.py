from django.urls import path
from .views import start_heavy_task, scan_arbitrage_opportunity

urlpatterns = [
    path("trade_task/", start_heavy_task),
    path("scan_task/", scan_arbitrage_opportunity),
]