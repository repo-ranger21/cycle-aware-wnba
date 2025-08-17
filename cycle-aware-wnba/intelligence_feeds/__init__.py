"""
Cycle-Aware WNBA Intelligence Feeds Module

This module provides data ingestion capabilities for multiple sources including:
- Clue cycle data via Terra API
- Wearable data using OAuth
- WNBA performance data from SportsData.io  
- Weather data from OpenWeatherMap
- Sentiment data from Twitter NLP

All implementations follow privacy-first, ethical data handling principles.
"""

from .base import DataSourceBase
from .clue_terra import ClueDataSource
from .wearable_oauth import WearableDataSource
from .wnba_sportsdata import WNBADataSource
from .weather_openweather import WeatherDataSource
from .sentiment_twitter import SentimentDataSource

__all__ = [
    'DataSourceBase',
    'ClueDataSource', 
    'WearableDataSource',
    'WNBADataSource',
    'WeatherDataSource',
    'SentimentDataSource'
]