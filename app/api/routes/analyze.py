from fastapi import APIRouter, HTTPException, Depends 
from app.services.analysis_service import get_analysis_service 
from app.models.schemas import ManualEntryRequest, AnalysisResponse 
import logging 
 
router = APIRouter(prefix="/analyze", tags=["Analysis"]) 
logger = logging.getLogger(__name__) 
 
@router.post("/manual", response_model=AnalysisResponse) 
async def analyze_manual_entry( 
    request: ManualEntryRequest, 
    analysis_service=Depends(get_analysis_service) 
): 
    try: 
        lipid_values = request.lipid_values.dict(exclude_none=True) 
        patient_info = request.patient_info or {} 
        return analysis_service.analyze_values(lipid_values, patient_info) 
    except Exception as e: 
        logger.error(f"Analysis error: {e}") 
        raise HTTPException(500, str(e)) 
