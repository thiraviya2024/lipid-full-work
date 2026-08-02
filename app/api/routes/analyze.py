# app/api/routes/analyze.py
"""
Analysis API Routes
"""

from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from typing import Optional, Dict, Any
from pydantic import BaseModel
import os
import shutil
from datetime import datetime

from app.services.lipid_service import LipidService
from app.services.cbc_service import CBCService
from app.services.lft_service import LFTService
from app.services.kft_service import KFTService
from app.services.thyroid_service import ThyroidService
from app.services.diabetes_service import DiabetesService
from app.services.vitamins_service import VitaminsService
from app.services.electrolytes_service import ElectrolytesService
from app.engines.extraction_engine.cbc_extractor import CBCExtractor

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
    """Analyze manual entry for any module."""
    try:
        if module == "lipid":
            if not request.lipid_values:
                raise HTTPException(status_code=400, detail="lipid_values required")
            values = request.lipid_values.dict(exclude_unset=True)
            service = LipidService()
            result = service.analyze_values(values)

        elif module == "cbc":
            if not request.cbc_values:
                raise HTTPException(status_code=400, detail="cbc_values required")
            service = CBCService()
            result = service.analyze_values(request.cbc_values)

        elif module == "lft":
            if not request.lft_values:
                raise HTTPException(status_code=400, detail="lft_values required")
            service = LFTService()
            result = service.analyze_values(request.lft_values)

        elif module == "kft":
            if not request.kft_values:
                raise HTTPException(status_code=400, detail="kft_values required")
            service = KFTService()
            result = service.analyze_values(request.kft_values)

        elif module == "thyroid":
            if not request.thyroid_values:
                raise HTTPException(status_code=400, detail="thyroid_values required")
            service = ThyroidService()
            result = service.analyze_values(request.thyroid_values)

        elif module == "diabetes":
            if not request.diabetes_values:
                raise HTTPException(status_code=400, detail="diabetes_values required")
            service = DiabetesService()
            result = service.analyze_values(request.diabetes_values)

        elif module == "vitamins":
            if not request.vitamins_values:
                raise HTTPException(status_code=400, detail="vitamins_values required")
            service = VitaminsService()
            result = service.analyze_values(request.vitamins_values)

        elif module == "electrolytes":
            if not request.electrolytes_values:
                raise HTTPException(status_code=400, detail="electrolytes_values required")
            service = ElectrolytesService()
            result = service.analyze_values(request.electrolytes_values)

        else:
            raise HTTPException(status_code=400, detail=f"Unknown module: {module}")

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/file")
async def analyze_file(
    file: UploadFile = File(...),
    module: str = Query("lipid", description="Module to analyze: lipid, cbc, lft, kft, thyroid, diabetes, vitamins, electrolytes"),
    patient_info: Optional[str] = None
):
    """
    Upload and analyze a file.
    
    Supports: PDF, DOCX, TXT, CSV, XLSX, PNG, JPG
    """
    try:
        # Create upload directory
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(upload_dir, safe_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Read text from file based on extension
        file_extension = os.path.splitext(file.filename)[1].lower()
        text_content = ""
        
        if file_extension in ['.txt', '.csv']:
            # Read text files directly
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text_content = f.read()
        elif file_extension == '.pdf':
            # For PDF, use pdfplumber or PyPDF2
            try:
                import pdfplumber
                with pdfplumber.open(file_path) as pdf:
                    text_content = " ".join([page.extract_text() or "" for page in pdf.pages])
            except ImportError:
                text_content = "PDF parsing requires pdfplumber. Please install: pip install pdfplumber"
        elif file_extension in ['.docx', '.doc']:
            # For DOCX
            try:
                import docx
                doc = docx.Document(file_path)
                text_content = " ".join([para.text for para in doc.paragraphs])
            except ImportError:
                text_content = "DOCX parsing requires python-docx. Please install: pip install python-docx"
        else:
            text_content = f"File uploaded: {file.filename}. Manual analysis not available for this file type."
        
        # Determine which module to use
        if module == "cbc":
            extractor = CBCExtractor()
            values = extractor.extract(text_content)
            if values:
                service = CBCService()
                result = service.analyze_values(values)
            else:
                result = {
                    'success': False,
                    'message': 'No CBC values found in the file. Please use Manual Entry.',
                    'results': {}
                }
        elif module == "lipid":
            # For lipid, try to extract from text or use manual entry
            result = {
                'success': False,
                'message': 'File analysis for Lipid is not fully implemented yet. Please use Manual Entry for now.',
                'results': {}
            }
        else:
            result = {
                'success': False,
                'message': f'File analysis for {module} is not fully implemented yet. Please use Manual Entry.',
                'results': {}
            }
        
        # Add file info to result
        if isinstance(result, dict):
            result['file_info'] = {
                'filename': safe_filename,
                'size': os.path.getsize(file_path),
                'module': module
            }
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
