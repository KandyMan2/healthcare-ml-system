"""Data Pipeline Module

This module handles all data-related operations for the Healthcare ML System,
including data ingestion, preprocessing, validation, and transformation.

Key Responsibilities:
    - Ingest raw healthcare data from multiple sources (EHR systems, CSV, databases)
    - Validate data quality, completeness, and format consistency
    - Clean and preprocess data (handle missing values, outliers, normalization)
    - Transform data into ML-ready formats
    - Ensure HIPAA compliance and patient data anonymization
    - Maintain data lineage and audit trails

Design Rationale:
    Healthcare data is inherently complex, often incomplete, and comes from
    disparate sources with varying formats. This module centralizes all data
    handling logic to ensure:
    
    1. Data Quality: Consistent validation and cleaning procedures
    2. Compliance: Built-in privacy controls and audit capabilities
    3. Maintainability: Single source of truth for data processing
    4. Reusability: Shared preprocessing logic across different models
    5. Traceability: Complete data lineage for regulatory requirements

Typical Usage:
    >>> from src.data_pipeline import DataLoader, DataValidator, DataTransformer
    >>> 
    >>> # Load data from source
    >>> loader = DataLoader(source='ehr_system')
    >>> raw_data = loader.load()
    >>> 
    >>> # Validate and clean
    >>> validator = DataValidator()
    >>> clean_data = validator.validate_and_clean(raw_data)
    >>> 
    >>> # Transform for ML
    >>> transformer = DataTransformer()
    >>> ml_ready_data = transformer.transform(clean_data)

Components:
    DataLoader: Handles data ingestion from various sources
    DataValidator: Validates data quality and completeness
    DataCleaner: Cleans and preprocesses raw data
    DataTransformer: Transforms data into ML-ready formats
    PrivacyHandler: Ensures HIPAA compliance and data anonymization

For detailed architecture, see docs/architecture.md
"""

__version__ = "0.1.0"

# Module exports - will be populated as components are developed
__all__ = [
    "DataLoader",
    "DataValidator",
    "DataCleaner",
    "DataTransformer",
    "PrivacyHandler",
]
