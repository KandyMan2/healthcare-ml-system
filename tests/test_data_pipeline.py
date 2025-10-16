"""Unit tests for data pipeline validation components.

This test module ensures the DataValidator correctly handles patient data
according to HIPAA compliance requirements, schema validation, and PHI detection.
These tests are critical for:
- Regulatory compliance (HIPAA)
- Data quality assurance
- System reliability and maintainability
- Reproducible validation logic
"""

import unittest
import json
import os
from pathlib import Path
from src.data_pipeline.validation import DataValidator


class TestDataValidator(unittest.TestCase):
    """Test suite for DataValidator class.
    
    Chain-of-thought rationale:
    Testing the DataValidator is essential for healthcare ML systems because:
    1. It ensures data quality before model training
    2. It prevents invalid data from entering the pipeline
    3. It protects patient privacy by detecting PHI
    4. It provides clear error messages for debugging
    """
    
    @classmethod
    def setUpClass(cls):
        """Load the patient schema once for all tests.
        
        Why this matters:
        - Reduces redundant file I/O operations
        - Ensures all tests use the same schema version
        - Improves test execution speed
        """
        schema_path = Path(__file__).parent.parent / 'data' / 'schemas' / 'patient_schema.json'
        with open(schema_path, 'r') as f:
            cls.schema = json.load(f)
        cls.validator = DataValidator(cls.schema)
    
    def test_valid_record_ingestion(self):
        """Test that a fully compliant patient record passes validation.
        
        Compliance rationale:
        - Valid records must be accepted to avoid false rejections
        - This ensures legitimate patient data flows through the pipeline
        - Prevents data loss from overly strict validation
        
        Reproducibility:
        - Uses a deterministic, well-formed test record
        - Any failure indicates a regression in validation logic
        """
        valid_record = {
            "patient_id": "P123456",
            "age": 45,
            "gender": "F",
            "diagnosis_code": "E11.9",
            "medication_list": ["metformin", "lisinopril"],
            "lab_results": {
                "glucose": 120,
                "hba1c": 6.5
            },
            "visit_date": "2025-10-15"
        }
        
        result = self.validator.validate(valid_record)
        
        self.assertTrue(result['is_valid'], 
                       f"Valid record should pass validation. Errors: {result.get('errors', [])}")
        self.assertEqual(len(result.get('errors', [])), 0,
                        "Valid record should have no validation errors")
    
    def test_schema_validation_missing_required_field(self):
        """Test that records missing required fields are rejected.
        
        Compliance rationale:
        - Incomplete records can lead to biased model predictions
        - Missing critical fields (e.g., diagnosis_code) makes data unusable
        - Early detection prevents downstream pipeline failures
        
        Maintainability:
        - Clear error messages help developers identify data issues quickly
        - Prevents silent failures that are costly to debug
        """
        invalid_record = {
            "patient_id": "P123456",
            "age": 45,
            "gender": "F",
            # Missing required field: diagnosis_code
            "medication_list": ["metformin"],
            "visit_date": "2025-10-15"
        }
        
        result = self.validator.validate(invalid_record)
        
        self.assertFalse(result['is_valid'],
                        "Record missing required field should fail validation")
        self.assertGreater(len(result.get('errors', [])), 0,
                          "Should report at least one validation error")
        # Check that error message mentions the missing field
        error_messages = ' '.join(result.get('errors', []))
        self.assertIn('diagnosis_code', error_messages.lower(),
                     "Error should identify the missing 'diagnosis_code' field")
    
    def test_schema_validation_incorrect_type(self):
        """Test that records with incorrect data types are rejected.
        
        Compliance rationale:
        - Type errors can cause runtime exceptions in downstream processes
        - Ensures data conforms to expected structure for ML models
        - Prevents type coercion bugs that lead to incorrect predictions
        
        Reproducibility:
        - Type consistency is fundamental to reproducible ML pipelines
        - Prevents subtle bugs from inconsistent data representations
        """
        invalid_record = {
            "patient_id": "P123456",
            "age": "forty-five",  # Should be integer, not string
            "gender": "F",
            "diagnosis_code": "E11.9",
            "medication_list": ["metformin"],
            "visit_date": "2025-10-15"
        }
        
        result = self.validator.validate(invalid_record)
        
        self.assertFalse(result['is_valid'],
                        "Record with incorrect type should fail validation")
        self.assertGreater(len(result.get('errors', [])), 0,
                          "Should report type validation error")
        error_messages = ' '.join(result.get('errors', []))
        self.assertIn('age', error_messages.lower(),
                     "Error should identify the 'age' field with incorrect type")
    
    def test_phi_detection_placeholder(self):
        """Placeholder test for PHI (Protected Health Information) detection.
        
        Compliance rationale (HIPAA):
        - PHI detection is CRITICAL for HIPAA compliance
        - Must identify 18 types of identifiers: names, SSNs, medical record numbers, etc.
        - Prevents accidental exposure of patient identities
        - Required for de-identification before data sharing or research use
        
        Why a placeholder now:
        - PHI detection logic is complex and requires careful implementation
        - Regex patterns, NLP models, or external libraries may be needed
        - This test documents the requirement and will be implemented next
        
        Maintainability:
        - Explicit placeholder prevents forgetting this critical feature
        - Documents the importance for future developers
        - Can be easily found with TODO/FIXME searches
        """
        # TODO: Implement PHI detection logic in DataValidator
        # FIXME: This is a critical security feature required for HIPAA compliance
        
        record_with_potential_phi = {
            "patient_id": "P123456",
            "age": 45,
            "gender": "F",
            "diagnosis_code": "E11.9",
            "notes": "Patient John Doe reported symptoms.",  # Contains name (PHI)
            "medication_list": ["metformin"],
            "visit_date": "2025-10-15"
        }
        
        # Placeholder assertion - will be replaced with actual PHI detection
        with self.assertRaises(NotImplementedError,
                              msg="PHI detection must be implemented before production use"):
            self.validator.detect_phi(record_with_potential_phi)
    
    def test_phi_detection_ssn_placeholder(self):
        """Placeholder test for SSN detection in patient records.
        
        Compliance rationale:
        - SSNs are explicit PHI under HIPAA Privacy Rule
        - Must be detected and flagged before any data processing
        - Accidental SSN exposure can result in severe penalties
        
        Implementation notes:
        - Should detect formats: 123-45-6789, 123456789
        - Should handle edge cases: partial SSNs, masked SSNs (XXX-XX-1234)
        - Should minimize false positives from similar number patterns
        """
        record_with_ssn = {
            "patient_id": "P123456",
            "age": 45,
            "gender": "F",
            "diagnosis_code": "E11.9",
            "ssn": "123-45-6789",  # Explicit SSN field (should never exist)
            "medication_list": ["metformin"],
            "visit_date": "2025-10-15"
        }
        
        # Placeholder - will verify PHI detection identifies SSNs
        with self.assertRaises(NotImplementedError,
                              msg="SSN detection must be implemented for HIPAA compliance"):
            self.validator.detect_phi(record_with_ssn)
    
    def test_batch_validation_reproducibility(self):
        """Test that batch validation produces consistent results.
        
        Reproducibility rationale:
        - Validation results must be deterministic
        - Same input data should always produce same validation outcome
        - Critical for debugging and auditing data quality issues
        
        Maintainability:
        - Batch processing is common in ML pipelines
        - Ensures validation scales to production workloads
        - Tests that validator is stateless (no side effects between records)
        """
        test_records = [
            {
                "patient_id": "P001",
                "age": 30,
                "gender": "M",
                "diagnosis_code": "J45.20",
                "medication_list": ["albuterol"],
                "visit_date": "2025-10-01"
            },
            {
                "patient_id": "P002",
                "age": 55,
                "gender": "F",
                "diagnosis_code": "I10",
                "medication_list": ["lisinopril", "amlodipine"],
                "visit_date": "2025-10-02"
            },
            {
                "patient_id": "P003",
                "age": "invalid",  # Invalid type
                "gender": "F",
                "diagnosis_code": "E11.9",
                "medication_list": ["metformin"],
                "visit_date": "2025-10-03"
            }
        ]
        
        # Validate twice to ensure reproducibility
        results_first = [self.validator.validate(record) for record in test_records]
        results_second = [self.validator.validate(record) for record in test_records]
        
        # Check that results are identical
        for i, (first, second) in enumerate(zip(results_first, results_second)):
            self.assertEqual(first['is_valid'], second['is_valid'],
                           f"Record {i} validation result should be reproducible")
            self.assertEqual(first.get('errors', []), second.get('errors', []),
                           f"Record {i} error messages should be identical")
        
        # Verify expected outcomes
        self.assertTrue(results_first[0]['is_valid'], "First record should be valid")
        self.assertTrue(results_first[1]['is_valid'], "Second record should be valid")
        self.assertFalse(results_first[2]['is_valid'], "Third record should be invalid (type error)")


if __name__ == '__main__':
    unittest.main()
