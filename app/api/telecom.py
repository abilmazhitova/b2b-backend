from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session_maker
from app.schemas.telecom_schema import (
    TelecomGridCreate, TelecomGridRead,
    TelecomStatCreate, TelecomStatRead
)
from app.services.telecom_service import (
    create_grid, get_grids,
    create_stat, get_stats_by_grid
)
from fastapi import File, UploadFile
import tempfile
from app.services.telecom_service import import_telecom_data

router = APIRouter(prefix="/telecom", tags=["Telecom"])


# ---------- GRIDS ----------
@router.post("/grids", response_model=TelecomGridRead)
async def add_grid(data: TelecomGridCreate):
    async with async_session_maker() as session:
        grid = await create_grid(session, data)
        return grid


@router.get("/grids", response_model=list[TelecomGridRead])
async def list_grids():
    async with async_session_maker() as session:
        grids = await get_grids(session)
        return grids


# ---------- STATS ----------
@router.post("/stats", response_model=TelecomStatRead)
async def add_stat(data: TelecomStatCreate):
    async with async_session_maker() as session:
        stat = await create_stat(session, data)
        return stat


@router.get("/stats", response_model=list[TelecomStatRead])
async def list_stats(grid_id: int):
    """Получить все статистики по конкретной ячейке (grid_id)."""
    async with async_session_maker() as session:
        stats = await get_stats_by_grid(session, grid_id)
        return stats



@router.post("/upload")
async def upload_telecom_file(
    file: UploadFile = File(...),
    month_label: str = Query(..., description="например '03.2023'")
):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    async with async_session_maker() as session:
        result = await import_telecom_data(session, tmp_path, month_label)
        return result