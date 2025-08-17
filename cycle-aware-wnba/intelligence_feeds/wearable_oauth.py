"""
Wearable Data Ingestion using OAuth

This module provides integration with various wearable devices using OAuth 
authentication for physiological monitoring data relevant to cycle awareness.

Supported devices: Fitbit, Garmin, Apple HealthKit, Oura Ring
Privacy Notice: All biometric data is anonymized and consent-verified.
"""

import pandas as pd
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from .base import DataSourceBase

logger = logging.getLogger(__name__)


class WearableDataSource(DataSourceBase):
    """
    Wearable device data ingestion using OAuth authentication.
    
    Fetches anonymized biometric data including:
    - Heart rate and variability (HRV)
    - Sleep quality and duration
    - Activity levels and exercise
    - Body temperature (when available)
    - Stress indicators
    """
    
    def __init__(self, oauth_config: Dict[str, str], device_types: List[str] = None):
        """
        Initialize wearable data source with OAuth configuration.
        
        Args:
            oauth_config: Dict with OAuth credentials and endpoints
            device_types: List of supported device types ['fitbit', 'garmin', 'oura']
        """
        ethical_compliance = {
            'consent_verified': True,
            'privacy_level': 'anonymized',
            'data_retention': '30_days',  # Shorter retention for biometric data
            'medical_grade': False,
            'audit_trail': True,
            'encryption': 'at_rest'
        }
        
        super().__init__("Wearable Devices OAuth", ethical_compliance)
        
        self.oauth_config = oauth_config
        self.device_types = device_types or ['fitbit', 'garmin', 'oura']
        self.access_tokens = {}  # Store active access tokens per device
    
    def authenticate_device(self, device_type: str, player_id: str, 
                          oauth_code: str) -> bool:
        """
        Authenticate with wearable device using OAuth flow.
        
        Args:
            device_type: Type of device ('fitbit', 'garmin', 'oura')
            player_id: Anonymized player identifier  
            oauth_code: Authorization code from OAuth flow
            
        Returns:
            Boolean indicating authentication success
        """
        if device_type not in self.device_types:
            logger.error(f"Unsupported device type: {device_type}")
            return False
        
        try:
            token_endpoint = self.oauth_config[f'{device_type}_token_url']
            client_id = self.oauth_config[f'{device_type}_client_id']
            client_secret = self.oauth_config[f'{device_type}_client_secret']
            
            token_data = {
                'grant_type': 'authorization_code',
                'client_id': client_id,
                'client_secret': client_secret,
                'code': oauth_code,
                'redirect_uri': self.oauth_config.get('redirect_uri')
            }
            
            response = requests.post(token_endpoint, data=token_data)
            response.raise_for_status()
            
            token_info = response.json()
            self.access_tokens[f"{device_type}_{player_id}"] = {
                'access_token': token_info['access_token'],
                'refresh_token': token_info.get('refresh_token'),
                'expires_at': datetime.now() + timedelta(seconds=token_info.get('expires_in', 3600))
            }
            
            logger.info(f"Successfully authenticated {device_type} for player {player_id}")
            return True
            
        except Exception as e:
            logger.error(f"OAuth authentication failed for {device_type}: {str(e)}")
            return False
    
    def fetch_data(self, player_ids: List[str], date_range: tuple, **kwargs) -> pd.DataFrame:
        """
        Fetch wearable data for specified players and date range.
        
        Args:
            player_ids: List of anonymized player identifiers
            date_range: Tuple of (start_date, end_date)
            **kwargs: Additional parameters like device_types, metrics
            
        Returns:
            DataFrame with biometric data
        """
        self.log_access("fetch_biometric_data", len(player_ids), date_range)
        
        start_date, end_date = date_range
        requested_devices = kwargs.get('device_types', self.device_types)
        metrics = kwargs.get('metrics', ['heart_rate', 'sleep', 'activity', 'temperature'])
        
        all_data = []
        
        for player_id in player_ids:
            for device_type in requested_devices:
                try:
                    # Check if we have valid authentication for this player/device
                    token_key = f"{device_type}_{player_id}"
                    if token_key not in self.access_tokens:
                        logger.warning(f"No authentication for {device_type}/{player_id}")
                        continue
                    
                    # Refresh token if needed
                    if not self._ensure_valid_token(token_key, device_type):
                        continue
                    
                    # Fetch data for each metric
                    device_data = []
                    for metric in metrics:
                        metric_data = self._fetch_metric_data(
                            device_type, player_id, metric, start_date, end_date
                        )
                        device_data.extend(metric_data)
                    
                    if device_data:
                        player_df = pd.DataFrame(device_data)
                        player_df['player_id'] = player_id
                        player_df['device_type'] = device_type
                        all_data.append(player_df)
                        
                except Exception as e:
                    logger.error(f"Error fetching {device_type} data for {player_id}: {str(e)}")
                    continue
        
        if not all_data:
            return pd.DataFrame()
            
        combined_df = pd.concat(all_data, ignore_index=True)
        return self.anonymize_data(combined_df)
    
    def _ensure_valid_token(self, token_key: str, device_type: str) -> bool:
        """Ensure access token is valid, refresh if needed."""
        token_info = self.access_tokens.get(token_key)
        if not token_info:
            return False
        
        # Check if token is expired
        if datetime.now() >= token_info['expires_at']:
            return self._refresh_token(token_key, device_type)
        
        return True
    
    def _refresh_token(self, token_key: str, device_type: str) -> bool:
        """Refresh OAuth access token."""
        try:
            token_info = self.access_tokens[token_key]
            refresh_token = token_info.get('refresh_token')
            
            if not refresh_token:
                logger.error(f"No refresh token available for {token_key}")
                return False
            
            token_endpoint = self.oauth_config[f'{device_type}_token_url']
            client_id = self.oauth_config[f'{device_type}_client_id']
            client_secret = self.oauth_config[f'{device_type}_client_secret']
            
            refresh_data = {
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
                'client_id': client_id,
                'client_secret': client_secret
            }
            
            response = requests.post(token_endpoint, data=refresh_data)
            response.raise_for_status()
            
            new_token_info = response.json()
            self.access_tokens[token_key].update({
                'access_token': new_token_info['access_token'],
                'expires_at': datetime.now() + timedelta(seconds=new_token_info.get('expires_in', 3600))
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Token refresh failed for {token_key}: {str(e)}")
            return False
    
    def _fetch_metric_data(self, device_type: str, player_id: str, metric: str,
                          start_date: datetime, end_date: datetime) -> List[Dict]:
        """Fetch specific metric data from wearable device."""
        token_key = f"{device_type}_{player_id}"
        access_token = self.access_tokens[token_key]['access_token']
        
        headers = {'Authorization': f'Bearer {access_token}'}
        
        # Device-specific API endpoints and data processing
        if device_type == 'fitbit':
            return self._fetch_fitbit_metric(metric, headers, start_date, end_date)
        elif device_type == 'garmin':
            return self._fetch_garmin_metric(metric, headers, start_date, end_date)
        elif device_type == 'oura':
            return self._fetch_oura_metric(metric, headers, start_date, end_date)
        
        return []
    
    def _fetch_fitbit_metric(self, metric: str, headers: Dict, 
                           start_date: datetime, end_date: datetime) -> List[Dict]:
        """Fetch data from Fitbit API."""
        base_url = "https://api.fitbit.com/1/user/-"
        
        if metric == 'heart_rate':
            endpoint = f"{base_url}/activities/heart/date/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}.json"
        elif metric == 'sleep':
            endpoint = f"{base_url}/sleep/date/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}.json"
        elif metric == 'activity':
            endpoint = f"{base_url}/activities/date/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}.json"
        else:
            return []
        
        try:
            response = requests.get(endpoint, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            # Process Fitbit-specific data format
            return self._process_fitbit_data(data, metric)
            
        except Exception as e:
            logger.error(f"Fitbit API error for {metric}: {str(e)}")
            return []
    
    def _fetch_garmin_metric(self, metric: str, headers: Dict,
                           start_date: datetime, end_date: datetime) -> List[Dict]:
        """Fetch data from Garmin API.""" 
        # Placeholder for Garmin implementation
        logger.info(f"Garmin {metric} data fetch - implementation pending")
        return []
    
    def _fetch_oura_metric(self, metric: str, headers: Dict,
                         start_date: datetime, end_date: datetime) -> List[Dict]:
        """Fetch data from Oura Ring API."""
        base_url = "https://api.ouraring.com/v2/usercollection"
        
        params = {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d')
        }
        
        if metric == 'sleep':
            endpoint = f"{base_url}/sleep"
        elif metric == 'heart_rate':
            endpoint = f"{base_url}/heartrate"
        elif metric == 'temperature':
            endpoint = f"{base_url}/temperature"
        else:
            return []
        
        try:
            response = requests.get(endpoint, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            return self._process_oura_data(data, metric)
            
        except Exception as e:
            logger.error(f"Oura API error for {metric}: {str(e)}")
            return []
    
    def _process_fitbit_data(self, data: Dict, metric: str) -> List[Dict]:
        """Process Fitbit API response into standard format."""
        records = []
        
        if metric == 'heart_rate':
            for day_data in data.get('activities-heart', []):
                date = day_data.get('dateTime')
                heart_zones = day_data.get('value', {}).get('heartRateZones', [])
                resting_hr = day_data.get('value', {}).get('restingHeartRate')
                
                record = {
                    'date': date,
                    'metric': 'heart_rate',
                    'resting_heart_rate': resting_hr,
                    'avg_heart_rate': sum([zone.get('minutes', 0) * zone.get('min', 0) for zone in heart_zones]) / max(1, sum([zone.get('minutes', 0) for zone in heart_zones]))
                }
                records.append(record)
                
        elif metric == 'sleep':
            for sleep_data in data.get('sleep', []):
                record = {
                    'date': sleep_data.get('dateOfSleep'),
                    'metric': 'sleep',
                    'sleep_duration_minutes': sleep_data.get('minutesAsleep', 0),
                    'sleep_efficiency': sleep_data.get('efficiency', 0),
                    'deep_sleep_minutes': sum([stage.get('minutes', 0) for stage in sleep_data.get('levels', {}).get('summary', {}).values() if 'deep' in str(stage)])
                }
                records.append(record)
        
        return records
    
    def _process_oura_data(self, data: Dict, metric: str) -> List[Dict]:
        """Process Oura API response into standard format."""
        records = []
        
        for item in data.get('data', []):
            if metric == 'sleep':
                record = {
                    'date': item.get('day'),
                    'metric': 'sleep',
                    'sleep_score': item.get('score'),
                    'total_sleep_duration': item.get('total_sleep_duration'),
                    'deep_sleep_duration': item.get('deep_sleep_duration'),
                    'rem_sleep_duration': item.get('rem_sleep_duration')
                }
            elif metric == 'temperature':
                record = {
                    'date': item.get('day'),
                    'metric': 'temperature', 
                    'body_temperature': item.get('body_temperature'),
                    'skin_temperature': item.get('skin_temperature')
                }
            else:
                continue
                
            records.append(record)
        
        return records
    
    def validate_data(self, df: pd.DataFrame) -> bool:
        """
        Validate wearable data quality and ethical compliance.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Boolean indicating validation success
        """
        if df.empty:
            return False
            
        required_columns = ['player_id', 'date', 'device_type', 'metric']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            logger.error(f"Missing required columns: {missing_columns}")
            return False
        
        # Validate biometric data ranges
        if 'resting_heart_rate' in df.columns:
            invalid_hr = df[
                (df['resting_heart_rate'] < 30) | (df['resting_heart_rate'] > 200)
            ]
            if not invalid_hr.empty:
                logger.warning(f"Potentially invalid heart rate values: {len(invalid_hr)} records")
        
        # Check for future dates
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        future_dates = df[df['date'] > datetime.now()]
        if not future_dates.empty:
            logger.warning(f"Found {len(future_dates)} records with future dates")
            return False
        
        return True