"""Data Ingestion Module for Healthcare ML System.

This module provides abstraction for data ingestion from multiple sources.

Why Abstraction?
---------------
Healthcare data comes from diverse sources (CSV files, databases, APIs, HL7 feeds,
EHR systems). An abstract base class allows us to define a common interface while
enabling source-specific implementations. This promotes code reusability, testability,
and maintainability while ensuring consistent behavior across all data sources.

Why Multiple Source Types Matter?
----------------------------------
Healthcare organizations use heterogeneous systems. Patient data may originate from:
- Legacy CSV exports from old systems
- Real-time database connections
- REST APIs from third-party providers
- HL7/FHIR message streams

Supporting multiple source types is essential for practical deployment and
interoperability in real-world healthcare environments.

Extensibility and Compliance Rationale:
---------------------------------------
The abstract pattern allows future developers to add new source types (e.g.,
DatabaseIngester, APIIngester) without modifying existing code. Each ingester
implements audit logging for compliance with HIPAA and other regulations,
ensuring all data access is tracked and auditable.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import pandas as pd
import logging
from datetime import datetime
import os


# Configure logging for audit trail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class DataIngester(ABC):
    """Abstract Base Class for Data Ingestion.
    
    Chain-of-Thought Rationale:
    ---------------------------
    This abstract class defines the contract that all data ingesters must follow.
    By using ABC (Abstract Base Class), we enforce that child classes implement
    the required methods, preventing incomplete implementations that could lead
    to runtime errors or security vulnerabilities.
    
    The abstract pattern provides:
    1. **Consistency**: All ingesters have the same interface
    2. **Type Safety**: Static analysis can verify implementations
    3. **Documentation**: Clear contract for future developers
    4. **Compliance**: Enforces audit logging in all implementations
    
    Why This Design?
    ----------------
    Healthcare systems require strict validation and audit trails. By centralizing
    common functionality (audit logging, metadata tracking) in the base class and
    deferring source-specific logic to child classes, we achieve separation of
    concerns while maintaining compliance requirements.
    """
    
    def __init__(self, source_path: str, source_type: str):
        """Initialize the data ingester.
        
        Args:
            source_path: Path or connection string to data source
            source_type: Type of source (e.g., 'csv', 'database', 'api')
        """
        self.source_path = source_path
        self.source_type = source_type
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        self._metadata: Dict[str, Any] = {
            'source_path': source_path,
            'source_type': source_type,
            'ingester_class': self.__class__.__name__,
            'initialized_at': datetime.utcnow().isoformat()
        }
    
    @abstractmethod
    def ingest(self) -> pd.DataFrame:
        """Ingest data from the source.
        
        This method must be implemented by all child classes to handle
        source-specific ingestion logic.
        
        Returns:
            pd.DataFrame: Ingested data
            
        Raises:
            NotImplementedError: If not implemented by child class
        """
        pass
    
    def _log_audit_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """Log audit event for compliance.
        
        Chain-of-Thought: Why Audit Logging?
        ------------------------------------
        HIPAA requires covered entities to maintain audit logs of all access to
        Protected Health Information (PHI). This method creates an auditable
        record of data ingestion events, including:
        - Who accessed the data (system/user)
        - When it was accessed
        - What data source was used
        - Success/failure status
        
        This centralized logging ensures all ingesters maintain compliance
        without duplicating audit code.
        
        Args:
            event_type: Type of audit event (e.g., 'ingestion_start', 'ingestion_complete')
            details: Dictionary containing event-specific details
        """
        audit_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'source_type': self.source_type,
            'source_path': self.source_path,
            'ingester': self.__class__.__name__,
            **details
        }
        self.logger.info(f"AUDIT: {audit_entry}")
    
    def get_metadata(self) -> Dict[str, Any]:
        """Return metadata about the ingestion source.
        
        Returns:
            Dict containing metadata about the data source
        """
        return self._metadata.copy()


class CSVIngester(DataIngester):
    """CSV File Ingester Implementation.
    
    Chain-of-Thought Rationale:
    ---------------------------
    CSV files are one of the most common data exchange formats in healthcare,
    particularly for:
    - Legacy system exports
    - Data warehouse extracts
    - Research data sharing
    - Manual data entry exports
    
    Why Start with CSV?
    -------------------
    CSV is a practical starting point because:
    1. **Ubiquity**: Nearly all healthcare systems can export CSV
    2. **Simplicity**: Easy to validate and test
    3. **Foundation**: Establishes patterns for more complex ingesters
    
    This implementation serves as a reference for future ingester classes
    (DatabaseIngester, APIIngester, etc.).
    
    Compliance Considerations:
    -------------------------
    CSV files may contain PHI. This ingester:
    - Logs all access attempts for audit trails
    - Validates file existence before processing
    - Captures metadata for data lineage tracking
    - Provides error handling for security and reliability
    """
    
    def __init__(self, csv_path: str, **read_csv_kwargs):
        """Initialize CSV ingester.
        
        Args:
            csv_path: Path to CSV file
            **read_csv_kwargs: Additional arguments to pass to pd.read_csv()
        """
        super().__init__(source_path=csv_path, source_type='csv')
        self.read_csv_kwargs = read_csv_kwargs
    
    def ingest(self) -> pd.DataFrame:
        """Ingest data from CSV file.
        
        Chain-of-Thought: Ingestion Process
        -----------------------------------
        1. Log audit event for compliance (start)
        2. Validate file exists (security/error handling)
        3. Read CSV using pandas (actual ingestion)
        4. Capture metadata (row count, columns for data lineage)
        5. Log audit event (completion)
        6. Return data
        
        This step-by-step process ensures:
        - Compliance through audit logging
        - Reliability through validation
        - Transparency through metadata capture
        
        Returns:
            pd.DataFrame: Data loaded from CSV file
            
        Raises:
            FileNotFoundError: If CSV file does not exist
            Exception: For other ingestion errors
        """
        # Audit: Log ingestion start
        self._log_audit_event('ingestion_start', {
            'status': 'initiated',
            'csv_path': self.source_path
        })
        
        try:
            # Validate file exists
            if not os.path.exists(self.source_path):
                self._log_audit_event('ingestion_error', {
                    'status': 'failed',
                    'error': 'FileNotFoundError',
                    'message': f'CSV file not found: {self.source_path}'
                })
                raise FileNotFoundError(f"CSV file not found: {self.source_path}")
            
            # Ingest CSV data
            self.logger.info(f"Reading CSV from: {self.source_path}")
            df = pd.read_csv(self.source_path, **self.read_csv_kwargs)
            
            # Update metadata with ingestion results
            self._metadata.update({
                'rows_ingested': len(df),
                'columns': list(df.columns),
                'ingestion_timestamp': datetime.utcnow().isoformat(),
                'file_size_bytes': os.path.getsize(self.source_path)
            })
            
            # Audit: Log successful completion
            self._log_audit_event('ingestion_complete', {
                'status': 'success',
                'rows_ingested': len(df),
                'columns_count': len(df.columns)
            })
            
            return df
            
        except Exception as e:
            # Audit: Log error
            self._log_audit_event('ingestion_error', {
                'status': 'failed',
                'error': type(e).__name__,
                'message': str(e)
            })
            raise


# Placeholder for future ingester implementations:
# - DatabaseIngester: For SQL/NoSQL database connections
# - APIIngester: For REST/GraphQL API data sources
# - HL7Ingester: For healthcare-specific HL7 message streams
# - FHIRIngester: For FHIR-compliant data sources
# Each will follow the same abstract pattern for consistency and compliance.
