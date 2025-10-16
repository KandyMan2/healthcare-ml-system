"""Models Module

This module contains machine learning model definitions, training workflows,
and inference capabilities for the Healthcare ML System.

Key Responsibilities:
    - Define model architectures (traditional ML and deep learning)
    - Implement training and validation workflows
    - Handle model versioning and serialization
    - Provide inference and prediction capabilities
    - Track and log model performance metrics
    - Support model interpretability and explainability

Design Rationale:
    Separating models from data processing provides several critical benefits
    for healthcare ML development:
    
    1. Modularity: Data scientists can iterate on models independently from
       data engineering work, enabling parallel development
    
    2. Experimentation: Easy to test multiple model architectures, compare
       performance, and conduct A/B testing without affecting data pipeline
    
    3. Versioning: Models can be versioned independently, crucial for:
       - Regulatory compliance and audit trails
       - Rolling back to previous model versions if needed
       - Tracking performance degradation over time
    
    4. Deployment Flexibility: Models can be deployed on different infrastructure
       (CPU/GPU) and scaled independently from data processing
    
    5. Explainability: Healthcare decisions require interpretable models.
       This module provides tools for model transparency and explanation
    
    6. Safety: Separation allows for thorough testing of model predictions
       before deployment in clinical settings

Typical Usage:
    >>> from src.models import HealthcareModel, ModelTrainer, ModelEvaluator
    >>> 
    >>> # Initialize and train a model
    >>> model = HealthcareModel(model_type='random_forest')
    >>> trainer = ModelTrainer(model)
    >>> trainer.train(training_data, validation_data)
    >>> 
    >>> # Evaluate model performance
    >>> evaluator = ModelEvaluator(model)
    >>> metrics = evaluator.evaluate(test_data)
    >>> 
    >>> # Make predictions
    >>> predictions = model.predict(new_patient_data)
    >>> explanations = model.explain_prediction(predictions)

Components:
    HealthcareModel: Base class for all healthcare ML models
    ModelTrainer: Handles model training workflows
    ModelEvaluator: Evaluates model performance with healthcare-specific metrics
    ModelRegistry: Manages model versions and metadata
    ExplainabilityEngine: Provides model interpretability tools

Healthcare-Specific Considerations:
    - Models must be explainable for clinical acceptance
    - Performance metrics include clinical relevance (not just accuracy)
    - Bias detection and fairness across patient demographics
    - Uncertainty quantification for risk-sensitive predictions
    - Continuous monitoring for model drift in production

For detailed architecture, see docs/architecture.md
"""

__version__ = "0.1.0"

# Module exports - will be populated as components are developed
__all__ = [
    "HealthcareModel",
    "ModelTrainer",
    "ModelEvaluator",
    "ModelRegistry",
    "ExplainabilityEngine",
]
