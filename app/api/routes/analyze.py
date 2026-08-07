@router.post("/analyze/file")
async def analyze_file(
    file: UploadFile = File(...),
    module: str = Query("cbc", description="Module to analyze: lipid, cbc, lft, kft, thyroid, diabetes, vitamins, electrolytes"),
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
        
        # Get file extension
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        # Extract text from file
        text_content = extract_text_from_file(file_path, file_extension)
        
        # Parse values from text
        values = parse_lab_values(text_content, module)
        
        # Determine which module to use
        service_map = {
            "lipid": LipidService,
            "cbc": CBCService,
            "lft": LFTService,
            "kft": KFTService,
            "thyroid": ThyroidService,
            "diabetes": DiabetesService,
            "vitamins": VitaminsService,
            "electrolytes": ElectrolytesService,
        }
        
        if module not in service_map:
            return {
                'success': False,
                'message': f'Unknown module: {module}',
                'file_info': {
                    'filename': safe_filename,
                    'size': os.path.getsize(file_path),
                    'module': module
                }
            }
        
        if values:
            service = service_map[module]()
            result = service.analyze_values(values)
            result['message'] = f'{module.upper()} analysis completed from file'
            result['file_info'] = {
                'filename': safe_filename,
                'size': os.path.getsize(file_path),
                'module': module
            }
            return result
        else:
            return {
                'success': False,
                'message': f'No {module.upper()} values found in the file. Please use Manual Entry.',
                'file_info': {
                    'filename': safe_filename,
                    'size': os.path.getsize(file_path),
                    'module': module
                },
                'extracted_text_preview': text_content[:500] if text_content else None
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))