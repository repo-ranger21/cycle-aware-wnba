"""
WNBA Performance Data Ingestion from SportsData.io

This module provides integration with SportsData.io API for comprehensive
WNBA performance statistics and game data for cycle-aware analysis.

Privacy Notice: Only publicly available performance statistics are used.
No personal or medical information is accessed.
"""

import pandas as pd
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from .base import DataSourceBase

logger = logging.getLogger(__name__)


class WNBADataSource(DataSourceBase):
    """
    WNBA performance data ingestion from SportsData.io API.
    
    Fetches publicly available game and performance data including:
    - Game schedules and results
    - Player statistics (points, rebounds, assists, etc.)
    - Team performance metrics
    - Game context (home/away, opponent strength)
    - Injury reports (when available)
    """
    
    def __init__(self, api_key: str, api_endpoint: str = "https://api.sportsdata.io/v3/wnba"):
        """
        Initialize WNBA data source with SportsData.io credentials.
        
        Args:
            api_key: SportsData.io API key
            api_endpoint: Base URL for SportsData.io WNBA API
        """
        ethical_compliance = {
            'consent_verified': True,  # Public performance data
            'privacy_level': 'public',
            'data_retention': '365_days',
            'medical_grade': False,
            'audit_trail': True,
            'data_type': 'performance_statistics'
        }
        
        super().__init__("WNBA SportsData.io", ethical_compliance)
        
        self.api_key = api_key
        self.api_endpoint = api_endpoint
        self.headers = {'Ocp-Apim-Subscription-Key': api_key}
        
        # Cache for team and player lookups
        self.teams_cache = {}
        self.players_cache = {}
    
    def fetch_data(self, player_ids: List[str], date_range: tuple, **kwargs) -> pd.DataFrame:
        """
        Fetch WNBA performance data for specified players and date range.
        
        Args:
            player_ids: List of WNBA player IDs or names
            date_range: Tuple of (start_date, end_date)
            **kwargs: Additional parameters like data_types, season
            
        Returns:
            DataFrame with WNBA performance data
        """
        self.log_access("fetch_wnba_data", len(player_ids), date_range)
        
        start_date, end_date = date_range
        season = kwargs.get('season', str(start_date.year))
        data_types = kwargs.get('data_types', ['games', 'stats', 'injuries'])
        
        all_data = []
        
        # Ensure we have current team and player data
        self._refresh_lookup_data(season)
        
        for player_id in player_ids:
            try:
                # Convert player name to ID if needed
                resolved_player_id = self._resolve_player_id(player_id)
                if not resolved_player_id:
                    logger.warning(f"Could not resolve player: {player_id}")
                    continue
                
                player_data = []
                
                # Fetch different data types
                if 'games' in data_types:
                    games_data = self._fetch_player_games(
                        resolved_player_id, start_date, end_date, season
                    )
                    player_data.extend(games_data)
                
                if 'stats' in data_types:
                    stats_data = self._fetch_player_stats(
                        resolved_player_id, start_date, end_date, season
                    )
                    player_data.extend(stats_data)
                
                if 'injuries' in data_types:
                    injury_data = self._fetch_injury_data(
                        resolved_player_id, start_date, end_date, season
                    )
                    player_data.extend(injury_data)
                
                if player_data:
                    player_df = pd.DataFrame(player_data)
                    player_df['original_player_id'] = player_id
                    player_df['resolved_player_id'] = resolved_player_id
                    all_data.append(player_df)
                    
            except Exception as e:
                logger.error(f"Error fetching WNBA data for {player_id}: {str(e)}")
                continue
        
        if not all_data:
            return pd.DataFrame()
            
        combined_df = pd.concat(all_data, ignore_index=True)
        return self.anonymize_data(combined_df)
    
    def _refresh_lookup_data(self, season: str):
        """Refresh cached team and player lookup data."""
        try:
            # Fetch teams
            teams_endpoint = f"{self.api_endpoint}/scores/json/teams"
            teams_response = requests.get(teams_endpoint, headers=self.headers)
            teams_response.raise_for_status()
            
            teams_data = teams_response.json()
            self.teams_cache = {team['Key']: team for team in teams_data}
            
            # Fetch players for the season
            players_endpoint = f"{self.api_endpoint}/scores/json/Players/{season}"
            players_response = requests.get(players_endpoint, headers=self.headers)
            players_response.raise_for_status()
            
            players_data = players_response.json()
            self.players_cache = {
                player['PlayerID']: player for player in players_data
            }
            
            # Also create name-to-ID mapping
            self.player_name_map = {
                f"{player['FirstName']} {player['LastName']}".lower(): player['PlayerID']
                for player in players_data
            }
            
        except Exception as e:
            logger.error(f"Error refreshing lookup data: {str(e)}")
    
    def _resolve_player_id(self, player_identifier: str) -> Optional[int]:
        """Resolve player name or ID to numeric player ID."""
        # If it's already a numeric ID, use it
        try:
            player_id = int(player_identifier)
            if player_id in self.players_cache:
                return player_id
        except ValueError:
            pass
        
        # Try to find by name
        normalized_name = player_identifier.lower().strip()
        if normalized_name in self.player_name_map:
            return self.player_name_map[normalized_name]
        
        # Fuzzy matching for partial names
        for name, player_id in self.player_name_map.items():
            if normalized_name in name or name in normalized_name:
                return player_id
        
        return None
    
    def _fetch_player_games(self, player_id: int, start_date: datetime,
                           end_date: datetime, season: str) -> List[Dict]:
        """Fetch game logs for a specific player."""
        endpoint = f"{self.api_endpoint}/stats/json/PlayerGameStatsBySeason/{season}"
        
        try:
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            all_games = response.json()
            
            # Filter for this player and date range
            player_games = [
                game for game in all_games 
                if game['PlayerID'] == player_id
            ]
            
            records = []
            for game in player_games:
                game_date = datetime.strptime(game['Day'], '%Y-%m-%dT%H:%M:%S')
                
                if start_date <= game_date <= end_date:
                    record = {
                        'player_id': str(player_id),
                        'date': game_date.strftime('%Y-%m-%d'),
                        'data_type': 'game_performance',
                        'game_id': game.get('GameID'),
                        'opponent_team': game.get('Opponent'),
                        'home_away': 'home' if game.get('HomeOrAway') == 'HOME' else 'away',
                        'minutes_played': game.get('Minutes', 0),
                        'points': game.get('Points', 0),
                        'rebounds': game.get('Rebounds', 0),
                        'assists': game.get('Assists', 0),
                        'steals': game.get('Steals', 0),
                        'blocks': game.get('BlockedShots', 0),
                        'turnovers': game.get('Turnovers', 0),
                        'field_goal_percentage': game.get('FieldGoalPercentage', 0),
                        'three_point_percentage': game.get('ThreePointPercentage', 0),
                        'free_throw_percentage': game.get('FreeThrowPercentage', 0),
                        'plus_minus': game.get('PlusMinus', 0),
                        'team_won': game.get('IsGameOver') and game.get('FantasyPoints', 0) > 0
                    }
                    records.append(record)
            
            return records
            
        except Exception as e:
            logger.error(f"Error fetching games for player {player_id}: {str(e)}")
            return []
    
    def _fetch_player_stats(self, player_id: int, start_date: datetime,
                           end_date: datetime, season: str) -> List[Dict]:
        """Fetch aggregate statistics for a player."""
        endpoint = f"{self.api_endpoint}/stats/json/PlayerSeasonStats/{season}"
        
        try:
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            all_stats = response.json()
            
            # Find this player's season stats
            player_stats = next(
                (stats for stats in all_stats if stats['PlayerID'] == player_id),
                None
            )
            
            if not player_stats:
                return []
            
            # Create aggregated record for the season
            record = {
                'player_id': str(player_id),
                'date': start_date.strftime('%Y-%m-%d'),  # Use start date for season stats
                'data_type': 'season_statistics',
                'games_played': player_stats.get('Games', 0),
                'games_started': player_stats.get('Started', 0),
                'avg_minutes': player_stats.get('Minutes', 0),
                'avg_points': player_stats.get('Points', 0),
                'avg_rebounds': player_stats.get('Rebounds', 0),
                'avg_assists': player_stats.get('Assists', 0),
                'avg_steals': player_stats.get('Steals', 0),
                'avg_blocks': player_stats.get('BlockedShots', 0),
                'avg_turnovers': player_stats.get('Turnovers', 0),
                'field_goal_percentage': player_stats.get('FieldGoalPercentage', 0),
                'three_point_percentage': player_stats.get('ThreePointPercentage', 0),
                'free_throw_percentage': player_stats.get('FreeThrowPercentage', 0),
                'player_efficiency_rating': player_stats.get('PlayerEfficiencyRating', 0)
            }
            
            return [record]
            
        except Exception as e:
            logger.error(f"Error fetching stats for player {player_id}: {str(e)}")
            return []
    
    def _fetch_injury_data(self, player_id: int, start_date: datetime,
                          end_date: datetime, season: str) -> List[Dict]:
        """Fetch injury report data for a player."""
        endpoint = f"{self.api_endpoint}/scores/json/Injuries/{season}"
        
        try:
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            all_injuries = response.json()
            
            # Filter for this player
            player_injuries = [
                injury for injury in all_injuries 
                if injury.get('PlayerID') == player_id
            ]
            
            records = []
            for injury in player_injuries:
                injury_date_str = injury.get('Updated')
                if injury_date_str:
                    try:
                        injury_date = datetime.strptime(
                            injury_date_str.split('T')[0], '%Y-%m-%d'
                        )
                        
                        if start_date <= injury_date <= end_date:
                            record = {
                                'player_id': str(player_id),
                                'date': injury_date.strftime('%Y-%m-%d'),
                                'data_type': 'injury_report',
                                'injury_status': injury.get('Status'),
                                'injury_body_part': injury.get('BodyPart'),
                                'injury_details': injury.get('InjuryDetail'),
                                'expected_return': injury.get('ExpectedReturn'),
                                'games_missed': 0  # Would need additional logic to calculate
                            }
                            records.append(record)
                    except ValueError:
                        continue
            
            return records
            
        except Exception as e:
            logger.error(f"Error fetching injuries for player {player_id}: {str(e)}")
            return []
    
    def get_team_schedule(self, season: str, team_key: str = None) -> pd.DataFrame:
        """
        Get schedule data for analysis context.
        
        Args:
            season: Season year
            team_key: Optional team key to filter
            
        Returns:
            DataFrame with schedule information
        """
        endpoint = f"{self.api_endpoint}/scores/json/Games/{season}"
        
        try:
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            games = response.json()
            
            if team_key:
                games = [
                    game for game in games 
                    if game.get('HomeTeam') == team_key or game.get('AwayTeam') == team_key
                ]
            
            schedule_records = []
            for game in games:
                record = {
                    'game_id': game.get('GameID'),
                    'date': game.get('Day', '').split('T')[0],
                    'home_team': game.get('HomeTeam'),
                    'away_team': game.get('AwayTeam'),
                    'season_type': game.get('SeasonType'),
                    'week': game.get('Week'),
                    'status': game.get('Status')
                }
                schedule_records.append(record)
            
            return pd.DataFrame(schedule_records)
            
        except Exception as e:
            logger.error(f"Error fetching schedule: {str(e)}")
            return pd.DataFrame()
    
    def validate_data(self, df: pd.DataFrame) -> bool:
        """
        Validate WNBA data quality and consistency.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Boolean indicating validation success
        """
        if df.empty:
            return False
            
        required_columns = ['player_id', 'date', 'data_type']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            logger.error(f"Missing required columns: {missing_columns}")
            return False
        
        # Validate performance statistics ranges
        if 'points' in df.columns:
            invalid_points = df[(df['points'] < 0) | (df['points'] > 100)]
            if not invalid_points.empty:
                logger.warning(f"Potentially invalid point values: {len(invalid_points)} records")
        
        if 'minutes_played' in df.columns:
            invalid_minutes = df[(df['minutes_played'] < 0) | (df['minutes_played'] > 50)]
            if not invalid_minutes.empty:
                logger.warning(f"Potentially invalid minutes: {len(invalid_minutes)} records")
        
        # Check date validity
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        future_dates = df[df['date'] > datetime.now()]
        if not future_dates.empty:
            logger.warning(f"Found {len(future_dates)} records with future dates")
        
        return True