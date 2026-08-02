# app/services/lipid_service.py
"""
Lipid Analysis Service
"""

from typing import Dict, Any, Optional
from app.engines.clinical_engine.lipid_engine import LipidEngine
import logging

logger = logging.getLogger(__name__)


class LipidService:
    """Lipid analysis service."""
    
    def __init__(self):
        self.engine = LipidEngine()
    
    def analyze(self, values: Dict[str, float]) -> Dict[str, Any]:
        """
        Analyze lipid values.
        
        Args:
            values: Dictionary of lipid parameter values
            
        Returns:
            Analysis results
        """
        try:
            # Evaluate rules
            results = self.engine.evaluate(values)
            
            # Calculate statistics
            total_params = len(results)
            abnormal_count = sum(1 for v in results.values() if v.get('status') not in ['Normal', 'Good result'])
            normal_count = total_params - abnormal_count
            
            # Determine overall status
            if abnormal_count == 0:
                overall_status = "Normal"
                status_color = "green"
            elif abnormal_count <= 2:
                overall_status = "Minor Abnormalities"
                status_color = "yellow"
            else:
                overall_status = "Significant Abnormalities"
                status_color = "red"
            
            return {
                'success': True,
                'message': 'Lipid analysis completed',
                'overall_status': overall_status,
                'status_color': status_color,
                'total_parameters': total_params,
                'abnormal_count': abnormal_count,
                'normal_count': normal_count,
                'results': results,
                'category': 'lipid'
            }
            
        except Exception as e:
            logger.error(f"Lipid analysis failed: {e}")
            return {
                'success': False,
                'message': f'Lipid analysis failed: {str(e)}',
                'results': {}
            }
    
    def analyze_with_risk(self, values: Dict[str, float]) -> Dict[str, Any]:
        """
        Analyze lipid values with disease risk detection.
        
        Args:
            values: Dictionary of lipid parameter values
            
        Returns:
            Analysis results with disease risks
        """
        result = self.analyze(values)
        
        if result.get('success'):
            # Get disease risks
            risks = self.engine.get_disease_risks(result.get('results', {}))
            result['disease_risks'] = risks
            
            # Get recommendations
            recommendations = self.engine.get_recommendations(result.get('results', {}))
            result['recommendations'] = recommendations
        
        return result