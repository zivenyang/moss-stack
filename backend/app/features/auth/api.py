from fastapi import APIRouter

router = APIRouter()

# We will add endpoints here later
@router.get("/auth/test")
async def auth_test():
    return {"message": "Auth router is working"}