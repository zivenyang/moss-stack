import time
from app.shared.infrastructure.messaging.celery_app import celery_app


@celery_app.task
def example_long_running_task(x: int, y: int) -> int:
    print(f"Task started with args: {x}, {y}")
    time.sleep(5)  # 模拟一个耗时操作
    result = x + y
    print(f"Task finished with result: {result}")
    return result
