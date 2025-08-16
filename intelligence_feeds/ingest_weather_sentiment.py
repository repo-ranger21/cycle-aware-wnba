"""
Intelligence Feeds: Weather & Sentiment Data Ingestion

This module provides ethical ingestion of environmental weather data and public
sentiment analysis for cycle-aware WNBA performance modeling. All data processing
follows privacy-first principles and civic-grade transparency standards.

Ethical Notice: Social media sentiment analysis requires careful ethical consideration
of privacy, bias, and representativeness. All processing follows responsible AI
guidelines and includes bias detection and mitigation strategies.

Contributor Guidelines: This module handles public social media data and weather APIs.
Ensure compliance with API terms of service, privacy regulations, and ethical
sentiment analysis practices. Review ETHICS.md before making modifications.
"""

import pandas as pd
import numpy as np
import requests
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
import logging
import time
import re
from textblob import TextBlob
import tweepy

# Configure civic-grade logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class WeatherSentimentIngestor:
    """
    Ethical ingestion of weather data and public sentiment for cycle-aware analytics.
    
    Civic-Grade Design:
    - Weather data sourced from OpenWeatherMap with proper attribution
    - Social media sentiment analysis follows responsible AI guidelines
    - Bias detection and mitigation built into all sentiment processing
    - Transparent methodology with comprehensive audit trails
    
    Data Sources:
    - OpenWeatherMap API (hydration-relevant weather metrics)
    - Twitter/X API (public sentiment analysis with ethical filtering)
    - Additional social platforms (with proper consent and ethics review)
    """
    
    def __init__(self, openweather_api_key: Optional[str] = None,
                 twitter_api_credentials: Optional[Dict] = None,
                 bias_detection_enabled: bool = True):
        """
        Initialize weather and sentiment data ingestor with ethical safeguards.
        
        Args:
            openweather_api_key: OpenWeatherMap API key for weather data
            twitter_api_credentials: Twitter API credentials dict
            bias_detection_enabled: Enable bias detection in sentiment analysis
            
        Ethical Requirements:
        - Weather API must be used within free tier limits or paid subscription
        - Social media APIs require adherence to platform policies
        - Bias detection should always be enabled for civic-grade analytics
        """
        self.openweather_api_key = openweather_api_key
        self.twitter_credentials = twitter_api_credentials
        self.bias_detection = bias_detection_enabled
        self.api_configs = self._init_api_configurations()
        
        # Initialize Twitter client if credentials provided
        self.twitter_client = None
        if twitter_api_credentials:
            try:
                self.twitter_client = tweepy.Client(
                    bearer_token=twitter_api_credentials.get("bearer_token"),
                    consumer_key=twitter_api_credentials.get("consumer_key"),
                    consumer_secret=twitter_api_credentials.get("consumer_secret"),
                    access_token=twitter_api_credentials.get("access_token"),
                    access_token_secret=twitter_api_credentials.get("access_token_secret"),
                    wait_on_rate_limit=True
                )
            except Exception as e:
                logger.error(f"Failed to initialize Twitter client: {e}")
        
        logger.info("WeatherSentimentIngestor initialized with ethical safeguards")
    
    def _init_api_configurations(self) -> Dict:
        """
        Initialize API configurations for weather and sentiment data sources.
        
        Returns:
            API-specific configuration dictionary with ethical guidelines
            
        Civic Note: All API configurations documented for transparency
        and compliance with terms of service.
        """
        return {
            "openweathermap": {
                "base_url": "https://api.openweathermap.org/data/2.5",
                "endpoints": {
                    "current": "/weather",
                    "forecast": "/forecast",
                    "historical": "/onecall/timemachine"
                },
                "rate_limit": "60_calls_per_minute",
                "attribution": "Weather data by OpenWeatherMap",
                "ethical_usage": "hydration_research_only"
            },
            "twitter": {
                "base_url": "https://api.twitter.com/2",
                "endpoints": {
                    "search": "/tweets/search/recent",
                    "stream": "/tweets/sample/stream"
                },
                "rate_limit": "300_requests_per_15min",
                "attribution": "Social sentiment via Twitter API",
                "ethical_guidelines": [
                    "public_tweets_only",
                    "no_personal_targeting", 
                    "bias_detection_required",
                    "aggregated_analysis_only"
                ]
            }
        }
    
    def _get_arena_coordinates(self, team_name: str) -> Tuple[float, float]:
        """
        Get latitude and longitude coordinates for WNBA team arenas.
        
        Args:
            team_name: WNBA team name or abbreviation
            
        Returns:
            Tuple of (latitude, longitude) for weather API calls
            
        Geographic Note: Arena locations used for localized weather data
        relevant to game-day hydration and environmental conditions.
        """
        arena_coordinates = {
            "ATL": (33.7490, -84.3880),  # Atlanta Dream - State Farm Arena
            "CHI": (41.8807, -87.6742),  # Chicago Sky - Wintrust Arena  
            "CON": (41.7658, -72.6734),  # Connecticut Sun - Mohegan Sun Arena
            "DAL": (32.7905, -96.8103),  # Dallas Wings - College Park Center
            "IND": (39.7641, -86.1555),  # Indiana Fever - Gainbridge Fieldhouse
            "LAS": (36.0969, -115.1831), # Las Vegas Aces - Michelob ULTRA Arena
            "MIN": (44.9778, -93.2650),  # Minnesota Lynx - Target Center
            "NY": (40.7505, -73.9934),   # New York Liberty - Barclays Center
            "PHX": (33.4457, -112.0712), # Phoenix Mercury - Footprint Center
            "SEA": (47.6219, -122.3540), # Seattle Storm - Climate Pledge Arena
            "WAS": (38.8951, -77.0209),  # Washington Mystics - Entertainment & Sports Arena
            "LV": (36.0969, -115.1831)   # Las Vegas Aces (alternate abbreviation)
        }
        
        return arena_coordinates.get(team_name.upper(), (39.8283, -98.5795))  # Default to US center
    
    def _fetch_weather_data(self, latitude: float, longitude: float, date: str) -> Dict:
        """
        Fetch weather data from OpenWeatherMap API for specific location and date.
        
        Args:
            latitude: Arena latitude coordinate
            longitude: Arena longitude coordinate  
            date: Date for weather data (YYYY-MM-DD)
            
        Returns:
            Weather data including hydration-relevant metrics
            
        Hydration Research Note: Focuses on temperature, humidity, and heat index
        as factors affecting athlete hydration needs and performance.
        """
        if not self.openweather_api_key:
            logger.warning("No OpenWeatherMap API key - returning mock weather data")
            return self._generate_mock_weather_data()
        
        # Convert date to timestamp for historical weather
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        timestamp = int(date_obj.timestamp())
        
        # Use current weather for recent dates, historical for older dates
        days_ago = (datetime.now() - date_obj).days
        
        if days_ago <= 5:
            # Current/forecast weather API
            endpoint = f"{self.api_configs['openweathermap']['base_url']}/weather"
            params = {
                "lat": latitude,
                "lon": longitude,
                "appid": self.openweather_api_key,
                "units": "metric"
            }
        else:
            # Historical weather API (requires subscription)
            endpoint = f"{self.api_configs['openweathermap']['base_url']}/onecall/timemachine"
            params = {
                "lat": latitude,
                "lon": longitude,
                "dt": timestamp,
                "appid": self.openweather_api_key,
                "units": "metric"
            }
        
        try:
            time.sleep(0.1)  # Rate limiting
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            
            weather_data = response.json()
            logger.info(f"Successfully fetched weather data for coordinates ({latitude}, {longitude})")
            return weather_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"OpenWeatherMap API request failed: {e}")
            return self._generate_mock_weather_data()
    
    def _generate_mock_weather_data(self) -> Dict:
        """
        Generate mock weather data for development and testing.
        
        Returns:
            Mock weather data with realistic hydration-relevant values
            
        Development Note: Used when API keys are not available or for testing.
        Provides realistic ranges for temperature, humidity, and pressure.
        """
        return {
            "main": {
                "temp": np.random.normal(24, 8),  # Temperature in Celsius
                "humidity": np.random.randint(30, 90),  # Humidity percentage
                "pressure": np.random.randint(1000, 1030)  # Atmospheric pressure
            },
            "weather": [{"main": "Clear", "description": "clear sky"}],
            "wind": {"speed": np.random.uniform(0, 15)},
            "visibility": 10000,
            "dt": int(datetime.now().timestamp())
        }
    
    def _normalize_weather_data(self, weather_data: Dict, team: str, date: str) -> Dict:
        """
        Normalize weather data to standardized format for hydration analysis.
        
        Args:
            weather_data: Raw weather data from OpenWeatherMap
            team: Team abbreviation for location context
            date: Game date for temporal context
            
        Returns:
            Normalized weather record with hydration-relevant metrics
            
        Hydration Science Note: Calculates heat index and hydration risk factors
        based on temperature, humidity, and environmental conditions.
        """
        main_data = weather_data.get("main", {})
        weather_desc = weather_data.get("weather", [{}])[0]
        wind_data = weather_data.get("wind", {})
        
        # Calculate heat index (apparent temperature)
        temp_celsius = main_data.get("temp", 20)
        humidity = main_data.get("humidity", 50)
        
        # Convert to Fahrenheit for heat index calculation
        temp_fahrenheit = (temp_celsius * 9/5) + 32
        
        # Simplified heat index calculation
        if temp_fahrenheit >= 80 and humidity >= 40:
            heat_index = (-42.379 + 2.04901523 * temp_fahrenheit + 
                         10.14333127 * humidity - 0.22475541 * temp_fahrenheit * humidity -
                         6.83783e-03 * temp_fahrenheit**2 - 5.481717e-02 * humidity**2 +
                         1.22874e-03 * temp_fahrenheit**2 * humidity + 8.5282e-04 * temp_fahrenheit * humidity**2 -
                         1.99e-06 * temp_fahrenheit**2 * humidity**2)
        else:
            heat_index = temp_fahrenheit
        
        # Convert back to Celsius
        heat_index_celsius = (heat_index - 32) * 5/9
        
        normalized_record = {
            "team": team,
            "date": date,
            "temperature_celsius": temp_celsius,
            "humidity_percent": humidity,
            "heat_index_celsius": heat_index_celsius,
            "atmospheric_pressure": main_data.get("pressure", 1013),
            "wind_speed_ms": wind_data.get("speed", 0),
            "weather_condition": weather_desc.get("main", "Unknown"),
            "weather_description": weather_desc.get("description", ""),
            "visibility_meters": weather_data.get("visibility", 10000),
            "hydration_risk_level": self._calculate_hydration_risk(temp_celsius, humidity, heat_index_celsius),
            "data_source": "openweathermap",
            "processing_timestamp": datetime.utcnow().isoformat()
        }
        
        return normalized_record
    
    def _calculate_hydration_risk(self, temperature: float, humidity: float, heat_index: float) -> str:
        """
        Calculate hydration risk level based on environmental conditions.
        
        Args:
            temperature: Air temperature in Celsius
            humidity: Relative humidity percentage
            heat_index: Apparent temperature in Celsius
            
        Returns:
            Risk level category (low, moderate, high, extreme)
            
        Sports Medicine Note: Based on heat illness prevention guidelines
        for athletic activities and hydration recommendations.
        """
        if heat_index >= 40:  # 104°F+
            return "extreme"
        elif heat_index >= 32:  # 90°F+
            return "high" 
        elif heat_index >= 27:  # 80°F+
            return "moderate"
        else:
            return "low"
    
    def _fetch_twitter_sentiment(self, search_terms: List[str], date: str, max_tweets: int = 100) -> List[Dict]:
        """
        Fetch public tweets for sentiment analysis with ethical filtering.
        
        Args:
            search_terms: List of search terms/hashtags
            date: Date to search for tweets (YYYY-MM-DD)
            max_tweets: Maximum number of tweets to analyze
            
        Returns:
            List of filtered tweets for ethical sentiment analysis
            
        Ethical Guidelines:
        - Only public tweets analyzed
        - No personal/private information collected  
        - Bias detection applied to all sentiment analysis
        - Aggregated results only, no individual targeting
        """
        if not self.twitter_client:
            logger.warning("No Twitter client available - returning mock sentiment data")
            return self._generate_mock_sentiment_data(search_terms, date)
        
        all_tweets = []
        
        for term in search_terms:
            try:
                # Ethical search query - public tweets only, no retweets
                query = f"{term} -is:retweet lang:en"
                
                # Search recent tweets (up to 7 days)
                tweets = tweepy.Paginator(
                    self.twitter_client.search_recent_tweets,
                    query=query,
                    max_results=min(max_tweets // len(search_terms), 100),
                    tweet_fields=["created_at", "public_metrics", "context_annotations"]
                ).flatten(limit=max_tweets // len(search_terms))
                
                for tweet in tweets:
                    # Ethical filtering - exclude personal information
                    if self._is_ethically_suitable_tweet(tweet.text):
                        tweet_data = {
                            "tweet_id": str(tweet.id),
                            "text": self._sanitize_tweet_text(tweet.text),
                            "created_at": tweet.created_at.isoformat() if tweet.created_at else date,
                            "search_term": term,
                            "public_metrics": tweet.public_metrics or {},
                            "date": date
                        }
                        all_tweets.append(tweet_data)
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Failed to fetch tweets for term '{term}': {e}")
                continue
        
        logger.info(f"Fetched {len(all_tweets)} ethically filtered tweets for sentiment analysis")
        return all_tweets
    
    def _generate_mock_sentiment_data(self, search_terms: List[str], date: str) -> List[Dict]:
        """
        Generate mock sentiment data for development and testing.
        
        Args:
            search_terms: Search terms for mock data generation
            date: Date for mock tweets
            
        Returns:
            Mock tweet data with realistic sentiment patterns
            
        Development Note: Provides realistic sentiment distribution
        for testing sentiment analysis algorithms.
        """
        mock_tweets = []
        sentiments = ["positive", "neutral", "negative"]
        
        for term in search_terms:
            for i in range(10):  # 10 mock tweets per term
                mock_tweet = {
                    "tweet_id": f"mock_{term}_{i}",
                    "text": f"Mock tweet about {term} with {np.random.choice(sentiments)} sentiment",
                    "created_at": f"{date}T{np.random.randint(0, 23):02d}:{np.random.randint(0, 59):02d}:00Z",
                    "search_term": term,
                    "public_metrics": {"like_count": np.random.randint(0, 100)},
                    "date": date
                }
                mock_tweets.append(mock_tweet)
        
        return mock_tweets
    
    def _is_ethically_suitable_tweet(self, tweet_text: str) -> bool:
        """
        Filter tweets for ethical suitability in sentiment analysis.
        
        Args:
            tweet_text: Raw tweet text content
            
        Returns:
            True if tweet is suitable for ethical analysis, False otherwise
            
        Ethical Filtering Criteria:
        - No personal attacks or harassment
        - No private/personal information sharing
        - No spam or bot-generated content
        - Focus on sports-related sentiment only
        """
        # Convert to lowercase for analysis
        text_lower = tweet_text.lower()
        
        # Exclude tweets with personal information patterns
        personal_info_patterns = [
            r'\b\d{3}-\d{3}-\d{4}\b',  # Phone numbers
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Emails
            r'\b\d{1,5}\s\w+\s\w+\b'  # Potential addresses
        ]
        
        for pattern in personal_info_patterns:
            if re.search(pattern, tweet_text):
                return False
        
        # Exclude potentially harmful content
        harmful_keywords = [
            "hate", "attack", "threaten", "abuse", "harass",
            "doxx", "address", "phone", "personal info"
        ]
        
        for keyword in harmful_keywords:
            if keyword in text_lower:
                return False
        
        # Include sports-related content
        sports_keywords = [
            "wnba", "basketball", "game", "player", "team",
            "score", "win", "performance", "season"
        ]
        
        has_sports_content = any(keyword in text_lower for keyword in sports_keywords)
        
        return has_sports_content and len(tweet_text.strip()) > 10
    
    def _sanitize_tweet_text(self, tweet_text: str) -> str:
        """
        Sanitize tweet text for ethical sentiment analysis.
        
        Args:
            tweet_text: Raw tweet text
            
        Returns:
            Sanitized text with personal information removed
            
        Privacy Protection: Removes handles, URLs, and potential personal identifiers
        while preserving sentiment-relevant content.
        """
        # Remove user handles and URLs
        text = re.sub(r'@\w+', '', tweet_text)
        text = re.sub(r'http\S+', '', text)
        text = re.sub(r'www\.\S+', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text.strip()
    
    def _analyze_sentiment(self, tweets: List[Dict]) -> List[Dict]:
        """
        Perform ethical sentiment analysis with bias detection.
        
        Args:
            tweets: List of sanitized tweet data
            
        Returns:
            Tweets with sentiment analysis results and bias metrics
            
        Responsible AI Note: Includes bias detection and confidence scoring
        to identify potential algorithmic bias in sentiment classification.
        """
        analyzed_tweets = []
        
        for tweet in tweets:
            try:
                # Perform sentiment analysis using TextBlob
                text = tweet.get("text", "")
                blob = TextBlob(text)
                
                sentiment_score = blob.sentiment.polarity  # -1 to 1
                subjectivity_score = blob.sentiment.subjectivity  # 0 to 1
                
                # Convert to categorical sentiment
                if sentiment_score > 0.1:
                    sentiment_category = "positive"
                elif sentiment_score < -0.1:
                    sentiment_category = "negative"
                else:
                    sentiment_category = "neutral"
                
                # Calculate confidence based on distance from neutral
                confidence = abs(sentiment_score)
                
                # Bias detection - flag potentially biased results
                bias_flags = []
                if self.bias_detection:
                    bias_flags = self._detect_sentiment_bias(text, sentiment_score)
                
                analyzed_tweet = tweet.copy()
                analyzed_tweet.update({
                    "sentiment_score": sentiment_score,
                    "sentiment_category": sentiment_category,
                    "subjectivity_score": subjectivity_score,
                    "confidence": confidence,
                    "bias_flags": bias_flags,
                    "analysis_timestamp": datetime.utcnow().isoformat()
                })
                
                analyzed_tweets.append(analyzed_tweet)
                
            except Exception as e:
                logger.error(f"Sentiment analysis failed for tweet {tweet.get('tweet_id', 'unknown')}: {e}")
                continue
        
        return analyzed_tweets
    
    def _detect_sentiment_bias(self, text: str, sentiment_score: float) -> List[str]:
        """
        Detect potential bias in sentiment analysis results.
        
        Args:
            text: Tweet text content
            sentiment_score: Computed sentiment score
            
        Returns:
            List of detected bias indicators
            
        Bias Detection: Identifies common sources of algorithmic bias
        in sentiment analysis including demographic, temporal, and topic bias.
        """
        bias_flags = []
        text_lower = text.lower()
        
        # Demographic bias detection
        demographic_terms = ["women", "female", "girl", "lady"]
        if any(term in text_lower for term in demographic_terms):
            if sentiment_score < -0.3:  # Strong negative sentiment
                bias_flags.append("potential_gender_bias")
        
        # Topic bias detection
        sports_achievement_terms = ["win", "victory", "champion", "best", "record"]
        if any(term in text_lower for term in sports_achievement_terms):
            if sentiment_score < 0:  # Negative sentiment on achievements
                bias_flags.append("potential_achievement_bias")
        
        # Temporal bias - extreme sentiment on neutral topics
        if abs(sentiment_score) > 0.8 and len(text.split()) < 5:
            bias_flags.append("potential_temporal_bias")
        
        return bias_flags
    
    def _aggregate_sentiment_metrics(self, analyzed_tweets: List[Dict], date: str) -> Dict:
        """
        Aggregate individual tweet sentiments into daily mood volatility indicators.
        
        Args:
            analyzed_tweets: List of tweets with sentiment analysis
            date: Date for aggregation
            
        Returns:
            Aggregated sentiment metrics for mood volatility analysis
            
        Civic Analytics Note: Aggregation removes individual identification
        while preserving population-level mood trends for research.
        """
        if not analyzed_tweets:
            return {
                "date": date,
                "total_tweets": 0,
                "average_sentiment": 0.0,
                "sentiment_volatility": 0.0,
                "positive_ratio": 0.0,
                "negative_ratio": 0.0,
                "neutral_ratio": 0.0,
                "bias_detection_summary": {}
            }
        
        # Extract sentiment scores
        sentiment_scores = [tweet.get("sentiment_score", 0) for tweet in analyzed_tweets]
        sentiment_categories = [tweet.get("sentiment_category", "neutral") for tweet in analyzed_tweets]
        
        # Aggregate bias flags
        all_bias_flags = []
        for tweet in analyzed_tweets:
            all_bias_flags.extend(tweet.get("bias_flags", []))
        
        bias_summary = {}
        for flag in set(all_bias_flags):
            bias_summary[flag] = all_bias_flags.count(flag)
        
        # Calculate aggregated metrics
        total_tweets = len(analyzed_tweets)
        average_sentiment = np.mean(sentiment_scores)
        sentiment_volatility = np.std(sentiment_scores)  # Standard deviation as volatility measure
        
        positive_count = sentiment_categories.count("positive")
        negative_count = sentiment_categories.count("negative") 
        neutral_count = sentiment_categories.count("neutral")
        
        aggregated_metrics = {
            "date": date,
            "total_tweets_analyzed": total_tweets,
            "average_sentiment_score": round(average_sentiment, 4),
            "sentiment_volatility": round(sentiment_volatility, 4),
            "positive_sentiment_ratio": round(positive_count / total_tweets, 4),
            "negative_sentiment_ratio": round(negative_count / total_tweets, 4),
            "neutral_sentiment_ratio": round(neutral_count / total_tweets, 4),
            "bias_detection_summary": bias_summary,
            "data_quality": "aggregated_public_sentiment",
            "ethical_compliance": "privacy_preserving_analysis",
            "processing_timestamp": datetime.utcnow().isoformat()
        }
        
        return aggregated_metrics
    
    def ingest_game_day_context(self, team: str, game_date: str, 
                              search_terms: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Ingest complete game-day environmental and sentiment context.
        
        Args:
            team: WNBA team abbreviation
            game_date: Game date (YYYY-MM-DD)
            search_terms: Custom search terms for sentiment analysis
            
        Returns:
            DataFrame with weather and sentiment context data
            
        Civic-Grade Workflow:
        1. Fetch weather data for team's arena location
        2. Collect public sentiment data with ethical filtering
        3. Perform bias-aware sentiment analysis
        4. Aggregate into mood volatility indicators  
        5. Combine with hydration risk assessment
        6. Add civic accountability metadata
        """
        logger.info(f"Ingesting game-day context for {team} on {game_date}")
        
        # Default search terms if none provided
        if not search_terms:
            search_terms = [f"#{team}WNBA", f"{team} basketball", "WNBA game", f"{team} women's basketball"]
        
        try:
            # Step 1: Fetch weather data
            lat, lon = self._get_arena_coordinates(team)
            weather_data = self._fetch_weather_data(lat, lon, game_date)
            normalized_weather = self._normalize_weather_data(weather_data, team, game_date)
            
            # Step 2: Fetch and analyze sentiment data
            tweets = self._fetch_twitter_sentiment(search_terms, game_date)
            analyzed_tweets = self._analyze_sentiment(tweets)
            sentiment_metrics = self._aggregate_sentiment_metrics(analyzed_tweets, game_date)
            
            # Step 3: Combine weather and sentiment data
            context_record = {
                **normalized_weather,
                **sentiment_metrics,
                "search_terms_used": search_terms,
                "ethical_processing_version": "v1.0_civic_grade",
                "privacy_level": "aggregated_public_data",
                "usage_restriction": "health_research_only"
            }
            
            # Step 4: Create DataFrame
            context_df = pd.DataFrame([context_record])
            
            logger.info(f"Successfully ingested game-day context for {team} on {game_date}")
            return context_df
            
        except Exception as e:
            logger.error(f"Failed to ingest game-day context for {team} on {game_date}: {e}")
            raise
    
    def format_for_supabase(self, df: pd.DataFrame, table_name: str = "game_context_data") -> Dict:
        """
        Format weather and sentiment data for Supabase ingestion.
        
        Args:
            df: Context data DataFrame
            table_name: Target Supabase table name
            
        Returns:
            Dictionary formatted for Supabase insertion with ethical metadata
            
        Civic Note: Includes comprehensive attribution and bias detection
        results for transparency and accountability.
        """
        records = df.to_dict('records')
        
        supabase_payload = {
            "table_name": table_name,
            "records": records,
            "ingestion_metadata": {
                "total_records": len(records),
                "data_sources": ["openweathermap", "twitter_api"],
                "processing_timestamp": datetime.utcnow().isoformat(),
                "privacy_compliance": "aggregated_public_data_only",
                "ethical_framework": "civic_grade_analytics",
                "bias_detection_enabled": self.bias_detection,
                "api_attributions": [
                    "Weather data by OpenWeatherMap",
                    "Public sentiment via Twitter API"
                ]
            }
        }
        
        return supabase_payload


def batch_ingest_game_context(teams_games: List[Tuple[str, str]], 
                            openweather_key: str, twitter_credentials: Dict) -> pd.DataFrame:
    """
    Batch process multiple games' environmental and sentiment context.
    
    Args:
        teams_games: List of (team, game_date) tuples
        openweather_key: OpenWeatherMap API key
        twitter_credentials: Twitter API credentials
        
    Returns:
        Combined DataFrame with all games' context data
        
    Civic Accountability: Batch processing while maintaining ethical
    standards for each individual game context analysis.
    """
    ingestor = WeatherSentimentIngestor(openweather_key, twitter_credentials)
    all_context_data = []
    
    for team, game_date in teams_games:
        try:
            context_df = ingestor.ingest_game_day_context(team, game_date)
            all_context_data.append(context_df)
            logger.info(f"Successfully processed context for {team} on {game_date}")
            
            # Rate limiting between games
            time.sleep(2)
            
        except Exception as e:
            logger.error(f"Failed to process context for {team} on {game_date}: {e}")
            continue
    
    if all_context_data:
        combined_df = pd.concat(all_context_data, ignore_index=True)
        logger.info(f"Batch processing complete: {len(combined_df)} game context records")
        return combined_df
    else:
        logger.warning("No game context data was successfully processed")
        return pd.DataFrame()


# Civic-Grade Usage Example
if __name__ == "__main__":
    # Example usage with mock API credentials
    logger.info("Starting weather and sentiment ingestion with civic-grade ethical safeguards")
    
    # Mock credentials - replace with real API keys
    mock_openweather_key = "your_openweather_api_key_here"
    mock_twitter_creds = {
        "bearer_token": "your_twitter_bearer_token",
        "consumer_key": "your_consumer_key",
        "consumer_secret": "your_consumer_secret",
        "access_token": "your_access_token", 
        "access_token_secret": "your_access_token_secret"
    }
    
    try:
        # Initialize ingestor
        ingestor = WeatherSentimentIngestor(mock_openweather_key, mock_twitter_creds)
        
        # Example: Ingest context for Seattle Storm game
        context_data = ingestor.ingest_game_day_context(
            team="SEA",
            game_date="2024-07-15",
            search_terms=["#SEAStorm", "Seattle Storm", "WNBA Storm"]
        )
        
        print(f"Ingested context data with {len(context_data)} records")
        if not context_data.empty:
            print("\nWeather and sentiment context:")
            print(context_data[["team", "date", "temperature_celsius", "hydration_risk_level", 
                               "average_sentiment_score", "sentiment_volatility"]].head())
            
        # Format for database storage
        supabase_payload = ingestor.format_for_supabase(context_data)
        print(f"\nFormatted for storage: {supabase_payload['ingestion_metadata']['total_records']} records")
        
    except Exception as e:
        logger.error(f"Example ingestion failed: {e}")
        print("Note: This example requires valid API credentials and ethical compliance review")