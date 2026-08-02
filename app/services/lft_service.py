# app/services/lft_service.py
"""
LFT Analysis Service
"""

from typing import Dict, Any, Optional
from app.engines.extraction_engine.lft_extractor import LFTExtractor
from app.engines.clinical_engine.lft_engine import LFTEngine
import logging

logger = logging.getLogger(__name__)


class LFTService:
    """LFT analysis service."""
    
    def __init__(self):
        self.extractor = LFTExtractor()
        self.engine = LFTEngine()
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze LFT from text."""
        values = self.extractor.extract(text)
        
        if not values:
            return {
                'success': False,
                'message': 'No LFT values found in the text',
                'results': {}
            }
        
        return self.analyze_values(values)
    
    def analyze_values(self, values: Dict[str, float]) -> Dict[str, Any]:
        """Analyze LFT values."""
        results = self.engine.evaluate(values)
        risks = self.engine.get_disease_risks(results)
        
        total_params = len(results)
        abnormal_count = sum(1 for v in results.values() if v['status'] not in ['Normal', 'Good result'])
        
        if abnormal_count == 0:
            overall_status = "Normal"
            status_color = "green"
        elif abnormal_count <= 3:
            overall_status = "Minor Abnormalities"
            status_color = "yellow"
        elif abnormal_count <= 6:
            overall_status = "Moderate Abnormalities"
            status_color = "orange"
        else:
            overall_status = "Significant Abnormalities"
            status_color = "red"
        
        return {
            'success': True,
            'message': 'LFT analysis completed',
            'overall_status': overall_status,
            'status_color': status_color,
            'total_parameters': total_params,
            'abnormal_count': abnormal_count,
            'normal_count': total_params - abnormal_count,
            'results': results,
            'disease_risks': risks
        }