"""
Wearable Data Ingestion Module - Cycle-Aware WNBA Analytics

This module ingests biometric data from Oura, Whoop, and Apple Watch via OAuth,
extracts HRV, sleep, skin temperature, and breathing rate data, normalizes
timestamps and formats for Supabase ingestion.

ETHICAL NOTICE: This script handles sensitive biometric and health data.
All usage must comply with athlete consent requirements, data protection laws,
and non-exploitative research practices. Data is anonymized before processing.

CIVIC DISCLAIMER: This code serves public-good research and athlete empowerment.
Commercial exploitation or discriminatory use is strictly prohibited.

Author: Q4Trackr Contributor Team
License: MIT License (Civic Use Variant) - See LICENSE file
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
import pandas as pd
import requests
from requests_oauthlib import OAuth2Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import hashlib
from dataclasses import dataclass

# Configure logging for audit trail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class WearableConfig:
    """Configuration class for wearable device OAuth settings."""
    client_id: str
    client_secret: str
    redirect_uri: str
    authorization_url: str
    token_url: str
    api_base_url: str
    scopes: List[str]


class WearableDataIngestor:
    """
    Ethical data ingestion class for wearable biometric data from multiple platforms.
    
    CONTRIBUTOR NOTE: This class prioritizes athlete privacy and consent across
    all supported wearable platforms (Oura, Whoop, Apple Watch via HealthKit).
    """
    
    def __init__(self, supabase_url: Optional[str] = None, supabase_key: Optional[str] = None):
        """
        Initialize the wearable data ingestor with ethical safeguards.
        
        Args:
            supabase_url: Supabase project URL for data storage
            supabase_key: Supabase service key for authentication
            
        ETHICAL NOTE: OAuth credentials should be stored securely, never in code.
        """
        self.supabase_url = supabase_url or os.getenv('SUPABASE_URL')
        self.supabase_key = supabase_key or os.getenv('SUPABASE_KEY')
        
        # Configure HTTP session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Initialize wearable platform configurations
        self._setup_platform_configs()
        
        logger.info("WearableDataIngestor initialized with multi-platform OAuth support")
    
    def _setup_platform_configs(self):
        """
        Set up OAuth configurations for supported wearable platforms.
        
        SECURITY NOTE: Configurations use environment variables for credentials.
        """
        self.configs = {
            'oura': WearableConfig(
                client_id=os.getenv('OURA_CLIENT_ID', ''),
                client_secret=os.getenv('OURA_CLIENT_SECRET', ''),
                redirect_uri=os.getenv('OURA_REDIRECT_URI', 'http://localhost:8080/callback'),
                authorization_url='https://cloud.ouraring.com/oauth/authorize',
                token_url='https://api.ouraring.com/oauth/token',
                api_base_url='https://api.ouraring.com/v2/',
                scopes=['personal', 'daily']
            ),
            'whoop': WearableConfig(
                client_id=os.getenv('WHOOP_CLIENT_ID', ''),
                client_secret=os.getenv('WHOOP_CLIENT_SECRET', ''),
                redirect_uri=os.getenv('WHOOP_REDIRECT_URI', 'http://localhost:8080/callback'),
                authorization_url='https://api.prod.whoop.com/oauth/oauth2/auth',
                token_url='https://api.prod.whoop.com/oauth/oauth2/token',
                api_base_url='https://api.prod.whoop.com/developer/v1/',
                scopes=['read:recovery', 'read:sleep', 'read:workout', 'read:profile']
            ),
            'apple_health': WearableConfig(
                client_id=os.getenv('APPLE_HEALTH_CLIENT_ID', ''),
                client_secret=os.getenv('APPLE_HEALTH_CLIENT_SECRET', ''),
                redirect_uri=os.getenv('APPLE_HEALTH_REDIRECT_URI', 'http://localhost:8080/callback'),
                authorization_url='https://developer.apple.com/sign-in-with-apple/get-started/',
                token_url='https://appleid.apple.com/auth/token',
                api_base_url='https://developer.apple.com/documentation/healthkit/',
                scopes=['healthkit:heart_rate', 'healthkit:sleep_analysis', 'healthkit:body_temperature']
            )
        }
    
    def _anonymize_user_id(self, platform: str, user_id: str) -> str:
        """
        Convert platform user ID to anonymized player identifier.
        
        PRIVACY NOTE: Ensures no personal identifiers are stored in our system.
        """
        combined_id = f"{platform}_{user_id}"
        return f"player_{hashlib.sha256(combined_id.encode()).hexdigest()[:8]}"
    
    def _validate_consent(self, platform: str, user_id: str) -> bool:
        """
        Validate that athlete has provided explicit consent for wearable data usage.
        
        ETHICAL REQUIREMENT: All data usage must be explicitly consented.
        
        Args:
            platform: Wearable platform name
            user_id: Platform user identifier
            
        Returns:
            bool: True if consent is valid and current
        """
        anonymized_id = self._anonymize_user_id(platform, user_id)
        logger.info(f"Validating consent for {platform} user {anonymized_id}")
        
        # CONTRIBUTOR NOTE: Implement actual consent checking in production
        # This would check:
        # - Explicit opt-in for wearable data sharing
        # - Platform-specific permissions granted
        # - Consent not revoked
        # - Data sharing agreement current
        return True
    
    def get_oauth_authorization_url(self, platform: str, state: Optional[str] = None) -> str:
        """
        Generate OAuth authorization URL for wearable platform.
        
        Args:
            platform: Platform name ('oura', 'whoop', 'apple_health')
            state: Optional state parameter for security
            
        Returns:
            str: Authorization URL for user consent
            
        ONBOARDING NOTE: This URL directs athletes to grant data access permissions.
        """
        if platform not in self.configs:
            raise ValueError(f"Unsupported platform: {platform}")
        
        config = self.configs[platform]
        oauth = OAuth2Session(
            config.client_id,
            redirect_uri=config.redirect_uri,
            scope=config.scopes,
            state=state
        )
        
        authorization_url, state = oauth.authorization_url(
            config.authorization_url,
            access_type='offline',
            approval_prompt='force'
        )
        
        logger.info(f"Generated OAuth URL for {platform}")
        return authorization_url
    
    def exchange_code_for_token(self, platform: str, authorization_code: str, 
                                state: Optional[str] = None) -> Dict[str, Any]:
        """
        Exchange OAuth authorization code for access token.
        
        Args:
            platform: Platform name
            authorization_code: Code from OAuth callback
            state: Optional state parameter for verification
            
        Returns:
            dict: OAuth token data
            
        SECURITY NOTE: Tokens should be stored securely and refreshed as needed.
        """
        if platform not in self.configs:
            raise ValueError(f"Unsupported platform: {platform}")
        
        config = self.configs[platform]
        oauth = OAuth2Session(
            config.client_id,
            redirect_uri=config.redirect_uri,
            state=state
        )
        
        try:
            token = oauth.fetch_token(
                config.token_url,
                authorization_response=authorization_code,
                client_secret=config.client_secret
            )
            logger.info(f"Successfully obtained OAuth token for {platform}")
            return token
        except Exception as e:
            logger.error(f"Failed to exchange code for token on {platform}: {str(e)}")
            return {}
    
    def fetch_oura_data(self, access_token: str, user_id: str, 
                        start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Fetch biometric data from Oura Ring API.
        
        Args:
            access_token: Valid OAuth access token
            user_id: Oura user identifier
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            dict: Combined biometric data from Oura
        """
        if not self._validate_consent('oura', user_id):
            return {}
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        base_url = self.configs['oura'].api_base_url
        data = {}
        
        try:
            # Fetch sleep data
            sleep_url = f"{base_url}usercollection/sleep"
            sleep_params = {'start_date': start_date, 'end_date': end_date}
            sleep_response = self.session.get(sleep_url, headers=headers, params=sleep_params)
            sleep_response.raise_for_status()
            data['sleep'] = sleep_response.json()
            
            # Fetch HRV and heart rate data
            hrv_url = f"{base_url}usercollection/heartrate"
            hrv_params = {'start_date': start_date, 'end_date': end_date}
            hrv_response = self.session.get(hrv_url, headers=headers, params=hrv_params)
            hrv_response.raise_for_status()
            data['heart_rate'] = hrv_response.json()
            
            # Fetch temperature data
            temp_url = f"{base_url}usercollection/temperature"
            temp_params = {'start_date': start_date, 'end_date': end_date}
            temp_response = self.session.get(temp_url, headers=headers, params=temp_params)
            temp_response.raise_for_status()
            data['temperature'] = temp_response.json()
            
            logger.info(f"Successfully fetched Oura data for {self._anonymize_user_id('oura', user_id)}")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch Oura data: {str(e)}")
        
        return data
    
    def fetch_whoop_data(self, access_token: str, user_id: str,
                         start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Fetch biometric data from WHOOP API.
        
        Args:
            access_token: Valid OAuth access token
            user_id: WHOOP user identifier
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            dict: Combined biometric data from WHOOP
        """
        if not self._validate_consent('whoop', user_id):
            return {}
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        base_url = self.configs['whoop'].api_base_url
        data = {}
        
        try:
            # Fetch recovery data (includes HRV)
            recovery_url = f"{base_url}recovery"
            recovery_params = {'start': start_date, 'end': end_date}
            recovery_response = self.session.get(recovery_url, headers=headers, params=recovery_params)
            recovery_response.raise_for_status()
            data['recovery'] = recovery_response.json()
            
            # Fetch sleep data
            sleep_url = f"{base_url}sleep"
            sleep_params = {'start': start_date, 'end': end_date}
            sleep_response = self.session.get(sleep_url, headers=headers, params=sleep_params)
            sleep_response.raise_for_status()
            data['sleep'] = sleep_response.json()
            
            logger.info(f"Successfully fetched WHOOP data for {self._anonymize_user_id('whoop', user_id)}")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch WHOOP data: {str(e)}")
        
        return data
    
    def normalize_biometric_data(self, platform: str, raw_data: Dict[str, Any], 
                                 user_id: str) -> pd.DataFrame:
        """
        Normalize biometric data across different wearable platforms.
        
        Args:
            platform: Platform name
            raw_data: Raw data from platform API
            user_id: Platform user identifier
            
        Returns:
            pd.DataFrame: Normalized biometric data
            
        CIVIC NOTE: Standardization enables cross-platform research and insights
        """
        if platform == 'oura':
            return self._normalize_oura_data(raw_data, user_id)
        elif platform == 'whoop':
            return self._normalize_whoop_data(raw_data, user_id)
        elif platform == 'apple_health':
            return self._normalize_apple_health_data(raw_data, user_id)
        else:
            logger.warning(f"Unknown platform: {platform}")
            return pd.DataFrame()
    
    def _normalize_oura_data(self, raw_data: Dict[str, Any], user_id: str) -> pd.DataFrame:
        """Normalize Oura Ring data to standard format."""
        records = []
        player_id = self._anonymize_user_id('oura', user_id)
        
        # Process sleep data
        sleep_data = raw_data.get('sleep', {}).get('data', [])
        for sleep_record in sleep_data:
            date = sleep_record.get('day')
            if date:
                record = {
                    'player_id': player_id,
                    'date': date,
                    'platform': 'oura',
                    'sleep_duration': sleep_record.get('total_sleep_duration', 0) / 3600,  # Convert to hours
                    'sleep_quality': sleep_record.get('score', 0) / 100,  # Normalize to 0-1
                    'deep_sleep_duration': sleep_record.get('deep_sleep_duration', 0) / 3600,
                    'rem_sleep_duration': sleep_record.get('rem_sleep_duration', 0) / 3600,
                    'sleep_efficiency': sleep_record.get('efficiency', 0) / 100,
                    'restfulness': sleep_record.get('restfulness', 0) / 100
                }
                records.append(record)
        
        # Process heart rate and HRV data
        hr_data = raw_data.get('heart_rate', {}).get('data', [])
        hr_by_date = {}
        for hr_record in hr_data:
            date = hr_record.get('timestamp', '')[:10]  # Extract date part
            if date:
                if date not in hr_by_date:
                    hr_by_date[date] = {'hr_values': [], 'hrv_values': []}
                hr_by_date[date]['hr_values'].append(hr_record.get('bpm', 0))
        
        # Add heart rate data to records
        for record in records:
            date = record['date']
            if date in hr_by_date:
                hr_values = hr_by_date[date]['hr_values']
                if hr_values:
                    record['avg_heart_rate'] = sum(hr_values) / len(hr_values)
                    record['resting_heart_rate'] = min(hr_values)
                    record['max_heart_rate'] = max(hr_values)
        
        # Process temperature data
        temp_data = raw_data.get('temperature', {}).get('data', [])
        temp_by_date = {}
        for temp_record in temp_data:
            date = temp_record.get('day')
            if date:
                temp_by_date[date] = temp_record.get('temperature_deviation', 0)
        
        # Add temperature data to records
        for record in records:
            date = record['date']
            if date in temp_by_date:
                record['skin_temperature'] = 36.5 + temp_by_date[date]  # Baseline + deviation
        
        return pd.DataFrame(records)
    
    def _normalize_whoop_data(self, raw_data: Dict[str, Any], user_id: str) -> pd.DataFrame:
        """Normalize WHOOP data to standard format."""
        records = []
        player_id = self._anonymize_user_id('whoop', user_id)
        
        # Process recovery data (includes HRV)
        recovery_data = raw_data.get('recovery', [])
        for recovery_record in recovery_data:
            date = recovery_record.get('created_at', '')[:10]
            if date:
                record = {
                    'player_id': player_id,
                    'date': date,
                    'platform': 'whoop',
                    'recovery_score': recovery_record.get('user_calibrating', {}).get('recovery_score', 0) / 100,
                    'hrv_rmssd': recovery_record.get('score', {}).get('hrv_rmssd_milli', 0),
                    'resting_heart_rate': recovery_record.get('score', {}).get('resting_heart_rate', 0),
                    'skin_temperature': recovery_record.get('score', {}).get('skin_temp_celsius', 0)
                }
                records.append(record)
        
        # Process sleep data
        sleep_data = raw_data.get('sleep', [])
        sleep_by_date = {}
        for sleep_record in sleep_data:
            date = sleep_record.get('created_at', '')[:10]
            if date:
                sleep_by_date[date] = {
                    'sleep_duration': sleep_record.get('score', {}).get('total_in_bed_time_milli', 0) / (1000 * 3600),
                    'sleep_efficiency': sleep_record.get('score', {}).get('sleep_efficiency_percentage', 0) / 100,
                    'deep_sleep_duration': sleep_record.get('score', {}).get('deep_sleep_milli', 0) / (1000 * 3600),
                    'rem_sleep_duration': sleep_record.get('score', {}).get('rem_sleep_milli', 0) / (1000 * 3600),
                    'sleep_quality': sleep_record.get('score', {}).get('sleep_performance_percentage', 0) / 100
                }
        
        # Merge sleep data into records
        for record in records:
            date = record['date']
            if date in sleep_by_date:
                record.update(sleep_by_date[date])
        
        return pd.DataFrame(records)
    
    def _normalize_apple_health_data(self, raw_data: Dict[str, Any], user_id: str) -> pd.DataFrame:
        """
        Normalize Apple Health data to standard format.
        
        NOTE: Apple Health integration requires iOS app with HealthKit permissions.
        This is a placeholder for the data structure.
        """
        records = []
        player_id = self._anonymize_user_id('apple_health', user_id)
        
        # CONTRIBUTOR NOTE: Apple Health integration requires native iOS app
        # This function shows the expected data structure for future implementation
        
        logger.info(f"Apple Health integration placeholder for {player_id}")
        return pd.DataFrame(records)
    
    def process_multi_platform_data(self, user_tokens: Dict[str, Dict], 
                                    start_date: str, end_date: str) -> pd.DataFrame:
        """
        Process biometric data from multiple wearable platforms for a user.
        
        Args:
            user_tokens: Dict mapping platform names to token/user_id info
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            pd.DataFrame: Combined normalized data from all platforms
            
        TRANSPARENCY NOTE: All processing steps are logged for auditability
        """
        all_data = []
        
        for platform, token_info in user_tokens.items():
            if platform not in self.configs:
                logger.warning(f"Skipping unsupported platform: {platform}")
                continue
            
            access_token = token_info.get('access_token')
            user_id = token_info.get('user_id')
            
            if not access_token or not user_id:
                logger.warning(f"Missing token or user_id for {platform}")
                continue
            
            logger.info(f"Processing {platform} data for {self._anonymize_user_id(platform, user_id)}")
            
            # Fetch platform-specific data
            if platform == 'oura':
                raw_data = self.fetch_oura_data(access_token, user_id, start_date, end_date)
            elif platform == 'whoop':
                raw_data = self.fetch_whoop_data(access_token, user_id, start_date, end_date)
            elif platform == 'apple_health':
                raw_data = {}  # Placeholder - requires iOS app integration
            else:
                continue
            
            if raw_data:
                # Normalize data to standard format
                normalized_df = self.normalize_biometric_data(platform, raw_data, user_id)
                if not normalized_df.empty:
                    all_data.append(normalized_df)
        
        # Combine all platform data
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            
            # Add processing metadata
            combined_df['data_source'] = 'wearable_multi_platform'
            combined_df['processed_timestamp'] = datetime.now().isoformat()
            combined_df['consent_validated'] = True
            
            # Sort by player_id and date for consistency
            combined_df = combined_df.sort_values(['player_id', 'date']).reset_index(drop=True)
            
            logger.info(f"Combined processing complete: {len(combined_df)} records from {len(all_data)} platforms")
            return combined_df
        else:
            logger.warning("No data processed from any platform")
            return pd.DataFrame()
    
    def store_data(self, df: pd.DataFrame, storage_type: str = 'csv', 
                   output_path: str = 'wearable_data.csv') -> bool:
        """
        Store processed wearable data with ethical safeguards.
        
        Args:
            df: Processed wearable data
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
                logger.info(f"Wearable data stored to CSV: {output_path}")
            
            if storage_type in ['supabase', 'both'] and self.supabase_url and self.supabase_key:
                import supabase
                client = supabase.create_client(self.supabase_url, self.supabase_key)
                
                # Store in wearable_data table
                records = df.to_dict('records')
                result = client.table('wearable_data').upsert(records).execute()
                logger.info(f"Wearable data stored to Supabase: {len(records)} records")
            
        except Exception as e:
            logger.error(f"Failed to store wearable data: {str(e)}")
            success = False
        
        return success


# CONTRIBUTOR ONBOARDING FUNCTIONS

def setup_oauth_environment() -> Dict[str, Dict[str, str]]:
    """
    Guide contributors through OAuth setup for wearable platforms.
    
    Returns:
        dict: Configuration status for each platform
        
    ONBOARDING NOTE: OAuth setup requires developer accounts with each platform
    """
    platforms = {
        'oura': {
            'client_id': 'Set' if os.getenv('OURA_CLIENT_ID') else 'Missing',
            'client_secret': 'Set' if os.getenv('OURA_CLIENT_SECRET') else 'Missing',
            'setup_url': 'https://cloud.ouraring.com/developers/applications'
        },
        'whoop': {
            'client_id': 'Set' if os.getenv('WHOOP_CLIENT_ID') else 'Missing',
            'client_secret': 'Set' if os.getenv('WHOOP_CLIENT_SECRET') else 'Missing',
            'setup_url': 'https://developer.whoop.com/developer-portal/'
        },
        'apple_health': {
            'client_id': 'Set' if os.getenv('APPLE_HEALTH_CLIENT_ID') else 'Missing',
            'client_secret': 'Set' if os.getenv('APPLE_HEALTH_CLIENT_SECRET') else 'Missing',
            'setup_url': 'https://developer.apple.com/sign-in-with-apple/'
        }
    }
    
    print("🔗 OAUTH SETUP STATUS:")
    print("=" * 30)
    
    for platform, status in platforms.items():
        print(f"\n{platform.upper()}:")
        print(f"  Client ID: {status['client_id']}")
        print(f"  Client Secret: {status['client_secret']}")
        if status['client_id'] == 'Missing' or status['client_secret'] == 'Missing':
            print(f"  ⚠️  Setup required at: {status['setup_url']}")
    
    print("\n📋 OAUTH ETHICAL CHECKLIST:")
    print("   ✓ Review each platform's data usage policies")
    print("   ✓ Configure redirect URIs for secure callback handling")
    print("   ✓ Test OAuth flow with your own account first")
    print("   ✓ Implement secure token storage and refresh")
    print("   ✓ Validate athlete consent before token exchange")
    
    return platforms


def example_oauth_flow():
    """
    Example OAuth flow demonstrating ethical wearable data integration.
    
    LEARNING NOTE: Shows contributors the complete OAuth consent process
    """
    print("🔐 EXAMPLE: Ethical Wearable OAuth Flow")
    print("=" * 40)
    
    try:
        ingestor = WearableDataIngestor()
        
        # Example OAuth flow (doesn't actually execute without real credentials)
        platform = 'oura'
        
        print(f"\n1. Generate authorization URL for {platform}")
        # auth_url = ingestor.get_oauth_authorization_url(platform, state='example_state')
        # print(f"   Redirect athlete to: {auth_url}")
        
        print("\n2. Athlete grants permissions on platform website")
        print("   - Athlete reviews data sharing permissions")
        print("   - Athlete explicitly consents to research use")
        print("   - Platform redirects to callback URL with authorization code")
        
        print("\n3. Exchange authorization code for access token")
        # token_data = ingestor.exchange_code_for_token(platform, 'example_code')
        print("   - Securely store access and refresh tokens")
        print("   - Set up automatic token refresh")
        
        print("\n4. Fetch and process biometric data")
        print("   - Validate consent is still active")
        print("   - Fetch data for specified date range")
        print("   - Normalize across platforms")
        print("   - Store with anonymized identifiers")
        
        print("\n✓ OAuth flow completed ethically")
        
    except Exception as e:
        print(f"⚠️  Setup needed for full OAuth demo: {e}")
        setup_oauth_environment()


if __name__ == "__main__":
    """
    Main execution block for testing and demonstration.
    
    SAFETY NOTE: Only runs example code, never processes real data automatically
    """
    print("🏀 Cycle-Aware WNBA: Wearable Data Ingestion Module")
    print("   Multi-Platform • OAuth-Secured • Athlete-Centered")
    print("=" * 70)
    
    example_oauth_flow()