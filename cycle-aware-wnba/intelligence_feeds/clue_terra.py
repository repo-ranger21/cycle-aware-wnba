"""
Clue Data Ingestion via Terra API

This module provides integration with Clue menstrual cycle tracking data
through Terra API for cycle-aware analysis.

Privacy Notice: All data handling follows strict anonymization and 
consent-based practices. No personal identifiers are stored.
"""

import pandas as pd
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from .base import DataSourceBase

logger = logging.getLogger(__name__)


class ClueDataSource(DataSourceBase):
    """
    Clue cycle data ingestion via Terra API.
    
    Fetches anonymized menstrual cycle data including:
    - Cycle length and patterns
    - Flow intensity and duration  
    - Symptom tracking (cramps, mood, etc.)
    - Ovulation predictions
    """
    
    def __init__(self, api_key: str, terra_endpoint: str = "https://api.tryterra.co/v2"):
        """
        Initialize Clue data source with Terra API credentials.
        
        Args:
            api_key: Terra API key for accessing Clue data
            terra_endpoint: Base URL for Terra API
        """
        ethical_compliance = {
            'consent_verified': True,
            'privacy_level': 'anonymized',
            'data_retention': '90_days',
            'medical_grade': False,  # For research/awareness only
            'audit_trail': True
        }
        
        super().__init__("Clue via Terra API", ethical_compliance)
        
        self.api_key = api_key
        self.terra_endpoint = terra_endpoint
        self.headers = {
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        }
    
    def fetch_data(self, player_ids: List[str], date_range: tuple, **kwargs) -> pd.DataFrame:
        """
        Fetch Clue cycle data for specified players and date range.
        
        Args:
            player_ids: List of anonymized player Terra user IDs
            date_range: Tuple of (start_date, end_date)
            **kwargs: Additional parameters like data_types
            
        Returns:
            DataFrame with cycle tracking data
        """
        self.log_access("fetch_cycle_data", len(player_ids), date_range)
        
        start_date, end_date = date_range
        data_types = kwargs.get('data_types', ['menstruation', 'fertility'])
        
        all_data = []
        
        for player_id in player_ids:
            try:
                # Fetch menstruation data
                menstruation_data = self._fetch_menstruation_data(
                    player_id, start_date, end_date
                )
                
                # Fetch fertility/ovulation data  
                fertility_data = self._fetch_fertility_data(
                    player_id, start_date, end_date
                )
                
                # Merge and process data for this player
                player_data = self._process_player_data(
                    player_id, menstruation_data, fertility_data
                )
                
                if not player_data.empty:
                    all_data.append(player_data)
                    
            except Exception as e:
                logger.error(f"Error fetching data for player {player_id}: {str(e)}")
                continue
        
        if not all_data:
            return pd.DataFrame()
            
        combined_df = pd.concat(all_data, ignore_index=True)
        return self.anonymize_data(combined_df)
    
    def _fetch_menstruation_data(self, player_id: str, start_date: datetime, 
                                end_date: datetime) -> Dict:
        """Fetch menstruation data from Terra API."""
        endpoint = f"{self.terra_endpoint}/menstruation"
        params = {
            'user_id': player_id,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d')
        }
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Terra API request failed: {str(e)}")
            return {}
    
    def _fetch_fertility_data(self, player_id: str, start_date: datetime,
                             end_date: datetime) -> Dict:
        """Fetch fertility/ovulation data from Terra API."""
        endpoint = f"{self.terra_endpoint}/fertility"
        params = {
            'user_id': player_id,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d')
        }
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Terra API request failed: {str(e)}")
            return {}
    
    def _process_player_data(self, player_id: str, menstruation_data: Dict,
                           fertility_data: Dict) -> pd.DataFrame:
        """Process raw Terra API data into standardized format."""
        records = []
        
        # Process menstruation periods
        for period in menstruation_data.get('data', {}).get('periods', []):
            record = {
                'player_id': player_id,
                'date': period.get('start_time', '').split('T')[0],
                'cycle_day': period.get('cycle_day'),
                'flow_intensity': period.get('flow', 0),  # 0-4 scale
                'period_active': True,
                'cycle_length': period.get('cycle_length_days'),
                'symptoms_cramps': period.get('symptoms', {}).get('cramps', 0),
                'symptoms_mood': period.get('symptoms', {}).get('mood_change', 0),
                'data_type': 'menstruation'
            }
            records.append(record)
        
        # Process fertility/ovulation data  
        for fertility in fertility_data.get('data', {}).get('fertility_windows', []):
            record = {
                'player_id': player_id,
                'date': fertility.get('date', '').split('T')[0],
                'ovulation_probability': fertility.get('ovulation_probability', 0),
                'fertility_window': fertility.get('fertile', False),
                'cervical_fluid': fertility.get('cervical_fluid_score', 0),
                'basal_temp': fertility.get('temperature', None),
                'data_type': 'fertility'
            }
            records.append(record)
        
        if not records:
            return pd.DataFrame()
            
        df = pd.DataFrame(records)
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        return df.dropna(subset=['date'])
    
    def validate_data(self, df: pd.DataFrame) -> bool:
        """
        Validate Clue data quality and ethical compliance.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Boolean indicating validation success
        """
        if df.empty:
            return False
            
        required_columns = ['player_id', 'date', 'data_source']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            logger.error(f"Missing required columns: {missing_columns}")
            return False
        
        # Validate data ranges
        if 'flow_intensity' in df.columns:
            invalid_flow = df[
                (df['flow_intensity'] < 0) | (df['flow_intensity'] > 4)
            ]
            if not invalid_flow.empty:
                logger.warning(f"Invalid flow intensity values: {len(invalid_flow)} records")
        
        # Check for future dates (data quality issue)
        future_dates = df[df['date'] > datetime.now()]
        if not future_dates.empty:
            logger.warning(f"Found {len(future_dates)} records with future dates")
            return False
        
        return True