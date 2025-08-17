"""
Base class for all data sources in the intelligence feeds module.
Provides common interface and ethical data handling guidelines.
"""

import pandas as pd
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataSourceBase(ABC):
    """
    Abstract base class for all data sources.
    
    Enforces privacy-first, ethical data handling practices and provides
    standardized interface for cycle-aware data ingestion.
    """
    
    def __init__(self, name: str, ethical_compliance: Dict[str, Any] = None):
        """
        Initialize data source with ethical compliance metadata.
        
        Args:
            name: Human-readable name of the data source
            ethical_compliance: Dict with consent, privacy, and audit info
        """
        self.name = name
        self.ethical_compliance = ethical_compliance or {}
        self.created_at = datetime.now()
        
        # Validate ethical compliance requirements
        self._validate_ethical_compliance()
        
    def _validate_ethical_compliance(self):
        """Validate that ethical compliance requirements are met."""
        required_keys = ['consent_verified', 'privacy_level', 'data_retention']
        for key in required_keys:
            if key not in self.ethical_compliance:
                logger.warning(f"Missing ethical compliance key: {key}")
    
    @abstractmethod
    def fetch_data(self, player_ids: List[str], date_range: tuple, **kwargs) -> pd.DataFrame:
        """
        Fetch data for specified players and date range.
        
        Args:
            player_ids: List of anonymized player identifiers
            date_range: Tuple of (start_date, end_date) as datetime objects
            **kwargs: Additional source-specific parameters
            
        Returns:
            DataFrame with standardized columns including:
            - player_id (anonymized)
            - date
            - source_name
            - Any source-specific data columns
        """
        pass
    
    @abstractmethod
    def validate_data(self, df: pd.DataFrame) -> bool:
        """
        Validate data quality and ethical compliance.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Boolean indicating if data passes validation
        """
        pass
    
    def anonymize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply additional anonymization to protect athlete privacy.
        
        Args:
            df: DataFrame with potentially identifiable information
            
        Returns:
            DataFrame with enhanced anonymization
        """
        # Remove any potential PII columns
        pii_columns = ['name', 'email', 'phone', 'address', 'ssn']
        df_clean = df.drop(columns=[col for col in pii_columns if col in df.columns])
        
        # Add ethical audit trail
        df_clean['anonymized_at'] = datetime.now()
        df_clean['data_source'] = self.name
        
        return df_clean
    
    def log_access(self, action: str, player_count: int, date_range: tuple):
        """
        Log data access for ethical audit trail.
        
        Args:
            action: Description of the action taken
            player_count: Number of players affected
            date_range: Date range accessed
        """
        logger.info(f"Data Source: {self.name} | Action: {action} | "
                   f"Players: {player_count} | Date Range: {date_range}")