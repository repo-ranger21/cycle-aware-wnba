#!/usr/bin/env python3
"""
Example usage of the Cycle-Aware WNBA Intelligence Feeds

This script demonstrates how to use the intelligence feeds module
to collect data from multiple sources for cycle-aware analysis.

Before running this script:
1. Set up your API keys as environment variables
2. Install required dependencies: pip install -r requirements.txt
3. Review the ethical guidelines and ensure proper consent procedures

Note: This example uses mock/demo mode to avoid requiring actual API keys.
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent / 'cycle-aware-wnba'))

# Import our intelligence feeds
try:
    from intelligence_feeds import (
        ClueDataSource,
        WearableDataSource, 
        WNBADataSource,
        WeatherDataSource,
        SentimentDataSource
    )
    print("✅ Intelligence feeds module imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please install requirements: pip install -r requirements.txt")
    sys.exit(1)


def main():
    """Main demonstration function."""
    print("🩸 Cycle-Aware WNBA Intelligence Platform - Demo")
    print("=" * 60)
    
    # Define analysis parameters
    players = ['breanna_stewart_demo', 'aja_wilson_demo', 'diana_taurasi_demo']
    date_range = (
        datetime.now() - timedelta(days=30),
        datetime.now() - timedelta(days=1)  # Exclude today for historical data
    )
    
    print(f"📅 Date Range: {date_range[0].strftime('%Y-%m-%d')} to {date_range[1].strftime('%Y-%m-%d')}")
    print(f"👥 Players: {', '.join(players)}")
    print()
    
    # Initialize data sources (demo mode - no real API calls)
    data_sources = {}
    
    print("🔧 Initializing Data Sources:")
    print("-" * 30)
    
    # Clue cycle data via Terra API
    try:
        if os.getenv('TERRA_API_KEY'):
            clue_source = ClueDataSource(api_key=os.getenv('TERRA_API_KEY'))
        else:
            clue_source = ClueDataSource(api_key='demo_key_for_testing')
        data_sources['cycle'] = clue_source
        print("✅ Clue Terra API - Ready")
    except Exception as e:
        print(f"⚠️  Clue Terra API - Demo mode (no API key): {e}")
    
    # WNBA performance data
    try:
        if os.getenv('SPORTSDATA_API_KEY'):
            wnba_source = WNBADataSource(api_key=os.getenv('SPORTSDATA_API_KEY'))
        else:
            wnba_source = WNBADataSource(api_key='demo_key_for_testing')
        data_sources['performance'] = wnba_source
        print("✅ WNBA SportsData.io - Ready")
    except Exception as e:
        print(f"⚠️  WNBA SportsData.io - Demo mode (no API key): {e}")
    
    # Weather data
    try:
        if os.getenv('OPENWEATHER_API_KEY'):
            weather_source = WeatherDataSource(api_key=os.getenv('OPENWEATHER_API_KEY'))
        else:
            weather_source = WeatherDataSource(api_key='demo_key_for_testing')
        data_sources['weather'] = weather_source
        print("✅ OpenWeatherMap - Ready")
    except Exception as e:
        print(f"⚠️  OpenWeatherMap - Demo mode (no API key): {e}")
    
    # Sentiment analysis
    try:
        twitter_config = {'bearer_token': os.getenv('TWITTER_BEARER_TOKEN', 'demo_token')}
        sentiment_source = SentimentDataSource(twitter_config=twitter_config)
        data_sources['sentiment'] = sentiment_source
        print("✅ Twitter Sentiment - Ready")
    except Exception as e:
        print(f"⚠️  Twitter Sentiment - Demo mode (no API key): {e}")
    
    # Wearable devices (requires OAuth setup)
    try:
        oauth_config = {
            'fitbit_client_id': os.getenv('FITBIT_CLIENT_ID', 'demo_client'),
            'fitbit_client_secret': os.getenv('FITBIT_CLIENT_SECRET', 'demo_secret'),
            'fitbit_token_url': 'https://api.fitbit.com/oauth2/token',
            'redirect_uri': 'http://localhost:8000/callback'
        }
        wearable_source = WearableDataSource(oauth_config=oauth_config)
        data_sources['wearables'] = wearable_source
        print("✅ Wearable Devices - Ready (OAuth required for actual data)")
    except Exception as e:
        print(f"⚠️  Wearable Devices - Demo mode: {e}")
    
    print()
    
    # Demonstrate data source capabilities
    print("📊 Data Source Capabilities:")
    print("-" * 30)
    
    for source_name, source in data_sources.items():
        print(f"\n🔍 {source.name}:")
        print(f"   Privacy Level: {source.ethical_compliance.get('privacy_level', 'Not specified')}")
        print(f"   Data Retention: {source.ethical_compliance.get('data_retention', 'Not specified')}")
        print(f"   Consent Required: {source.ethical_compliance.get('consent_verified', False)}")
        
        # Show what types of data each source provides
        if source_name == 'cycle':
            print("   Data Types: Flow patterns, ovulation predictions, symptom tracking")
        elif source_name == 'performance':
            print("   Data Types: Game statistics, player metrics, injury reports")
        elif source_name == 'weather':
            print("   Data Types: Temperature, humidity, air quality, seasonal patterns")
        elif source_name == 'sentiment':
            print("   Data Types: Social mentions, reactions, sentiment scores")
        elif source_name == 'wearables':
            print("   Data Types: Heart rate, sleep quality, activity levels, temperature")
    
    print("\n" + "=" * 60)
    print("🛡️  ETHICAL FRAMEWORK REMINDER")
    print("=" * 60)
    print("✅ All data sources follow privacy-first principles")
    print("✅ Athlete consent is required for all personal data")
    print("✅ Data is anonymized and has limited retention periods")
    print("✅ Results are for research and awareness, not medical decisions")
    print("✅ Transparent methodology and bias documentation")
    
    print("\n🚀 To collect real data:")
    print("1. Obtain proper API keys from each service")
    print("2. Set up environment variables for credentials")
    print("3. Ensure athlete consent and ethical approval")
    print("4. Use the fetch_data() method on each source")
    print("5. Apply your analysis with the collected data")
    
    print("\n📚 For more information:")
    print("- Read README.md for detailed setup instructions")
    print("- Review data_sources.json for API specifications")
    print("- Check ETHICS.md for ethical guidelines")
    print("- See example integrations in the documentation")
    
    return data_sources


if __name__ == "__main__":
    try:
        sources = main()
        print(f"\n✨ Demo completed successfully with {len(sources)} data sources initialized!")
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()