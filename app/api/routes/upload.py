from fastapi import APIRouter, UploadFile, File, HTTPException, Depends 
import shutil 
from pathlib import Path 
import uuid 
import logging 
from app.core.config import settings 
from app.services.analysis_service import get_analysis_service 
from app.models.schemas import AnalysisResponse 
 
router = APIRouter(prefix="/upload", tags=["Upload"]) 
logger = logging.getLogger(__name__) 
 
@router.post("/report", response_model=AnalysisResponse) 
async def upload_report( 
    file: UploadFile = File(...), 
    analysis_service=Depends(get_analysis_service) 
): 
    ext = Path(file.filename).suffix.lower() 
    if ext not in settings.ALLOWED_EXTENSIONS: 
        raise HTTPException(400, "Unsupported file format") 
    upload_dir = Path(settings.UPLOAD_DIR) 
    upload_dir.mkdir(parents=True, exist_ok=True) 
    file_id = str(uuid.uuid4()) 
    file_path = upload_dir / f"{file_id}{ext}" 
    try: 
        with open(file_path, "wb") as f: 
            shutil.copyfileobj(file.file, f) 
        result = analysis_service.analyze_from_file(file_path) 
        file_path.unlink(missing_ok=True) 
        return result 
    except ValueError as e: 
        raise HTTPException(400, str(e)) 
    except Exception as e: 
        logger.error(f"Upload error: {e}") 
        raise HTTPException(500, f"Processing error: {str(e)}") 
