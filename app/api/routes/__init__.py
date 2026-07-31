# app/api/routes/__init__.py
from .upload import router
from .analyze import router as analyze_router
from .report import router as report_router
from .admin import router as admin_router
from .blood_test import router as blood_test_router
