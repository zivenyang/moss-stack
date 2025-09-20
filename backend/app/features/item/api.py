from fastapi import APIRouter, Depends
from .tasks import example_long_running_task
from app.shared.web.deps import get_current_active_user
from app.features.auth.domain.user import User

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

@router.get("/item/protected-route")
async def read_protected_route(
    current_user: User = Depends(get_current_active_user)
):
    return {"message": f"Hello {current_user.username}, you are authenticated!"}