from fastapi import APIRouter
from .tasks import example_long_running_task

router = APIRouter()

# We will add endpoints here later
@router.get("/item/test")
async def item_test():
    return {"message": "Item router is working"}


@router.post("/item/run-task")
async def run_task():
    # .delay() 是 Celery 的异步调用方法
    task = example_long_running_task.delay(1, 2)
    return {"task_id": task.id, "message": "Task has been sent to the queue."}