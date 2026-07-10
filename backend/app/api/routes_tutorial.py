from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(prefix="/api/v1/tutorial", tags=["tutorial"])

TUTORIAL_PATH = Path(__file__).resolve().parent.parent.parent / "tutorial.html"


@router.get("")
async def get_tutorial() -> FileResponse:
    if not TUTORIAL_PATH.exists():
        raise HTTPException(status_code=404, detail="Tutorial documentation not found")
    return FileResponse(TUTORIAL_PATH, media_type="text/html")
