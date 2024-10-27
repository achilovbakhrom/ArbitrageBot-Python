from django.http import JsonResponse
from .handler import heavy_task

def start_heavy_task(request):
    task = heavy_task.delay()
    return JsonResponse({"task_id": task.id, "status": "Task started!"})
