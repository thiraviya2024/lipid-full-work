# app/api/routes/analyze.py
"""
Analysis API Routes
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any
from pydantic import BaseModel

from app.services.lipid_service import LipidService
from app.services.cbc_service import CBCService
from app.services.lft_service import LFTService
from app.services.kft_service import KFTService
from app.services.thyroid_service import ThyroidService
from app.services.diabetes_service import DiabetesService
from app.services.vitamins_service import VitaminsService
from app.services.electrolytes_service import ElectrolytesService

router = APIRouter()


class LipidValues(BaseModel):
    total_cholesterol: Optional[float] = None
    ldl: Optional[float] = None
    hdl: Optional[float] = None
    triglycerides: Optional[float] = None
    vldl: Optional[float] = None
    non_hdl: Optional[float] = None


class ManualEntryRequest(BaseModel):
    lipid_values: Optional[LipidValues] = None
    cbc_values: Optional[Dict[str, float]] = None
    lft_values: Optional[Dict[str, float]] = None
    kft_values: Optional[Dict[str, float]] = None
    thyroid_values: Optional[Dict[str, float]] = None
    diabetes_values: Optional[Dict[str, float]] = None
    vitamins_values: Optional[Dict[str, float]] = None
    electrolytes_values: Optional[Dict[str, float]] = None
    patient_info: Optional[Dict[str, Any]] = None


@router.post("/analyze/manual")
async def analyze_manual(
    module: str = Query(..., description="Module to analyze: lipid, cbc, lft, kft, thyroid, diabetes, vitamins, electrolytes"),
    request: ManualEntryRequest = None
):
    """
    Analyze manual entry for any module.
    """
    try:
        # Extract values based on module
        if module == "lipid":
            if not request.lipid_values:
                raise HTTPException(status_code=400, detail="lipid_values required")
            values = request.lipid_values.dict(exclude_unset=True)
            service = LipidService()
            result = service.analyze_values(values)  # ← ONLY 1 ARGUMENT

        elif module == "cbc":
            if not request.cbc_values:
                raise HTTPException(status_code=400, detail="cbc_values required")
            service = CBCService()
            result = service.analyze_values(request.cbc_values)  # ← ONLY 1 ARGUMENT

        elif module == "lft":
            if not request.lft_values:
                raise HTTPException(status_code=400, detail="lft_values required")
            service = LFTService()
            result = service.analyze_values(request.lft_values)  # ← ONLY 1 ARGUMENT

        elif module == "kft":
            if not request.kft_values:
                raise HTTPException(status_code=400, detail="kft_values required")
            service = KFTService()
            result = service.analyze_values(request.kft_values)  # ← ONLY 1 ARGUMENT

        elif module == "thyroid":
            if not request.thyroid_values:
                raise HTTPException(status_code=400, detail="thyroid_values required")
            service = ThyroidService()
            result = service.analyze_values(request.thyroid_values)  # ← ONLY 1 ARGUMENT

        elif module == "diabetes":
            if not request.diabetes_values:
                raise HTTPException(status_code=400, detail="diabetes_values required")
            service = DiabetesService()
            result = service.analyze_values(request.diabetes_values)  # ← ONLY 1 ARGUMENT

        elif module == "vitamins":
            if not request.vitamins_values:
                raise HTTPException(status_code=400, detail="vitamins_values required")
            service = VitaminsService()
            result = service.analyze_values(request.vitamins_values)  # ← ONLY 1 ARGUMENT

        elif module == "electrolytes":
            if not request.electrolytes_values:
                raise HTTPException(status_code=400, detail="electrolytes_values required")
            service = ElectrolytesService()
            result = service.analyze_values(request.electrolytes_values)  # ← ONLY 1 ARGUMENT

        else:
            raise HTTPException(status_code=400, detail=f"Unknown module: {module}")

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/file")
async def analyze_file():
    """
    Analyze uploaded file (coming soon).
    """
    return {"message": "File analysis coming soon"}