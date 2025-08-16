"""
Weather and Sentiment Data Ingestion Module - Cycle-Aware WNBA Analytics

This module uses OpenWeatherMap API to pull hydration-relevant weather data
and analyzes public Twitter/X sentiment using NLP, normalizes mood volatility
indicators and timestamp alignment for environmental context modeling.

ETHICAL NOTICE: This script handles environmental and public sentiment data
for research purposes. All usage must comply with privacy laws and ethical
research practices. No personal social media data is collected.

CIVIC DISCLAIMER: This code serves public-good research and athlete empowerment.
Only publicly available environmental data and aggregated sentiment is used.
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
import tweepy
from textblob import TextBlob
import numpy as np
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import hashlib
import re
from dataclasses import dataclass
from collections import defaultdict

# Configure logging for audit trail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class WeatherConfig:
    """Configuration class for weather API settings."""
    api_key: str
    base_url: str
    endpoints: Dict[str, str]
    rate_limit: int


@dataclass
class SentimentConfig:
    """Configuration class for sentiment analysis settings."""
    api_key: str
    api_secret: str
    access_token: str
    access_token_secret: str
    bearer_token: str
    rate_limit: int


class WeatherSentimentIngestor:
    """
    Ethical data ingestion class for weather and public sentiment data.
    
    CONTRIBUTOR NOTE: This class focuses on environmental context and public
    sentiment trends that may affect athlete performance, while maintaining
    privacy and avoiding personal data collection.
    """
    
    def __init__(self, supabase_url: Optional[str] = None, supabase_key: Optional[str] = None):
        """
        Initialize the weather and sentiment data ingestor.
        
        Args:
            supabase_url: Supabase project URL for data storage
            supabase_key: Supabase service key for authentication
            
        ETHICAL NOTE: Only uses publicly available environmental and sentiment data.
        """
        self.supabase_url = supabase_url or os.getenv('SUPABASE_URL')
        self.supabase_key = supabase_key or os.getenv('SUPABASE_KEY')
        
        # Configure HTTP session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Initialize API configurations
        self._setup_api_configs()
        
        # Initialize Twitter/X API client
        self._setup_twitter_client()
        
        # Cache for location data
        self._location_cache = {}
        
        logger.info("WeatherSentimentIngestor initialized with environmental data access")
    
    def _setup_api_configs(self):
        """
        Set up API configurations for weather and sentiment data providers.
        
        TRANSPARENCY NOTE: Documents all external data sources used.
        """
        self.weather_config = WeatherConfig(
            api_key=os.getenv('OPENWEATHERMAP_API_KEY', ''),
            base_url='https://api.openweathermap.org/data/2.5',
            endpoints={
                'current': '/weather',
                'history': '/onecall/timemachine',
                'forecast': '/forecast',
                'air_quality': '/air_pollution'
            },
            rate_limit=60  # 60 requests per minute for free tier
        )
        
        self.sentiment_config = SentimentConfig(
            api_key=os.getenv('TWITTER_API_KEY', ''),
            api_secret=os.getenv('TWITTER_API_SECRET', ''),
            access_token=os.getenv('TWITTER_ACCESS_TOKEN', ''),
            access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET', ''),
            bearer_token=os.getenv('TWITTER_BEARER_TOKEN', ''),
            rate_limit=15  # 15 requests per 15-minute window
        )
    
    def _setup_twitter_client(self):
        """
        Initialize Twitter/X API client for sentiment analysis.
        
        PRIVACY NOTE: Only accesses public tweets, never private data.
        """
        try:
            if self.sentiment_config.bearer_token:
                self.twitter_client = tweepy.Client(
                    bearer_token=self.sentiment_config.bearer_token,
                    consumer_key=self.sentiment_config.api_key,
                    consumer_secret=self.sentiment_config.api_secret,
                    access_token=self.sentiment_config.access_token,
                    access_token_secret=self.sentiment_config.access_token_secret,
                    wait_on_rate_limit=True
                )
                logger.info("Twitter API client initialized successfully")
            else:
                self.twitter_client = None
                logger.warning("Twitter API credentials not configured")
        except Exception as e:
            logger.warning(f"Failed to initialize Twitter client: {str(e)}")
            self.twitter_client = None
    
    def _get_wnba_venue_coordinates(self) -> Dict[str, Tuple[float, float]]:
        """
        Get coordinates for WNBA venues for weather data collection.
        
        Returns:
            dict: Mapping of venue names to (latitude, longitude) coordinates
            
        CIVIC NOTE: Uses publicly available venue location data
        """
        # WNBA team locations (publicly available information)
        venues = {
            'Las Vegas Aces': (36.1215, -115.1739),  # Las Vegas, NV
            'New York Liberty': (40.7505, -73.9934),  # Brooklyn, NY
            'Minnesota Lynx': (44.9537, -93.0900),   # Minneapolis, MN
            'Seattle Storm': (47.6205, -122.3493),   # Seattle, WA
            'Phoenix Mercury': (33.4734, -112.0713), # Phoenix, AZ
            'Chicago Sky': (41.8373, -87.6862),      # Chicago, IL
            'Connecticut Sun': (41.5737, -72.0859),  # Uncasville, CT
            'Indiana Fever': (39.7643, -86.1553),    # Indianapolis, IN
            'Atlanta Dream': (33.7573, -84.3963),    # Atlanta, GA
            'Dallas Wings': (32.7912, -97.0051),     # Arlington, TX
            'Washington Mystics': (38.8816, -77.0269), # Washington, DC
            'Los Angeles Sparks': (34.0434, -118.2677) # Los Angeles, CA
        }
        return venues
    
    def _validate_environmental_ethics(self, data_type: str, location: str) -> bool:
        """
        Validate that environmental data collection meets ethical standards.
        
        ETHICAL REQUIREMENT: Only publicly available environmental data.
        
        Args:
            data_type: Type of environmental data
            location: Location being monitored
            
        Returns:
            bool: True if data collection is ethical
        """
        # Ensure we're only collecting public environmental data
        approved_types = ['weather', 'air_quality', 'public_sentiment', 'environmental_context']
        
        if data_type not in approved_types:
            logger.warning(f"Data type {data_type} not approved for collection")
            return False
        
        # Verify location is a public venue, not private
        venues = self._get_wnba_venue_coordinates()
        if location not in venues and 'public' not in location.lower():
            logger.warning(f"Location {location} not approved for monitoring")
            return False
        
        logger.info(f"Environmental data validation passed for {data_type} at {location}")
        return True
    
    def fetch_weather_data(self, location: str, date: str, 
                           venue_coords: Optional[Tuple[float, float]] = None) -> Dict[str, Any]:
        """
        Fetch weather data for specific location and date.
        
        Args:
            location: Venue/city name
            date: Date in YYYY-MM-DD format
            venue_coords: Optional (lat, lon) coordinates
            
        Returns:
            dict: Weather data for the specified location and date
        """
        if not self.weather_config.api_key:
            logger.warning("OpenWeatherMap API key not configured")
            return {}
        
        if not self._validate_environmental_ethics('weather', location):
            return {}
        
        # Get coordinates
        if venue_coords:
            lat, lon = venue_coords
        else:
            coords = self._get_venue_coordinates(location)
            if not coords:
                return {}
            lat, lon = coords
        
        # Convert date to timestamp for historical data
        try:
            target_date = datetime.strptime(date, '%Y-%m-%d')
            timestamp = int(target_date.timestamp())
        except ValueError:
            logger.error(f"Invalid date format: {date}")
            return {}
        
        # Determine if we need current, historical, or forecast data
        today = datetime.now().date()
        target_date_obj = target_date.date()
        
        if target_date_obj < today:
            # Historical data
            return self._fetch_historical_weather(lat, lon, timestamp, location)
        elif target_date_obj == today:
            # Current data
            return self._fetch_current_weather(lat, lon, location)
        else:
            # Forecast data
            return self._fetch_forecast_weather(lat, lon, location)
    
    def _fetch_historical_weather(self, lat: float, lon: float, 
                                  timestamp: int, location: str) -> Dict[str, Any]:
        """Fetch historical weather data for specific coordinates and timestamp."""
        url = f"{self.weather_config.base_url}{self.weather_config.endpoints['history']}"
        
        params = {
            'lat': lat,
            'lon': lon,
            'dt': timestamp,
            'appid': self.weather_config.api_key,
            'units': 'imperial'  # Fahrenheit, mph
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            weather_data = self._normalize_weather_data(data, location, 'historical')
            
            logger.info(f"Fetched historical weather for {location}")
            return weather_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch historical weather for {location}: {str(e)}")
            return {}
    
    def _fetch_current_weather(self, lat: float, lon: float, location: str) -> Dict[str, Any]:
        """Fetch current weather data for specific coordinates."""
        url = f"{self.weather_config.base_url}{self.weather_config.endpoints['current']}"
        
        params = {
            'lat': lat,
            'lon': lon,
            'appid': self.weather_config.api_key,
            'units': 'imperial'
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            weather_data = self._normalize_weather_data(data, location, 'current')
            
            logger.info(f"Fetched current weather for {location}")
            return weather_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch current weather for {location}: {str(e)}")
            return {}
    
    def _fetch_forecast_weather(self, lat: float, lon: float, location: str) -> Dict[str, Any]:
        """Fetch weather forecast for specific coordinates."""
        # For forecast, we'll use current weather as a proxy
        # (OpenWeatherMap's forecast API has different structure)
        return self._fetch_current_weather(lat, lon, location)
    
    def _normalize_weather_data(self, raw_data: Dict[str, Any], 
                                location: str, data_type: str) -> Dict[str, Any]:
        """
        Normalize weather data to standard format for hydration analysis.
        
        CIVIC NOTE: Focuses on hydration-relevant metrics for athlete wellness.
        """
        if data_type == 'historical' and 'current' in raw_data:
            weather_info = raw_data['current']
        else:
            weather_info = raw_data
        
        # Extract hydration-relevant metrics
        normalized_data = {
            'location': location,
            'timestamp': datetime.now().isoformat(),
            'data_type': data_type,
            'temperature_f': weather_info.get('temp', 0),
            'feels_like_f': weather_info.get('feels_like', weather_info.get('temp', 0)),
            'humidity_percent': weather_info.get('humidity', 0),
            'pressure_mb': weather_info.get('pressure', 0),
            'wind_speed_mph': weather_info.get('wind_speed', weather_info.get('wind', {}).get('speed', 0)),
            'wind_direction': weather_info.get('wind_deg', weather_info.get('wind', {}).get('deg', 0)),
            'visibility_miles': weather_info.get('visibility', 0) / 1609.34 if weather_info.get('visibility') else 0,  # Convert meters to miles
            'uv_index': weather_info.get('uvi', 0),
            'weather_condition': weather_info.get('weather', [{}])[0].get('main', 'Unknown'),
            'weather_description': weather_info.get('weather', [{}])[0].get('description', ''),
            'cloudiness_percent': weather_info.get('clouds', weather_info.get('clouds', {}).get('all', 0)),
        }
        
        # Calculate hydration risk factors
        normalized_data['heat_index'] = self._calculate_heat_index(
            normalized_data['temperature_f'], 
            normalized_data['humidity_percent']
        )
        
        normalized_data['hydration_risk'] = self._assess_hydration_risk(normalized_data)
        
        # Add processing metadata
        normalized_data['data_source'] = 'openweathermap'
        normalized_data['processed_timestamp'] = datetime.now().isoformat()
        
        return normalized_data
    
    def _calculate_heat_index(self, temp_f: float, humidity: float) -> float:
        """
        Calculate heat index for hydration risk assessment.
        
        Args:
            temp_f: Temperature in Fahrenheit
            humidity: Relative humidity percentage
            
        Returns:
            float: Heat index in Fahrenheit
        """
        if temp_f < 80 or humidity < 40:
            return temp_f  # Heat index not significant below these thresholds
        
        # Rothfusz regression formula for heat index
        hi = -42.379 + 2.04901523 * temp_f + 10.14333127 * humidity
        hi += -0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2
        hi += -5.481717e-2 * humidity**2 + 1.22874e-3 * temp_f**2 * humidity
        hi += 8.5282e-4 * temp_f * humidity**2 - 1.99e-6 * temp_f**2 * humidity**2
        
        return round(hi, 1)
    
    def _assess_hydration_risk(self, weather_data: Dict[str, Any]) -> str:
        """
        Assess hydration risk based on weather conditions.
        
        Returns:
            str: Risk level ('low', 'moderate', 'high', 'extreme')
        """
        heat_index = weather_data.get('heat_index', weather_data.get('temperature_f', 0))
        humidity = weather_data.get('humidity_percent', 0)
        wind_speed = weather_data.get('wind_speed_mph', 0)
        
        # Risk assessment based on heat index and conditions
        if heat_index >= 105:
            risk = 'extreme'
        elif heat_index >= 90 or (weather_data.get('temperature_f', 0) >= 85 and humidity >= 70):
            risk = 'high'
        elif heat_index >= 80 or weather_data.get('temperature_f', 0) >= 75:
            risk = 'moderate'
        else:
            risk = 'low'
        
        # Adjust for wind (cooling effect)
        if wind_speed > 15 and risk in ['high', 'extreme']:
            risk_levels = ['low', 'moderate', 'high', 'extreme']
            current_index = risk_levels.index(risk)
            if current_index > 0:
                risk = risk_levels[current_index - 1]
        
        return risk
    
    def _get_venue_coordinates(self, location: str) -> Optional[Tuple[float, float]]:
        """Get coordinates for a venue location."""
        venues = self._get_wnba_venue_coordinates()
        
        # Try exact match first
        if location in venues:
            return venues[location]
        
        # Try fuzzy matching for team names
        for venue, coords in venues.items():
            if location.lower() in venue.lower() or venue.lower() in location.lower():
                return coords
        
        logger.warning(f"Coordinates not found for location: {location}")
        return None
    
    def fetch_public_sentiment(self, search_terms: List[str], date: str, 
                               location: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetch and analyze public sentiment from Twitter/X.
        
        Args:
            search_terms: Terms to search for (e.g., ['WNBA', 'women sports'])
            date: Date in YYYY-MM-DD format
            location: Optional location filter
            
        Returns:
            dict: Aggregated sentiment analysis data
            
        PRIVACY NOTE: Only analyzes public tweets, never private data
        """
        if not self.twitter_client:
            logger.warning("Twitter API client not available")
            return {}
        
        if not self._validate_environmental_ethics('public_sentiment', location or 'public'):
            return {}
        
        # Build search query
        query = ' OR '.join(search_terms)
        if location:
            query += f' near:"{location}"'
        
        # Add filters for public tweets only
        query += ' -is:retweet lang:en'  # Exclude retweets, English only
        
        try:
            # Search for tweets from the specified date
            start_time = datetime.strptime(date, '%Y-%m-%d')
            end_time = start_time + timedelta(days=1)
            
            tweets = tweepy.Paginator(
                self.twitter_client.search_recent_tweets,
                query=query,
                start_time=start_time,
                end_time=end_time,
                max_results=100,  # Limit to avoid overwhelming analysis
                tweet_fields=['created_at', 'public_metrics', 'context_annotations']
            ).flatten(limit=500)
            
            # Analyze sentiment
            sentiment_data = self._analyze_tweet_sentiment(tweets, search_terms, date)
            
            logger.info(f"Analyzed sentiment for {len(sentiment_data.get('tweets', []))} tweets")
            return sentiment_data
            
        except Exception as e:
            logger.error(f"Failed to fetch Twitter sentiment: {str(e)}")
            return {}
    
    def _analyze_tweet_sentiment(self, tweets, search_terms: List[str], date: str) -> Dict[str, Any]:
        """
        Analyze sentiment of collected tweets using TextBlob NLP.
        
        ETHICAL NOTE: Aggregates sentiment without storing personal tweet data.
        """
        sentiment_scores = []
        tweet_count = 0
        emotion_categories = defaultdict(int)
        
        for tweet in tweets:
            if tweet.text:
                # Analyze sentiment using TextBlob
                blob = TextBlob(tweet.text)
                
                sentiment_score = blob.sentiment.polarity  # -1 (negative) to 1 (positive)
                subjectivity = blob.sentiment.subjectivity  # 0 (objective) to 1 (subjective)
                
                sentiment_scores.append({
                    'polarity': sentiment_score,
                    'subjectivity': subjectivity,
                    'created_at': tweet.created_at.isoformat() if tweet.created_at else date
                })
                
                # Categorize emotions
                if sentiment_score > 0.1:
                    emotion_categories['positive'] += 1
                elif sentiment_score < -0.1:
                    emotion_categories['negative'] += 1
                else:
                    emotion_categories['neutral'] += 1
                
                tweet_count += 1
        
        # Calculate aggregated metrics
        if sentiment_scores:
            polarities = [s['polarity'] for s in sentiment_scores]
            subjectivities = [s['subjectivity'] for s in sentiment_scores]
            
            aggregated_sentiment = {
                'date': date,
                'search_terms': search_terms,
                'tweet_count': tweet_count,
                'avg_polarity': np.mean(polarities),
                'std_polarity': np.std(polarities),
                'avg_subjectivity': np.mean(subjectivities),
                'sentiment_distribution': dict(emotion_categories),
                'mood_volatility': np.std(polarities),  # Higher std = more volatile mood
                'overall_sentiment': 'positive' if np.mean(polarities) > 0.1 else 'negative' if np.mean(polarities) < -0.1 else 'neutral',
                'data_source': 'twitter_public_sentiment',
                'processed_timestamp': datetime.now().isoformat(),
                'privacy_compliant': True  # Flag indicating only public data used
            }
        else:
            aggregated_sentiment = {
                'date': date,
                'search_terms': search_terms,
                'tweet_count': 0,
                'message': 'No public tweets found for analysis',
                'data_source': 'twitter_public_sentiment',
                'processed_timestamp': datetime.now().isoformat()
            }
        
        return aggregated_sentiment
    
    def normalize_environmental_context(self, weather_data: Dict[str, Any], 
                                        sentiment_data: Dict[str, Any],
                                        game_date: str, location: str) -> pd.DataFrame:
        """
        Normalize environmental and sentiment data for cycle-aware modeling.
        
        Args:
            weather_data: Weather information for the location
            sentiment_data: Public sentiment analysis results
            game_date: Date of the game/event
            location: Venue location
            
        Returns:
            pd.DataFrame: Normalized environmental context data
        """
        # Combine weather and sentiment into unified record
        context_record = {
            'location': location,
            'date': game_date,
            'data_source': 'environmental_context',
            
            # Weather metrics (hydration-focused)
            'temperature_f': weather_data.get('temperature_f', 0),
            'heat_index': weather_data.get('heat_index', weather_data.get('temperature_f', 0)),
            'humidity_percent': weather_data.get('humidity_percent', 0),
            'hydration_risk': weather_data.get('hydration_risk', 'unknown'),
            'weather_condition': weather_data.get('weather_condition', 'unknown'),
            
            # Sentiment metrics (mood context)
            'public_sentiment': sentiment_data.get('overall_sentiment', 'neutral'),
            'mood_volatility': sentiment_data.get('mood_volatility', 0),
            'sentiment_polarity': sentiment_data.get('avg_polarity', 0),
            'tweet_volume': sentiment_data.get('tweet_count', 0),
            
            # Combined environmental stress indicators
            'environmental_stress_score': self._calculate_environmental_stress(weather_data, sentiment_data),
            'context_quality': self._assess_context_quality(weather_data, sentiment_data),
            
            # Metadata
            'processed_timestamp': datetime.now().isoformat(),
            'privacy_compliant': True
        }
        
        return pd.DataFrame([context_record])
    
    def _calculate_environmental_stress(self, weather_data: Dict[str, Any], 
                                        sentiment_data: Dict[str, Any]) -> float:
        """
        Calculate combined environmental stress score (0-10 scale).
        
        RESEARCH NOTE: Higher scores indicate more challenging conditions for performance.
        """
        stress_score = 0.0
        
        # Weather stress factors
        heat_index = weather_data.get('heat_index', weather_data.get('temperature_f', 70))
        if heat_index > 80:
            stress_score += (heat_index - 80) / 10  # Scale heat stress
        
        humidity = weather_data.get('humidity_percent', 50)
        if humidity > 60:
            stress_score += (humidity - 60) / 20  # Scale humidity stress
        
        # Sentiment stress factors
        mood_volatility = sentiment_data.get('mood_volatility', 0)
        stress_score += mood_volatility * 2  # Scale sentiment volatility
        
        sentiment_polarity = sentiment_data.get('avg_polarity', 0)
        if sentiment_polarity < -0.2:  # Negative sentiment adds stress
            stress_score += abs(sentiment_polarity) * 2
        
        # Cap at 10.0
        return min(10.0, stress_score)
    
    def _assess_context_quality(self, weather_data: Dict[str, Any], 
                                sentiment_data: Dict[str, Any]) -> str:
        """
        Assess quality of environmental context data.
        
        Returns:
            str: Quality level ('high', 'medium', 'low')
        """
        quality_score = 0
        
        # Weather data quality
        if weather_data.get('temperature_f', 0) > 0:
            quality_score += 1
        if weather_data.get('humidity_percent', 0) > 0:
            quality_score += 1
        if weather_data.get('weather_condition', 'unknown') != 'unknown':
            quality_score += 1
        
        # Sentiment data quality
        if sentiment_data.get('tweet_count', 0) >= 10:
            quality_score += 1
        elif sentiment_data.get('tweet_count', 0) >= 1:
            quality_score += 0.5
        
        if sentiment_data.get('avg_polarity') is not None:
            quality_score += 1
        
        # Classify quality
        if quality_score >= 4:
            return 'high'
        elif quality_score >= 2:
            return 'medium'
        else:
            return 'low'
    
    def process_environmental_data(self, locations: List[str], dates: List[str],
                                   search_terms: List[str] = None) -> pd.DataFrame:
        """
        Complete pipeline to process environmental and sentiment data.
        
        Args:
            locations: List of venue locations
            dates: List of dates to analyze
            search_terms: Terms for sentiment analysis
            
        Returns:
            pd.DataFrame: Processed environmental context data
        """
        if search_terms is None:
            search_terms = ['WNBA', 'women basketball', 'women sports']
        
        all_context_data = []
        
        for location in locations:
            for date in dates:
                logger.info(f"Processing environmental data for {location} on {date}")
                
                # Fetch weather data
                weather_data = self.fetch_weather_data(location, date)
                
                # Fetch sentiment data
                sentiment_data = self.fetch_public_sentiment(search_terms, date, location)
                
                # Normalize and combine
                if weather_data or sentiment_data:
                    context_df = self.normalize_environmental_context(
                        weather_data, sentiment_data, date, location
                    )
                    all_context_data.append(context_df)
                
                # Rate limiting
                import time
                time.sleep(2)  # 2 second delay between requests
        
        # Combine all data
        if all_context_data:
            final_df = pd.concat(all_context_data, ignore_index=True)
            logger.info(f"Environmental processing complete: {len(final_df)} records")
            return final_df
        else:
            logger.warning("No environmental data processed")
            return pd.DataFrame()
    
    def store_data(self, df: pd.DataFrame, storage_type: str = 'csv', 
                   output_path: str = 'environmental_data.csv') -> bool:
        """
        Store processed environmental data with ethical safeguards.
        
        Args:
            df: Processed environmental context data
            storage_type: Storage method ('csv', 'supabase', or 'both')
            output_path: Path for CSV output
            
        Returns:
            bool: Success status
        """
        if df.empty:
            logger.warning("No environmental data to store")
            return False
        
        success = True
        
        try:
            if storage_type in ['csv', 'both']:
                df.to_csv(output_path, index=False)
                logger.info(f"Environmental data stored to CSV: {output_path}")
            
            if storage_type in ['supabase', 'both'] and self.supabase_url and self.supabase_key:
                import supabase
                client = supabase.create_client(self.supabase_url, self.supabase_key)
                
                # Store in environmental_data table
                records = df.to_dict('records')
                result = client.table('environmental_data').upsert(records).execute()
                logger.info(f"Environmental data stored to Supabase: {len(records)} records")
            
        except Exception as e:
            logger.error(f"Failed to store environmental data: {str(e)}")
            success = False
        
        return success


