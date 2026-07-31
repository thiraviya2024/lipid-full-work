# app/api/routes/blood_test.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.services.analysis_service import get_analysis_service

router = APIRouter(prefix="/blood-test", tags=["Blood Test"])


class BloodTestRequest(BaseModel):
    text: str
    patient_info: Optional[dict] = None


@router.post("/analyze")
async def analyze_blood_test(request: BloodTestRequest):
    """Analyze blood test results from text input"""
    try:
        analysis_service = get_analysis_service()
        result = analysis_service.analyze_full_blood_test(request.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
