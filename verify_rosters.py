from supabase import create_client
from dotenv import load_dotenv
import os

# ── Load environment variables ────────────────────────────────────────────────
load_dotenv()

SUPABASE_URL = os.getenv("https://qxwqddozplzdlcduhjcw.supabase.co")
SUPABASE_KEY = os.getenv("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF4d3FkZG96cGx6ZGxjZHVoamN3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU0NDcwMTAsImV4cCI6MjA3MTAyMzAxMH0.kUq8_-Tq_mc_4KN95NKs5byIIlvweehaUJSn1mgM28Q")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Missing Supabase credentials. Check your .env file.")
    exit(1)

# ── Create Supabase client ────────────────────────────────────────────────────
supabase = create_client(https://qxwqddozplzdlcduhjcw.supabase.co, eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF4d3FkZG96cGx6ZGxjZHVoamN3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU0NDcwMTAsImV4cCI6MjA3MTAyMzAxMH0.kUq8_-Tq_mc_4KN95NKs5byIIlvweehaUJSn1mgM28Q)

# ── Emoji-coded team tags ─────────────────────────────────────────────────────
TEAM_EMOJIS = {
    "NYL": "🗽", "LVA": "🎰", "CHI": "🌆", "CON": "🌊", "ATL": "🍑",
    "DAL": "🐎", "IND": "🏁", "MIN": "🐺", "PHO": "🔥", "SEA": "🌧️",
    "WAS": "🏛️", "LA": "🎬"
}

# ── Query and display roster ──────────────────────────────────────────────────
response = supabase.table("wnba_rosters").select("*").limit(10).execute()
players = response.data

if not players:
    print("🛡️ No roster data found in Supabase. Run seed_wnba_rosters.py first.")
    exit(0)

print(f"✅ Found {len(players)} players. Displaying sample:\n")

for p in players:
    name = p.get("player_name", "❓")
    team = p.get("team_name", "UNK")
    emoji = TEAM_EMOJIS.get(team, "🏀")
    position = p.get("position", "—")
    jersey = p.get("jersey_number", "—")
    print(f"{emoji} {name} | {team} | #{jersey} | {position}")
