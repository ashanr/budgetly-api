from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from typing import Optional
import io
from app.database import get_db
from app.schemas.common import APIResponse
from app.services.export_service import ExportService
from app.repositories.expense_repository import ExpenseRepository
from app.repositories.budget_repository import BudgetRepository
from app.core.security import get_current_user_id

router = APIRouter()


def get_export_service(db: AsyncSession = Depends(get_db)) -> ExportService:
    return ExportService(ExpenseRepository(db), BudgetRepository(db))


@router.get("/export/csv/{user_id}")
async def export_csv(
    user_id: str,
    start: Optional[date] = Query(default=None),
    end: Optional[date] = Query(default=None),
    _current_user: str = Depends(get_current_user_id),
    export_service: ExportService = Depends(get_export_service),
):
    csv_data = await export_service.export_csv(user_id, start, end)
    return StreamingResponse(
        io.StringIO(csv_data),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=expenses_{user_id}.csv"},
    )


@router.get("/export/json/{user_id}", response_model=APIResponse)
async def export_json(
    user_id: str,
    start: Optional[date] = Query(default=None),
    end: Optional[date] = Query(default=None),
    _current_user: str = Depends(get_current_user_id),
    export_service: ExportService = Depends(get_export_service),
):
    data = await export_service.export_json(user_id, start, end)
    return APIResponse.ok(data=data, message="Export generated")


@router.get("/export/pdf/{user_id}", response_model=APIResponse)
async def export_pdf(
    user_id: str,
    _current_user: str = Depends(get_current_user_id),
):
    return APIResponse.ok(
        data={"message": "PDF export is available when ReportLab is configured", "user_id": user_id},
        message="PDF export endpoint ready",
    )


@router.post("/import/{user_id}", response_model=APIResponse)
async def import_data(
    user_id: str,
    payload: dict,
    _current_user: str = Depends(get_current_user_id),
    export_service: ExportService = Depends(get_export_service),
):
    result = await export_service.restore(user_id, payload)
    return APIResponse.ok(data=result, message="Import preview completed")


@router.post("/backup/{user_id}", response_model=APIResponse)
async def backup_data(
    user_id: str,
    _current_user: str = Depends(get_current_user_id),
    export_service: ExportService = Depends(get_export_service),
):
    data = await export_service.backup(user_id)
    return APIResponse.ok(data=data, message="Backup created")


@router.post("/restore/{user_id}", response_model=APIResponse)
async def restore_data(
    user_id: str,
    payload: dict,
    _current_user: str = Depends(get_current_user_id),
    export_service: ExportService = Depends(get_export_service),
):
    result = await export_service.restore(user_id, payload)
    return APIResponse.ok(data=result, message="Restore completed")
