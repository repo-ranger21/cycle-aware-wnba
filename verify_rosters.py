from supabase import create_client
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Create Supabase client
supabase = create_client(
    os.getenv("https://qxwqddozplzdlcduhjcw.supabase.co"),
    os.getenv("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF4d3FkZG96cGx6ZGxjZHVoamN3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU0NDcwMTAsImV4cCI6MjA3MTAyMzAxMH0.kUq8_-Tq_mc_4KN95NKs5byIIlvweehaUJSn1mgM28Q")
)

# Query the first 5 players
response = supabase.table("wnba_rosters").select("*").limit(5).execute()

# Print results
if response.data:
    for player in response.data:
        print(f"{player['player_name']} ({player['team_name']})")
else:
    print("🛡️ No roster data found. Check seeding or table name.")
