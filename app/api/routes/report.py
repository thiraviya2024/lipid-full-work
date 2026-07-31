from fastapi import APIRouter, HTTPException, Depends 
from fastapi.responses import FileResponse 
from app.services.analysis_service import get_analysis_service 
from app.models.schemas import ManualEntryRequest 
import logging 
 
router = APIRouter(prefix="/report", tags=["Report"]) 
logger = logging.getLogger(__name__) 
 
@router.post("/generate") 
async def generate_report( 
    request: ManualEntryRequest, 
    analysis_service=Depends(get_analysis_service) 
): 
    try: 
        lipid_values = request.lipid_values.dict(exclude_none=True) 
        patient_info = request.patient_info or {} 
        result = analysis_service.analyze_values(lipid_values, patient_info) 
        from report.report_generator import generate_summary_report 
        report_path = generate_summary_report( 
            result.dict(),  
            result.ai_explanation.get("summary", ""), 
            "manual_entry" 
        ) 
        return FileResponse(report_path, media_type="application/pdf", filename="LipidAI_Report.pdf") 
    except Exception as e: 
        logger.error(f"Report error: {e}") 
        raise HTTPException(500, str(e)) 
