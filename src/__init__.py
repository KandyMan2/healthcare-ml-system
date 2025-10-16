"""Healthcare ML System - Main Package

This package contains the core components of the Healthcare ML System,
including data pipeline and machine learning models for healthcare analytics.

Modules:
    data_pipeline: Data ingestion, preprocessing, validation, and transformation
    models: ML model definitions, training, and inference capabilities

The system is designed with healthcare-specific considerations including:
- HIPAA compliance and patient privacy
- Data quality validation and traceability
- Model explainability for clinical decision support
- Reproducibility for regulatory requirements

Example:
    >>> from src.data_pipeline import DataPipeline
    >>> from src.models import HealthcareModel
    >>> 
    >>> pipeline = DataPipeline()
    >>> model = HealthcareModel()

For detailed architecture and design rationale, see docs/architecture.md
"""

__version__ = "0.1.0"
__author__ = "Healthcare ML Team"

# Package-level imports for convenient access
# These will be populated as modules are developed
__all__ = [
    "data_pipeline",
    "models",
]
