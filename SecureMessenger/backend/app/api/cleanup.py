from fastapi import APIRouter
from app.utils.cleanup import cleanup_all

router = APIRouter(prefix="/cleanup", tags=["cleanup"])

@router.post("/now")
async def cleanup_now():
    res = await cleanup_all()
    return {"status": "ok", **res}