# CONTRIBUTOR ONBOARDING FUNCTIONS

def setup_environmental_api_environment() -> Dict[str, str]:
    """
    Guide contributors through environmental API setup.
    
    Returns:
        dict: Configuration status for environmental APIs
    """
    api_status = {
        'openweathermap': 'Set' if os.getenv('OPENWEATHERMAP_API_KEY') else 'Missing',
        'twitter': 'Set' if os.getenv('TWITTER_BEARER_TOKEN') else 'Missing'
    }
    
    print("🌤️ ENVIRONMENTAL API SETUP STATUS:")
    print("=" * 35)
    print(f"OpenWeatherMap: {api_status['openweathermap']}")
    print(f"Twitter/X: {api_status['twitter']}")
    
    if api_status['openweathermap'] == 'Missing':
        print("\n⚠️  WEATHER API SETUP REQUIRED:")
        print("   1. Visit https://openweathermap.org/api")
        print("   2. Sign up for free account (60 calls/minute)")
        print("   3. Get API key from dashboard")
        print("   4. Set environment variable:")
        print("      export OPENWEATHERMAP_API_KEY='your_api_key_here'")
    
    if api_status['twitter'] == 'Missing':
        print("\n⚠️  TWITTER API SETUP REQUIRED:")
        print("   1. Visit https://developer.twitter.com/")
        print("   2. Apply for developer account")
        print("   3. Create app and get Bearer Token")
        print("   4. Set environment variable:")
        print("      export TWITTER_BEARER_TOKEN='your_bearer_token_here'")
    
    print("\n📋 ENVIRONMENTAL DATA ETHICS CHECKLIST:")
    print("   ✓ Use only publicly available weather data")
    print("   ✓ Analyze only public social media posts")
    print("   ✓ Respect API rate limits and terms of service")
    print("   ✓ Focus on environmental context, not personal tracking")
    print("   ✓ Aggregate sentiment data to protect individual privacy")
    print("   ✓ Use data only for athlete wellness and performance context")
    
    return api_status


