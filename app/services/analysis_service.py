# app/services/analysis_service.py
import sys
from pathlib import Path
from typing import Dict, Any
import logging

PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from clinical.rule_engine import rule_engine
from clinical.combination_engine import combination_engine
from clinical.food_engine import food_engine
from clinical.risk_engine import calculate_overall_risk
from clinical.disease_engine import get_disease_engine
from clinical.mimic_engine import mimic_engine
from clinical.groq_explainer import get_groq_explainer
from clinical.confidence_engine import get_confidence_engine
from clinical.guidelines_engine import get_guidelines_engine
from clinical.medication_engine import get_medication_engine
from clinical.exercise_engine import get_exercise_engine
from clinical.followup_engine import get_followup_engine

# NEW IMPORTS FOR BLOOD TESTS
from clinical.multi_rule_engine import MultiRuleEngine
from extractor.blood_test_parser import BloodTestParser

from parser.file_parser import parse_uploaded_file
from extractor.parameter_extractor import extract_lipid_parameters
from extractor.validator import is_lipid_report

from app.models.schemas import AnalysisResponse

logger = logging.getLogger(__name__)


class AnalysisService:
    def __init__(self):
        self.rule_engine = rule_engine
        self.combination_engine = combination_engine
        self.food_engine = food_engine
        self.risk_engine = calculate_overall_risk
        self.disease_engine = get_disease_engine()
        self.mimic_engine = mimic_engine
        self.groq_explainer = get_groq_explainer()
        self.confidence_engine = get_confidence_engine()
        self.guidelines_engine = get_guidelines_engine()
        self.medication_engine = get_medication_engine()
        self.exercise_engine = get_exercise_engine()
        self.followup_engine = get_followup_engine()
        
        # NEW: Initialize blood test engines
        self.multi_rule_engine = MultiRuleEngine()
        self.blood_parser = BloodTestParser()

    def analyze_from_file(self, file_path: Path) -> AnalysisResponse:
        raw_text, structured = parse_uploaded_file(file_path)
        if not is_lipid_report(raw_text):
            raise ValueError("Not a lipid profile report")
        lipid_values = extract_lipid_parameters(raw_text, structured)
        if not lipid_values:
            raise ValueError("Could not extract lipid parameters")
        return self.analyze_values(lipid_values, {"filename": file_path.name})

    def analyze_values(self, lipid_values: Dict[str, Any], patient_info: Dict = None) -> AnalysisResponse:
        rule_results = self.rule_engine.evaluate(lipid_values)
        combination_findings = self.combination_engine.evaluate(rule_results)
        disease_food_advice = self.food_engine.evaluate(combination_findings)
        analyzed_data = self.risk_engine(rule_results)

        disease_predictions = self.disease_engine.predict(rule_results)
        disease_names = [f.get('result') for f in combination_findings if f.get('result')]
        mimic_evidence = self.mimic_engine.get_evidence(disease_names) if disease_names else {}

        guidelines = []
        for disease in disease_names:
            guidelines.extend(self.guidelines_engine.get_guidelines(disease))
        guidelines = guidelines[:5]

        medication_data = []
        for disease in disease_names:
            meds = self.medication_engine.get_disease_medication_recommendations(disease)
            medication_data.extend(meds)

        exercise_data = self.exercise_engine.evaluate(disease_names)
        followup_tests = self.followup_engine.get_all_recommendations(disease_names)

        confidence = self.confidence_engine.calculate_full_confidence(
            rule_results, disease_predictions, guidelines, mimic_evidence
        )

        ai_explanation = self.groq_explainer.generate_explanation(
            rule_results, disease_predictions, exercise_data,
            medication_data, followup_tests, guidelines,
            confidence, patient_info or {}
        )

        return AnalysisResponse(
            success=True,
            message="Analysis completed successfully",
            parameters=[{
                "parameter": k.replace("_", " ").title(),
                "value": v.get("value"),
                "status": v.get("status"),
                "recommendation": v.get("recommendation"),
                "food": v.get("food", "")
            } for k, v in analyzed_data.items() if isinstance(v, dict)],
            combination_findings=combination_findings,
            disease_predictions=disease_predictions,
            overall_risk=analyzed_data.get("overall_risk", "Unknown"),
            risk_score=analyzed_data.get("risk_score", 0),
            mimic_evidence=mimic_evidence,
            ai_explanation=ai_explanation,
            confidence_score=confidence
        )

    # NEW METHOD: Analyze full blood test
    def analyze_full_blood_test(self, text: str) -> Dict[str, Any]:
        """Analyze complete blood test results from text"""
        
        # Parse blood test values
        blood_values = self.blood_parser.parse(text)
        
        if not blood_values:
            return {
                'success': False,
                'message': 'No blood test values found in the text',
                'results': {}
            }
        
        # Evaluate all parameters
        results = self.multi_rule_engine.evaluate_all(blood_values)
        
        # Get disease risks
        risks = self.multi_rule_engine.get_disease_risks(results)
        
        # Calculate overall risk
        overall_risk = self.multi_rule_engine.calculate_overall_risk(results)
        
        # Group results by category
        categorized_results = {}
        for param, data in results.items():
            category = data.get('category', 'Other')
            if category not in categorized_results:
                categorized_results[category] = []
            categorized_results[category].append({
                'parameter': param,
                'value': data['value'],
                'status': data['status'],
                'recommendation': data['recommendation']
            })
        
        return {
            'success': True,
            'message': 'Blood test analysis completed',
            'overall_risk': overall_risk,
            'categorized_results': categorized_results,
            'all_results': results,
            'disease_risks': risks
        }


_analysis_service = None

def get_analysis_service():
    global _analysis_service
    if _analysis_service is None:
        _analysis_service = AnalysisService()
    return _analysis_service