"""
Sentiment Data Ingestion using Twitter NLP

This module provides sentiment analysis of social media content related to
WNBA players and teams for understanding public perception and potential
stress factors that could influence performance.

Privacy Notice: Only public social media content is analyzed. No personal
direct messages or private content is accessed.
"""

import pandas as pd
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
import re
from .base import DataSourceBase

logger = logging.getLogger(__name__)


class SentimentDataSource(DataSourceBase):
    """
    Sentiment analysis data source using Twitter API and NLP.
    
    Analyzes public social media sentiment including:
    - Player mentions and reactions
    - Team-related discussions
    - Game performance reactions
    - General WNBA sentiment trends
    - Media coverage sentiment
    """
    
    def __init__(self, twitter_config: Dict[str, str], nlp_service_config: Dict[str, str] = None):
        """
        Initialize sentiment data source with Twitter API and NLP service credentials.
        
        Args:
            twitter_config: Dict with Twitter API v2 credentials
            nlp_service_config: Optional dict with external NLP service config
        """
        ethical_compliance = {
            'consent_verified': True,  # Public social media data only
            'privacy_level': 'public',
            'data_retention': '30_days',
            'medical_grade': False,
            'audit_trail': True,
            'data_type': 'public_sentiment',
            'no_private_content': True
        }
        
        super().__init__("Sentiment Twitter NLP", ethical_compliance)
        
        self.twitter_config = twitter_config
        self.nlp_service_config = nlp_service_config or {}
        
        # Twitter API headers
        self.twitter_headers = {
            'Authorization': f"Bearer {twitter_config.get('bearer_token', '')}",
            'Content-Type': 'application/json'
        }
        
        # Basic sentiment keywords for rule-based analysis
        self.positive_keywords = [
            'amazing', 'excellent', 'great', 'fantastic', 'awesome', 'outstanding',
            'incredible', 'brilliant', 'superb', 'clutch', 'dominate', 'queen'
        ]
        
        self.negative_keywords = [
            'terrible', 'awful', 'horrible', 'disappointing', 'frustrated',
            'angry', 'upset', 'pathetic', 'useless', 'trash'
        ]
        
        # WNBA teams mapping for searches
        self.team_handles = {
            'ATL': 'atlhawks',  # Note: These would be actual WNBA team handles
            'CHI': 'chicagosky',
            'CONN': 'connecticutsun',
            'DAL': 'dallaswings',
            'IND': 'indianafever',
            'LAS': 'lvaces',
            'MIN': 'minnesotalynx',
            'NY': 'nyliberty',
            'PHX': 'phoenixmercury',
            'SEA': 'seattlestorm',
            'WAS': 'washingtonmystics'
        }
    
    def fetch_data(self, player_ids: List[str], date_range: tuple, **kwargs) -> pd.DataFrame:
        """
        Fetch sentiment data for specified players and date range.
        
        Args:
            player_ids: List of player names or handles to search for
            date_range: Tuple of (start_date, end_date)
            **kwargs: Additional parameters like search_terms, sentiment_types
            
        Returns:
            DataFrame with sentiment analysis data
        """
        self.log_access("fetch_sentiment_data", len(player_ids), date_range)
        
        start_date, end_date = date_range
        search_terms = kwargs.get('search_terms', [])
        sentiment_types = kwargs.get('sentiment_types', ['mentions', 'reactions', 'news'])
        max_tweets_per_query = kwargs.get('max_tweets', 100)
        
        all_data = []
        
        for player_id in player_ids:
            try:
                player_data = []
                
                # Search for player mentions
                if 'mentions' in sentiment_types:
                    mentions_data = self._fetch_player_mentions(
                        player_id, start_date, end_date, max_tweets_per_query
                    )
                    player_data.extend(mentions_data)
                
                # Search for game reaction posts
                if 'reactions' in sentiment_types:
                    reactions_data = self._fetch_game_reactions(
                        player_id, start_date, end_date, max_tweets_per_query
                    )
                    player_data.extend(reactions_data)
                
                # Search for news/media coverage
                if 'news' in sentiment_types:
                    news_data = self._fetch_news_sentiment(
                        player_id, start_date, end_date, max_tweets_per_query
                    )
                    player_data.extend(news_data)
                
                # Process additional search terms
                for term in search_terms:
                    term_data = self._fetch_custom_search(
                        f"{player_id} {term}", start_date, end_date, max_tweets_per_query
                    )
                    player_data.extend(term_data)
                
                if player_data:
                    player_df = pd.DataFrame(player_data)
                    player_df['target_player'] = player_id
                    all_data.append(player_df)
                    
            except Exception as e:
                logger.error(f"Error fetching sentiment for {player_id}: {str(e)}")
                continue
        
        if not all_data:
            return pd.DataFrame()
            
        combined_df = pd.concat(all_data, ignore_index=True)
        
        # Perform sentiment analysis on collected data
        combined_df = self._analyze_sentiment(combined_df)
        
        # Add aggregated sentiment metrics
        combined_df = self._add_sentiment_metrics(combined_df)
        
        return self.anonymize_data(combined_df)
    
    def _fetch_player_mentions(self, player_name: str, start_date: datetime,
                              end_date: datetime, max_tweets: int) -> List[Dict]:
        """Fetch tweets mentioning a specific player."""
        # Build search query
        query = f'"{player_name}" (WNBA OR basketball) -is:retweet lang:en'
        
        return self._search_tweets(query, start_date, end_date, max_tweets, 'player_mention')
    
    def _fetch_game_reactions(self, player_name: str, start_date: datetime,
                             end_date: datetime, max_tweets: int) -> List[Dict]:
        """Fetch reaction tweets during/after games."""
        # Search for game-related reactions
        game_terms = ['game', 'tonight', 'scored', 'points', 'rebounds', 'assists', 'clutch', 'MVP']
        query = f'"{player_name}" ({" OR ".join(game_terms)}) WNBA -is:retweet lang:en'
        
        return self._search_tweets(query, start_date, end_date, max_tweets, 'game_reaction')
    
    def _fetch_news_sentiment(self, player_name: str, start_date: datetime,
                             end_date: datetime, max_tweets: int) -> List[Dict]:
        """Fetch news and media coverage sentiment."""
        # Search for news/media accounts mentioning the player
        news_terms = ['breaking', 'report', 'news', 'update', 'analysis', 'interview']
        query = f'"{player_name}" ({" OR ".join(news_terms)}) WNBA -is:retweet lang:en'
        
        return self._search_tweets(query, start_date, end_date, max_tweets, 'news_coverage')
    
    def _fetch_custom_search(self, search_query: str, start_date: datetime,
                            end_date: datetime, max_tweets: int) -> List[Dict]:
        """Fetch tweets for custom search terms."""
        full_query = f'{search_query} WNBA -is:retweet lang:en'
        
        return self._search_tweets(full_query, start_date, end_date, max_tweets, 'custom_search')
    
    def _search_tweets(self, query: str, start_date: datetime, end_date: datetime,
                      max_tweets: int, content_type: str) -> List[Dict]:
        """Search tweets using Twitter API v2."""
        endpoint = "https://api.twitter.com/2/tweets/search/recent"
        
        params = {
            'query': query,
            'max_results': min(max_tweets, 100),  # API limit
            'tweet.fields': 'created_at,public_metrics,context_annotations,lang,author_id',
            'start_time': start_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'end_time': end_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        }
        
        try:
            response = requests.get(endpoint, headers=self.twitter_headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            tweets = data.get('data', [])
            records = []
            
            for tweet in tweets:
                record = {
                    'tweet_id': tweet['id'],
                    'date': tweet['created_at'][:10],  # Extract date part
                    'content': tweet['text'],
                    'content_type': content_type,
                    'author_id': tweet.get('author_id', 'unknown'),
                    'retweet_count': tweet.get('public_metrics', {}).get('retweet_count', 0),
                    'like_count': tweet.get('public_metrics', {}).get('like_count', 0),
                    'reply_count': tweet.get('public_metrics', {}).get('reply_count', 0),
                    'quote_count': tweet.get('public_metrics', {}).get('quote_count', 0),
                    'raw_data': tweet  # Store for additional analysis
                }
                records.append(record)
            
            return records
            
        except requests.RequestException as e:
            logger.error(f"Twitter API request failed: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error processing Twitter data: {str(e)}")
            return []
    
    def _analyze_sentiment(self, df: pd.DataFrame) -> pd.DataFrame:
        """Perform sentiment analysis on tweet content."""
        if df.empty or 'content' not in df.columns:
            return df
        
        # Use external NLP service if configured, otherwise use rule-based approach
        if self.nlp_service_config.get('service_url'):
            df = self._analyze_with_external_service(df)
        else:
            df = self._analyze_with_rule_based(df)
        
        return df
    
    def _analyze_with_external_service(self, df: pd.DataFrame) -> pd.DataFrame:
        """Analyze sentiment using external NLP service (e.g., AWS Comprehend, Azure Text Analytics)."""
        service_url = self.nlp_service_config['service_url']
        api_key = self.nlp_service_config.get('api_key', '')
        
        sentiment_scores = []
        
        for content in df['content']:
            try:
                # Example for generic sentiment API
                payload = {'text': content}
                headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
                
                response = requests.post(service_url, json=payload, headers=headers)
                response.raise_for_status()
                
                sentiment_data = response.json()
                score = {
                    'sentiment_label': sentiment_data.get('sentiment', 'neutral'),
                    'sentiment_score': sentiment_data.get('confidence', 0.5),
                    'positive_score': sentiment_data.get('positive', 0),
                    'negative_score': sentiment_data.get('negative', 0),
                    'neutral_score': sentiment_data.get('neutral', 0)
                }
                
            except Exception as e:
                logger.error(f"External sentiment analysis failed: {str(e)}")
                score = {
                    'sentiment_label': 'neutral',
                    'sentiment_score': 0.5,
                    'positive_score': 0.33,
                    'negative_score': 0.33,
                    'neutral_score': 0.34
                }
            
            sentiment_scores.append(score)
        
        # Add sentiment columns to dataframe
        sentiment_df = pd.DataFrame(sentiment_scores)
        return pd.concat([df, sentiment_df], axis=1)
    
    def _analyze_with_rule_based(self, df: pd.DataFrame) -> pd.DataFrame:
        """Analyze sentiment using rule-based approach with keyword matching."""
        sentiment_results = []
        
        for content in df['content']:
            content_lower = content.lower()
            
            # Clean content for analysis
            content_clean = re.sub(r'[^\w\s]', ' ', content_lower)
            words = content_clean.split()
            
            # Count positive and negative keywords
            positive_count = sum(1 for word in words if word in self.positive_keywords)
            negative_count = sum(1 for word in words if word in self.negative_keywords)
            
            # Simple scoring logic
            if positive_count > negative_count:
                sentiment_label = 'positive'
                sentiment_score = min(0.5 + (positive_count * 0.1), 1.0)
            elif negative_count > positive_count:
                sentiment_label = 'negative' 
                sentiment_score = max(0.5 - (negative_count * 0.1), 0.0)
            else:
                sentiment_label = 'neutral'
                sentiment_score = 0.5
            
            # Additional heuristics
            if '!' in content or content.isupper():
                # Exclamation or all caps might indicate stronger sentiment
                if sentiment_label == 'positive':
                    sentiment_score = min(sentiment_score + 0.1, 1.0)
                elif sentiment_label == 'negative':
                    sentiment_score = max(sentiment_score - 0.1, 0.0)
            
            result = {
                'sentiment_label': sentiment_label,
                'sentiment_score': sentiment_score,
                'positive_score': max(0, sentiment_score - 0.5) * 2 if sentiment_label == 'positive' else 0,
                'negative_score': max(0, 0.5 - sentiment_score) * 2 if sentiment_label == 'negative' else 0,
                'neutral_score': 1.0 if sentiment_label == 'neutral' else 0.2,
                'keyword_positive_count': positive_count,
                'keyword_negative_count': negative_count
            }
            sentiment_results.append(result)
        
        sentiment_df = pd.DataFrame(sentiment_results)
        return pd.concat([df, sentiment_df], axis=1)
    
    def _add_sentiment_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add aggregated sentiment metrics and derived features."""
        if df.empty:
            return df
        
        # Engagement score based on tweet metrics
        if all(col in df.columns for col in ['like_count', 'retweet_count', 'reply_count']):
            df['engagement_score'] = (
                df['like_count'] + 
                df['retweet_count'] * 2 + 
                df['reply_count'] * 3
            ) / 6  # Normalize
        
        # Viral potential (high engagement + positive sentiment)
        if 'engagement_score' in df.columns and 'sentiment_score' in df.columns:
            df['viral_potential'] = (
                df['engagement_score'] * df['sentiment_score']
            ).fillna(0)
        
        # Controversy score (high engagement + negative sentiment)
        if 'engagement_score' in df.columns and 'negative_score' in df.columns:
            df['controversy_score'] = (
                df['engagement_score'] * df['negative_score']
            ).fillna(0)
        
        # Content length analysis
        if 'content' in df.columns:
            df['content_length'] = df['content'].str.len()
            df['word_count'] = df['content'].str.split().str.len()
        
        # Time-based features
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['day_of_week'] = df['date'].dt.day_name()
        df['hour'] = df['date'].dt.hour
        
        return df
    
    def get_sentiment_summary(self, player_name: str, date_range: tuple) -> Dict[str, Any]:
        """
        Get sentiment summary for a specific player and date range.
        
        Args:
            player_name: Player name to analyze
            date_range: Tuple of (start_date, end_date)
            
        Returns:
            Dictionary with sentiment summary statistics
        """
        sentiment_df = self.fetch_data([player_name], date_range)
        
        if sentiment_df.empty:
            return {
                'player': player_name,
                'date_range': date_range,
                'total_mentions': 0,
                'sentiment_breakdown': {},
                'engagement_summary': {},
                'error': 'No data found'
            }
        
        summary = {
            'player': player_name,
            'date_range': date_range,
            'total_mentions': len(sentiment_df),
            'sentiment_breakdown': {
                'positive': len(sentiment_df[sentiment_df['sentiment_label'] == 'positive']),
                'negative': len(sentiment_df[sentiment_df['sentiment_label'] == 'negative']),
                'neutral': len(sentiment_df[sentiment_df['sentiment_label'] == 'neutral'])
            },
            'average_sentiment_score': sentiment_df['sentiment_score'].mean(),
            'engagement_summary': {
                'total_likes': sentiment_df['like_count'].sum(),
                'total_retweets': sentiment_df['retweet_count'].sum(),
                'total_replies': sentiment_df['reply_count'].sum(),
                'avg_engagement_score': sentiment_df.get('engagement_score', pd.Series([0])).mean()
            },
            'content_analysis': {
                'avg_content_length': sentiment_df.get('content_length', pd.Series([0])).mean(),
                'avg_word_count': sentiment_df.get('word_count', pd.Series([0])).mean()
            }
        }
        
        # Add top positive and negative keywords if available
        if 'keyword_positive_count' in sentiment_df.columns:
            summary['positive_keyword_mentions'] = sentiment_df['keyword_positive_count'].sum()
        if 'keyword_negative_count' in sentiment_df.columns:
            summary['negative_keyword_mentions'] = sentiment_df['keyword_negative_count'].sum()
        
        return summary
    
    def validate_data(self, df: pd.DataFrame) -> bool:
        """
        Validate sentiment data quality and ethical compliance.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Boolean indicating validation success
        """
        if df.empty:
            return False
            
        required_columns = ['tweet_id', 'date', 'content', 'sentiment_label']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            logger.error(f"Missing required columns: {missing_columns}")
            return False
        
        # Check for duplicate tweets
        duplicate_tweets = df.duplicated(subset=['tweet_id'])
        if duplicate_tweets.any():
            logger.warning(f"Found {duplicate_tweets.sum()} duplicate tweets")
        
        # Validate sentiment scores
        if 'sentiment_score' in df.columns:
            invalid_scores = df[
                (df['sentiment_score'] < 0) | (df['sentiment_score'] > 1)
            ]
            if not invalid_scores.empty:
                logger.warning(f"Invalid sentiment scores: {len(invalid_scores)} records")
        
        # Check date validity
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        future_dates = df[df['date'] > datetime.now()]
        if not future_dates.empty:
            logger.warning(f"Found {len(future_dates)} records with future dates")
        
        # Ensure no private or sensitive content was accidentally captured
        sensitive_patterns = ['private', 'confidential', 'personal']
        for pattern in sensitive_patterns:
            sensitive_content = df[df['content'].str.lower().str.contains(pattern, na=False)]
            if not sensitive_content.empty:
                logger.error(f"Potentially sensitive content detected: {pattern}")
                return False
        
        return True