from django.http import JsonResponse
from .scan_task import start_scan
from .trade_task import start_trading
def start_heavy_task(request):
    task = start_trading.delay()
    return JsonResponse({"task_id": task.id, "status": "Task started!"})


def scan_arbitrage_opportunity(request):
    task = start_scan.delay()
    return JsonResponse({"task_id": task.id, "status": "Task started!"})

