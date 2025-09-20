from fastapi import APIRouter

router = APIRouter()

# We will add endpoints here later
@router.get("/item/test")
async def item_test():
    return {"message": "Item router is working"}