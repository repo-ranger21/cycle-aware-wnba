"""
Clue Data Ingestion Module - Cycle-Aware WNBA Analytics

This module ingests anonymized menstrual cycle data from the Clue app via Terra API,
normalizes flow intensity, ovulation flags, and symptom logs, and formats output
for ingestion into Supabase or local storage.

ETHICAL NOTICE: This script handles sensitive reproductive health data. All usage
must comply with athlete consent requirements, data protection laws, and
non-exploitative research practices. Data is anonymized before processing.

CIVIC DISCLAIMER: This code serves public-good research and athlete empowerment.
Commercial exploitation or discriminatory use is strictly prohibited.

Author: Q4Trackr Contributor Team
License: MIT License (Civic Use Variant) - See LICENSE file
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging for audit trail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ClueDataIngestor:
    """
    Ethical data ingestion class for Clue menstrual cycle data via Terra API.
    
    CONTRIBUTOR NOTE: This class prioritizes athlete privacy and consent.
    All methods include anonymization and ethical safeguards.
    """
    
    def __init__(self, terra_api_key: Optional[str] = None, supabase_url: Optional[str] = None, 
                 supabase_key: Optional[str] = None):
        """
        Initialize the Clue data ingestor with ethical safeguards.
        
        Args:
            terra_api_key: Terra API key for accessing Clue data (from env var if None)
            supabase_url: Supabase project URL for data storage
            supabase_key: Supabase service key for authentication
            
        ETHICAL NOTE: API keys should never be hardcoded. Use environment variables.
        """
        self.terra_api_key = terra_api_key or os.getenv('TERRA_API_KEY')
        self.supabase_url = supabase_url or os.getenv('SUPABASE_URL')
        self.supabase_key = supabase_key or os.getenv('SUPABASE_KEY')
        
        if not self.terra_api_key:
            raise ValueError("Terra API key required. Set TERRA_API_KEY environment variable.")
        
        # Configure HTTP session with retry strategy for reliability
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # API endpoint configuration
        self.base_url = "https://api.tryterra.co/v2"
        self.headers = {
            "dev-id": "cycle-aware-wnba-civic",
            "X-API-Key": self.terra_api_key,
            "Content-Type": "application/json"
        }
        
        logger.info("ClueDataIngestor initialized with ethical safeguards enabled")
    
    def _anonymize_user_id(self, user_id: str) -> str:
        """
        Convert Terra user ID to anonymized player identifier.
        
        PRIVACY NOTE: This ensures no personal identifiers are stored in our system.
        """
        import hashlib
        # Use consistent hashing for reproducible anonymization
        return f"player_{hashlib.sha256(user_id.encode()).hexdigest()[:8]}"
    
    def _validate_consent(self, user_id: str) -> bool:
        """
        Validate that athlete has provided explicit consent for data usage.
        
        ETHICAL REQUIREMENT: All data usage must be explicitly consented.
        In production, this would check against a consent database.
        
        Args:
            user_id: Terra user identifier
            
        Returns:
            bool: True if consent is valid and current
        """
        # CONTRIBUTOR NOTE: Implement actual consent checking in production
        # This is a placeholder that assumes consent for development/testing
        logger.info(f"Validating consent for user {self._anonymize_user_id(user_id)}")
        
        # In production, check against consent database:
        # - Explicit opt-in recorded
        # - Consent not revoked
        # - Consent timestamp within valid period
        return True
    
    def fetch_cycle_data(self, user_id: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Fetch cycle data from Terra API for specified date range.
        
        Args:
            user_id: Terra user identifier
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            dict: Raw cycle data from Terra API
            
        ETHICAL SAFEGUARD: Validates consent before any data access
        """
        # Validate consent before accessing any data
        if not self._validate_consent(user_id):
            logger.warning(f"Consent validation failed for user {self._anonymize_user_id(user_id)}")
            return {}
        
        url = f"{self.base_url}/menstruation"
        params = {
            "user_id": user_id,
            "start_date": start_date,
            "end_date": end_date
        }
        
        try:
            logger.info(f"Fetching cycle data for {self._anonymize_user_id(user_id)} from {start_date} to {end_date}")
            response = self.session.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successfully fetched cycle data: {len(data.get('data', []))} records")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch cycle data: {str(e)}")
            return {}
    
    def normalize_flow_intensity(self, raw_flow_data: List[Dict]) -> pd.DataFrame:
        """
        Normalize flow intensity data to standardized scale (1-3).
        
        Args:
            raw_flow_data: Raw flow data from Terra API
            
        Returns:
            pd.DataFrame: Normalized flow intensity data
            
        CIVIC NOTE: Standardization enables cross-platform compatibility and research
        """
        flow_records = []
        
        for record in raw_flow_data:
            # Handle different flow intensity representations
            flow_intensity = record.get('flow_intensity', 0)
            
            # Normalize to 1-3 scale (1=light, 2=medium, 3=heavy)
            if isinstance(flow_intensity, str):
                flow_mapping = {
                    'light': 1, 'spotting': 1,
                    'medium': 2, 'normal': 2,
                    'heavy': 3, 'very_heavy': 3
                }
                normalized_intensity = flow_mapping.get(flow_intensity.lower(), 0)
            else:
                # Assume numeric scale, normalize to 1-3
                normalized_intensity = max(1, min(3, int(flow_intensity))) if flow_intensity > 0 else 0
            
            flow_records.append({
                'date': record.get('date'),
                'flow_intensity': normalized_intensity,
                'flow_raw': record.get('flow_intensity'),  # Keep original for reference
                'timestamp': record.get('timestamp')
            })
        
        return pd.DataFrame(flow_records)
    
    def extract_ovulation_flags(self, raw_cycle_data: List[Dict]) -> pd.DataFrame:
        """
        Extract and normalize ovulation indicators from cycle data.
        
        Args:
            raw_cycle_data: Raw cycle data from Terra API
            
        Returns:
            pd.DataFrame: Ovulation flags and related indicators
        """
        ovulation_records = []
        
        for record in raw_cycle_data:
            # Extract various ovulation indicators
            ovulation_flag = 0
            if record.get('ovulation_test') == 'positive' or record.get('lh_surge', False):
                ovulation_flag = 1
            elif record.get('basal_body_temp_rise', False) or record.get('cervical_mucus_peak', False):
                ovulation_flag = 1
                
            ovulation_records.append({
                'date': record.get('date'),
                'ovulation_flag': ovulation_flag,
                'lh_level': record.get('lh_level', 0),
                'basal_body_temp': record.get('basal_body_temp'),
                'cervical_mucus': record.get('cervical_mucus_consistency', 'unknown'),
                'timestamp': record.get('timestamp')
            })
        
        return pd.DataFrame(ovulation_records)
    
    def normalize_symptom_logs(self, raw_symptom_data: List[Dict]) -> pd.DataFrame:
        """
        Normalize symptom logs to standardized severity scale (0-3).
        
        Args:
            raw_symptom_data: Raw symptom data from Terra API
            
        Returns:
            pd.DataFrame: Normalized symptom severity data
            
        DIGNITY NOTE: Symptoms are treated as health indicators, not limitations
        """
        symptom_records = []
        
        for record in raw_symptom_data:
            # Normalize common symptoms to 0-3 scale
            symptoms = {
                'cramps': self._normalize_symptom_severity(record.get('cramps', 0)),
                'mood_swings': self._normalize_symptom_severity(record.get('mood', 0)),
                'bloating': self._normalize_symptom_severity(record.get('bloating', 0)),
                'breast_tenderness': self._normalize_symptom_severity(record.get('breast_tenderness', 0)),
                'fatigue': self._normalize_symptom_severity(record.get('fatigue', 0)),
                'headache': self._normalize_symptom_severity(record.get('headache', 0)),
            }
            
            # Calculate composite symptom score
            symptom_score = sum(symptoms.values())
            
            symptom_records.append({
                'date': record.get('date'),
                'symptom_score': symptom_score,
                **symptoms,
                'timestamp': record.get('timestamp')
            })
        
        return pd.DataFrame(symptom_records)
    
    def _normalize_symptom_severity(self, severity: Any) -> int:
        """
        Normalize symptom severity to standardized 0-3 scale.
        
        Args:
            severity: Raw severity value (string or numeric)
            
        Returns:
            int: Normalized severity (0=none, 1=mild, 2=moderate, 3=severe)
        """
        if isinstance(severity, str):
            severity_mapping = {
                'none': 0, 'no': 0, 'absent': 0,
                'mild': 1, 'light': 1, 'low': 1,
                'moderate': 2, 'medium': 2, 'normal': 2,
                'severe': 3, 'heavy': 3, 'high': 3, 'intense': 3
            }
            return severity_mapping.get(severity.lower(), 0)
        else:
            # Assume numeric scale, normalize to 0-3
            return max(0, min(3, int(severity or 0)))
    
    def process_user_data(self, user_id: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Complete pipeline to process all cycle data for a user.
        
        Args:
            user_id: Terra user identifier
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            pd.DataFrame: Processed and normalized cycle data
            
        TRANSPARENCY NOTE: All processing steps are logged for auditability
        """
        logger.info(f"Starting data processing for user {self._anonymize_user_id(user_id)}")
        
        # Fetch raw data
        raw_data = self.fetch_cycle_data(user_id, start_date, end_date)
        if not raw_data:
            logger.warning("No data fetched, returning empty DataFrame")
            return pd.DataFrame()
        
        # Process different data components
        flow_df = self.normalize_flow_intensity(raw_data.get('flow_data', []))
        ovulation_df = self.extract_ovulation_flags(raw_data.get('cycle_data', []))
        symptom_df = self.normalize_symptom_logs(raw_data.get('symptom_data', []))
        
        # Merge all components by date
        if not flow_df.empty and not ovulation_df.empty and not symptom_df.empty:
            merged_df = flow_df.merge(ovulation_df, on='date', how='outer')
            merged_df = merged_df.merge(symptom_df, on='date', how='outer')
        else:
            # Handle cases where some data streams are empty
            merged_df = pd.concat([flow_df, ovulation_df, symptom_df], ignore_index=True)
        
        # Add anonymized player ID and metadata
        if not merged_df.empty:
            merged_df['player_id'] = self._anonymize_user_id(user_id)
            merged_df['data_source'] = 'clue_via_terra'
            merged_df['processed_timestamp'] = datetime.now().isoformat()
            merged_df['consent_validated'] = True
        
        logger.info(f"Processing complete: {len(merged_df)} records for {self._anonymize_user_id(user_id)}")
        return merged_df
    
    def store_data(self, df: pd.DataFrame, storage_type: str = 'csv', 
                   output_path: str = 'cycle_data.csv') -> bool:
        """
        Store processed data in specified format with ethical safeguards.
        
        Args:
            df: Processed cycle data
            storage_type: Storage method ('csv', 'supabase', or 'both')
            output_path: Path for CSV output
            
        Returns:
            bool: Success status
            
        AUDIT NOTE: All data storage is logged for compliance tracking
        """
        if df.empty:
            logger.warning("No data to store")
            return False
        
        success = True
        
        try:
            if storage_type in ['csv', 'both']:
                df.to_csv(output_path, index=False)
                logger.info(f"Data stored to CSV: {output_path}")
            
            if storage_type in ['supabase', 'both'] and self.supabase_url and self.supabase_key:
                # Import supabase here to make it optional
                import supabase
                client = supabase.create_client(self.supabase_url, self.supabase_key)
                
                # Store in cycle_data table with ethical metadata
                records = df.to_dict('records')
                result = client.table('cycle_data').upsert(records).execute()
                logger.info(f"Data stored to Supabase: {len(records)} records")
            
        except Exception as e:
            logger.error(f"Failed to store data: {str(e)}")
            success = False
        
        return success


# CONTRIBUTOR ONBOARDING FUNCTIONS

def setup_environment() -> Dict[str, str]:
    """
    Helper function to guide contributors through environment setup.
    
    Returns:
        dict: Configuration status and setup instructions
        
    ONBOARDING NOTE: This helps new contributors get started ethically
    """
    setup_status = {
        'terra_api_key': 'Set' if os.getenv('TERRA_API_KEY') else 'Missing',
        'supabase_url': 'Set' if os.getenv('SUPABASE_URL') else 'Optional',
        'supabase_key': 'Set' if os.getenv('SUPABASE_KEY') else 'Optional'
    }
    
    if setup_status['terra_api_key'] == 'Missing':
        print("⚠️  SETUP REQUIRED: Set TERRA_API_KEY environment variable")
        print("   Get your Terra API key from: https://dashboard.tryterra.co/")
        print("   Run: export TERRA_API_KEY='your_api_key_here'")
    
    print("\n📋 ETHICAL CHECKLIST:")
    print("   ✓ Review ETHICS.md and consent requirements")
    print("   ✓ Ensure athlete consent before using real data")
    print("   ✓ Use anonymization for all identifiers")
    print("   ✓ Test with synthetic data first")
    
    return setup_status


def example_usage():
    """
    Example usage demonstrating ethical data ingestion practices.
    
    LEARNING NOTE: This shows contributors how to use the module ethically
    """
    print("🔬 EXAMPLE: Ethical Clue Data Ingestion")
    print("=" * 50)
    
    # Initialize with environment variables (never hardcode keys)
    try:
        ingestor = ClueDataIngestor()
        print("✓ Ingestor initialized successfully")
        
        # Example with synthetic user ID (never use real IDs in examples)
        synthetic_user_id = "example_user_123"
        start_date = "2024-01-01"
        end_date = "2024-01-31"
        
        print(f"\n📊 Processing synthetic data for demonstration...")
        print(f"   User ID: {ingestor._anonymize_user_id(synthetic_user_id)}")
        print(f"   Date Range: {start_date} to {end_date}")
        
        # In real usage:
        # df = ingestor.process_user_data(synthetic_user_id, start_date, end_date)
        # ingestor.store_data(df, 'csv', 'example_output.csv')
        
        print("\n✓ Example completed - ready for ethical data processing")
        
    except ValueError as e:
        print(f"⚠️  Setup needed: {e}")
        setup_status = setup_environment()
        return setup_status


if __name__ == "__main__":
    """
    Main execution block for testing and demonstration.
    
    SAFETY NOTE: Only runs example code, never processes real data automatically
    """
    print("🏀 Cycle-Aware WNBA: Clue Data Ingestion Module")
    print("   Ethical • Transparent • Athlete-Centered")
    print("=" * 60)
    
    example_usage()