def example_environmental_usage():
    """
    Example usage demonstrating ethical environmental data collection.
    """
    print("🌍 EXAMPLE: Ethical Environmental Data Collection")
    print("=" * 50)
    
    try:
        ingestor = WeatherSentimentIngestor()
        
        # Example parameters (safe public data)
        locations = ["Las Vegas Aces", "New York Liberty"]
        dates = ["2024-06-15", "2024-06-16"]
        search_terms = ["WNBA", "women basketball"]
        
        print(f"🏢 Processing venues: {locations}")
        print(f"📅 Date range: {dates[0]} to {dates[-1]}")
        print(f"🔍 Sentiment terms: {search_terms}")
        
        # In real usage:
        # df = ingestor.process_environmental_data(locations, dates, search_terms)
        # ingestor.store_data(df, 'csv', 'environmental_context.csv')
        
        print("\n🌡️ Weather Data Collection:")
        print("   • Temperature and heat index for hydration planning")
        print("   • Humidity and weather conditions")
        print("   • Environmental stress assessment")
        
        print("\n💬 Public Sentiment Analysis:")
        print("   • Aggregated mood indicators from public posts")
        print("   • Sentiment volatility metrics")
        print("   • Context for social/media pressure")
        
        print("\n✅ Ethical Standards Maintained:")
        print("   • Only public environmental data collected")
        print("   • No personal social media data stored")
        print("   • Aggregate sentiment analysis protects privacy")
        print("   • Focus on athlete wellness context")
        
        print("\n✓ Example completed - ready for ethical environmental analytics")
        
    except Exception as e:
        print(f"⚠️  Setup needed: {e}")
        setup_environmental_api_environment()


if __name__ == "__main__":
    """
    Main execution block for testing and demonstration.
    """
    print("🏀 Cycle-Aware WNBA: Weather & Sentiment Ingestion Module")
    print("   Environmental Context • Public Data • Privacy-Preserving")
    print("=" * 75)
    
    example_environmental_usage()