"""
Weather Data Ingestion using OpenWeatherMap API

This module provides integration with OpenWeatherMap for environmental
context data that may influence performance and cycle-related symptoms.

Weather factors considered: temperature, humidity, barometric pressure,
precipitation, air quality, and seasonal patterns.
"""

import pandas as pd
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import logging
from .base import DataSourceBase

logger = logging.getLogger(__name__)


class WeatherDataSource(DataSourceBase):
    """
    Weather data ingestion from OpenWeatherMap API.
    
    Fetches environmental context data including:
    - Current weather conditions
    - Historical weather data
    - Temperature and humidity
    - Barometric pressure changes
    - Air quality index
    - UV index and seasonal factors
    """
    
    def __init__(self, api_key: str, api_endpoint: str = "https://api.openweathermap.org"):
        """
        Initialize weather data source with OpenWeatherMap credentials.
        
        Args:
            api_key: OpenWeatherMap API key
            api_endpoint: Base URL for OpenWeatherMap API
        """
        ethical_compliance = {
            'consent_verified': True,  # Public environmental data
            'privacy_level': 'public',
            'data_retention': '90_days',
            'medical_grade': False,
            'audit_trail': True,
            'data_type': 'environmental_context'
        }
        
        super().__init__("Weather OpenWeatherMap", ethical_compliance)
        
        self.api_key = api_key
        self.api_endpoint = api_endpoint
        
        # WNBA team city coordinates for weather data
        self.team_locations = {
            'ATL': {'lat': 33.7490, 'lon': -84.3880, 'city': 'Atlanta'},
            'CHI': {'lat': 41.8781, 'lon': -87.6298, 'city': 'Chicago'},
            'CONN': {'lat': 41.7658, 'lon': -72.6734, 'city': 'Uncasville'},
            'DAL': {'lat': 32.7767, 'lon': -96.7970, 'city': 'Dallas'},
            'IND': {'lat': 39.7391, 'lon': -86.1612, 'city': 'Indianapolis'},
            'LAS': {'lat': 36.1699, 'lon': -115.1398, 'city': 'Las Vegas'},
            'MIN': {'lat': 44.9537, 'lon': -93.2650, 'city': 'Minneapolis'},
            'NY': {'lat': 40.7128, 'lon': -74.0060, 'city': 'New York'},
            'PHX': {'lat': 33.4484, 'lon': -112.0740, 'city': 'Phoenix'},
            'SEA': {'lat': 47.6062, 'lon': -122.3321, 'city': 'Seattle'},
            'WAS': {'lat': 38.9072, 'lon': -77.0369, 'city': 'Washington'}
        }
    
    def fetch_data(self, player_ids: List[str], date_range: tuple, **kwargs) -> pd.DataFrame:
        """
        Fetch weather data for game locations and specified date range.
        
        Args:
            player_ids: List of player IDs (used to determine relevant teams/locations)
            date_range: Tuple of (start_date, end_date)
            **kwargs: Additional parameters like locations, weather_types
            
        Returns:
            DataFrame with weather context data
        """
        self.log_access("fetch_weather_data", len(player_ids), date_range)
        
        start_date, end_date = date_range
        locations = kwargs.get('locations', list(self.team_locations.keys()))
        weather_types = kwargs.get('weather_types', ['current', 'historical'])
        
        all_data = []
        
        for location in locations:
            if location not in self.team_locations:
                logger.warning(f"Unknown location: {location}")
                continue
                
            try:
                location_data = self.team_locations[location]
                
                # Fetch different types of weather data
                if 'current' in weather_types:
                    current_data = self._fetch_current_weather(location_data)
                    if current_data:
                        all_data.extend(current_data)
                
                if 'historical' in weather_types:
                    historical_data = self._fetch_historical_weather(
                        location_data, start_date, end_date
                    )
                    all_data.extend(historical_data)
                
                # Add air quality data if available
                if 'air_quality' in weather_types:
                    air_quality_data = self._fetch_air_quality(location_data)
                    if air_quality_data:
                        all_data.extend(air_quality_data)
                        
            except Exception as e:
                logger.error(f"Error fetching weather for {location}: {str(e)}")
                continue
        
        if not all_data:
            return pd.DataFrame()
            
        combined_df = pd.DataFrame(all_data)
        
        # Add derived weather features
        combined_df = self._add_derived_features(combined_df)
        
        return self.anonymize_data(combined_df)
    
    def _fetch_current_weather(self, location_data: Dict) -> List[Dict]:
        """Fetch current weather conditions for a location."""
        endpoint = f"{self.api_endpoint}/data/2.5/weather"
        params = {
            'lat': location_data['lat'],
            'lon': location_data['lon'],
            'appid': self.api_key,
            'units': 'imperial'  # Fahrenheit for US cities
        }
        
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()
            
            record = {
                'location': location_data['city'],
                'date': datetime.now().strftime('%Y-%m-%d'),
                'data_type': 'current_weather',
                'temperature_f': data['main']['temp'],
                'feels_like_f': data['main']['feels_like'],
                'humidity_percent': data['main']['humidity'],
                'pressure_hpa': data['main']['pressure'],
                'visibility_m': data.get('visibility', 0),
                'uv_index': 0,  # Requires separate API call
                'weather_condition': data['weather'][0]['main'],
                'weather_description': data['weather'][0]['description'],
                'cloud_cover_percent': data['clouds']['all'],
                'wind_speed_mph': data.get('wind', {}).get('speed', 0),
                'wind_direction_deg': data.get('wind', {}).get('deg', 0),
                'precipitation_mm': data.get('rain', {}).get('1h', 0) + data.get('snow', {}).get('1h', 0)
            }
            
            return [record]
            
        except Exception as e:
            logger.error(f"Error fetching current weather: {str(e)}")
            return []
    
    def _fetch_historical_weather(self, location_data: Dict, start_date: datetime,
                                 end_date: datetime) -> List[Dict]:
        """Fetch historical weather data for a location and date range."""
        records = []
        
        # OpenWeatherMap historical data requires timestamp
        current_date = start_date
        while current_date <= end_date:
            timestamp = int(current_date.timestamp())
            
            endpoint = f"{self.api_endpoint}/data/2.5/onecall/timemachine"
            params = {
                'lat': location_data['lat'],
                'lon': location_data['lon'],
                'dt': timestamp,
                'appid': self.api_key,
                'units': 'imperial'
            }
            
            try:
                response = requests.get(endpoint, params=params)
                response.raise_for_status()
                data = response.json()
                
                # Extract current day data
                current_weather = data.get('current', {})
                if current_weather:
                    record = {
                        'location': location_data['city'],
                        'date': current_date.strftime('%Y-%m-%d'),
                        'data_type': 'historical_weather',
                        'temperature_f': current_weather.get('temp', 0),
                        'feels_like_f': current_weather.get('feels_like', 0),
                        'humidity_percent': current_weather.get('humidity', 0),
                        'pressure_hpa': current_weather.get('pressure', 0),
                        'uv_index': current_weather.get('uvi', 0),
                        'weather_condition': current_weather.get('weather', [{}])[0].get('main', ''),
                        'weather_description': current_weather.get('weather', [{}])[0].get('description', ''),
                        'cloud_cover_percent': current_weather.get('clouds', 0),
                        'wind_speed_mph': current_weather.get('wind_speed', 0),
                        'wind_direction_deg': current_weather.get('wind_deg', 0),
                        'precipitation_mm': current_weather.get('rain', {}).get('1h', 0)
                    }
                    records.append(record)
                
                # Rate limiting - OpenWeatherMap allows 60 calls/minute for free tier
                import time
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error fetching historical weather for {current_date}: {str(e)}")
            
            current_date += timedelta(days=1)
        
        return records
    
    def _fetch_air_quality(self, location_data: Dict) -> List[Dict]:
        """Fetch air quality data for a location."""
        endpoint = f"{self.api_endpoint}/data/2.5/air_pollution"
        params = {
            'lat': location_data['lat'],
            'lon': location_data['lon'],
            'appid': self.api_key
        }
        
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()
            
            air_quality = data.get('list', [{}])[0]
            main_aqi = air_quality.get('main', {})
            components = air_quality.get('components', {})
            
            record = {
                'location': location_data['city'],
                'date': datetime.now().strftime('%Y-%m-%d'),
                'data_type': 'air_quality',
                'air_quality_index': main_aqi.get('aqi', 0),
                'co_concentration': components.get('co', 0),
                'no2_concentration': components.get('no2', 0),
                'o3_concentration': components.get('o3', 0),
                'pm2_5_concentration': components.get('pm2_5', 0),
                'pm10_concentration': components.get('pm10', 0),
                'so2_concentration': components.get('so2', 0),
                'nh3_concentration': components.get('nh3', 0)
            }
            
            return [record]
            
        except Exception as e:
            logger.error(f"Error fetching air quality: {str(e)}")
            return []
    
    def _add_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add derived weather features that may correlate with cycle symptoms."""
        if df.empty:
            return df
        
        # Temperature comfort zones
        df['temp_comfort'] = df['temperature_f'].apply(self._categorize_temperature)
        
        # Pressure change indicator (requires historical data)
        if 'pressure_hpa' in df.columns:
            df['pressure_category'] = df['pressure_hpa'].apply(self._categorize_pressure)
        
        # Heat index calculation (temperature + humidity)
        if 'temperature_f' in df.columns and 'humidity_percent' in df.columns:
            df['heat_index'] = df.apply(self._calculate_heat_index, axis=1)
        
        # Seasonal indicators
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['season'] = df['date'].apply(self._get_season)
        df['month'] = df['date'].dt.month
        
        # Weather severity scoring
        df['weather_severity_score'] = df.apply(self._calculate_weather_severity, axis=1)
        
        return df
    
    def _categorize_temperature(self, temp_f: float) -> str:
        """Categorize temperature into comfort zones."""
        if temp_f < 32:
            return 'freezing'
        elif temp_f < 50:
            return 'cold'
        elif temp_f < 70:
            return 'cool'
        elif temp_f < 80:
            return 'comfortable'
        elif temp_f < 90:
            return 'warm'
        else:
            return 'hot'
    
    def _categorize_pressure(self, pressure_hpa: float) -> str:
        """Categorize barometric pressure."""
        if pressure_hpa < 1000:
            return 'low'
        elif pressure_hpa < 1020:
            return 'normal'
        else:
            return 'high'
    
    def _calculate_heat_index(self, row) -> float:
        """Calculate heat index from temperature and humidity."""
        try:
            temp_f = row.get('temperature_f', 0)
            humidity = row.get('humidity_percent', 0)
            
            if temp_f < 80 or humidity < 40:
                return temp_f  # Heat index not applicable
            
            # Simplified heat index calculation
            hi = (temp_f + humidity) * 0.6 + 30
            return min(hi, 150)  # Cap at reasonable maximum
            
        except (TypeError, ValueError):
            return 0
    
    def _get_season(self, date) -> str:
        """Determine season from date."""
        if pd.isna(date):
            return 'unknown'
        
        month = date.month
        if month in [12, 1, 2]:
            return 'winter'
        elif month in [3, 4, 5]:
            return 'spring'
        elif month in [6, 7, 8]:
            return 'summer'
        else:
            return 'fall'
    
    def _calculate_weather_severity(self, row) -> float:
        """Calculate a composite weather severity score."""
        score = 0
        
        # Temperature extremes
        temp = row.get('temperature_f', 70)
        if temp < 32 or temp > 95:
            score += 2
        elif temp < 40 or temp > 85:
            score += 1
        
        # High humidity
        humidity = row.get('humidity_percent', 50)
        if humidity > 80:
            score += 1
        
        # Pressure changes
        pressure = row.get('pressure_hpa', 1013)
        if pressure < 1000 or pressure > 1025:
            score += 1
        
        # Precipitation
        precip = row.get('precipitation_mm', 0)
        if precip > 10:
            score += 1
        
        # Poor air quality
        aqi = row.get('air_quality_index', 1)
        if aqi > 3:  # Unhealthy for sensitive groups
            score += 2
        elif aqi > 2:  # Moderate
            score += 1
        
        return min(score, 8)  # Cap at 8 for reasonable scale
    
    def get_weather_summary(self, location: str, date_range: tuple) -> Dict[str, Any]:
        """
        Get weather summary statistics for a location and date range.
        
        Args:
            location: Location key (e.g., 'CHI', 'NY')
            date_range: Tuple of (start_date, end_date)
            
        Returns:
            Dictionary with weather summary statistics
        """
        if location not in self.team_locations:
            return {}
        
        # Fetch weather data for the specified range
        weather_df = self.fetch_data([], date_range, locations=[location])
        
        if weather_df.empty:
            return {}
        
        summary = {
            'location': self.team_locations[location]['city'],
            'date_range': date_range,
            'avg_temperature_f': weather_df['temperature_f'].mean(),
            'min_temperature_f': weather_df['temperature_f'].min(),
            'max_temperature_f': weather_df['temperature_f'].max(),
            'avg_humidity_percent': weather_df['humidity_percent'].mean(),
            'avg_pressure_hpa': weather_df['pressure_hpa'].mean(),
            'total_precipitation_mm': weather_df['precipitation_mm'].sum(),
            'avg_weather_severity': weather_df['weather_severity_score'].mean(),
            'most_common_condition': weather_df['weather_condition'].mode().iloc[0] if not weather_df.empty else 'unknown'
        }
        
        return summary
    
    def validate_data(self, df: pd.DataFrame) -> bool:
        """
        Validate weather data quality and reasonableness.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Boolean indicating validation success
        """
        if df.empty:
            return False
            
        required_columns = ['location', 'date', 'data_type']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            logger.error(f"Missing required columns: {missing_columns}")
            return False
        
        # Validate weather data ranges
        if 'temperature_f' in df.columns:
            extreme_temps = df[
                (df['temperature_f'] < -50) | (df['temperature_f'] > 130)
            ]
            if not extreme_temps.empty:
                logger.warning(f"Extreme temperature values: {len(extreme_temps)} records")
        
        if 'humidity_percent' in df.columns:
            invalid_humidity = df[
                (df['humidity_percent'] < 0) | (df['humidity_percent'] > 100)
            ]
            if not invalid_humidity.empty:
                logger.warning(f"Invalid humidity values: {len(invalid_humidity)} records")
                return False
        
        # Check date validity
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        future_dates = df[df['date'] > datetime.now()]
        if not future_dates.empty and df.iloc[0]['data_type'] != 'current_weather':
            logger.warning(f"Found {len(future_dates)} records with future dates")
        
        return True