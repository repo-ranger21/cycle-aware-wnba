import os
import json
from datetime import datetime
from supabase import create_client
from nba_api.stats.endpoints import commonallplayers

# ── Supabase setup ─────────────────────────────────────────────────────────────
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ── Fallback loader ────────────────────────────────────────────────────────────
def load_fallback_rosters(path="fallbacks/wnba_rosters_fallback.json"):
    try:
        with open(path, "r") as f:
            print("⚠️ Using fallback roster data.")
            return json.load(f)
    except Exception as e:
        print(f"❌ Failed to load fallback file: {e}")
        return []

# ── WNBA API fetch ─────────────────────────────────────────────────────────────
def fetch_all_players(season: str = "2025"):
    try:
        resp = commonallplayers.CommonAllPlayers(season="2025", league_id="10").get_dict()
        cols = resp["resultSets"][0]["headers"]
        rows = resp["resultSets"][0]["rowSet"]
        return [dict(zip(cols, row)) for row in rows]
    except Exception as e:
        print(f"❌ WNBA API fetch failed: {e}")
        return []

# ── Supabase upsert ────────────────────────────────────────────────────────────
def upsert_rosters(players: list[dict]):
    for p in players:
        record = {
            "player_id":       str(p["PLAYER_ID"]),
            "player_name":     p["PLAYER_NAME"],
            "team_id":         p["TEAM_ID"],
            "team_name":       p["TEAM_ABBREVIATION"],
            "position":        p["POSITION"],
            "jersey_number":   p.get("JERSEY_NUM"),
            "created_at":      datetime.utcnow().isoformat()
        }
        supabase.table("wnba_rosters").upsert(record).execute()
        print(f"✅ Upserted: {record['player_name']} ({record['team_name']})")

# ── Main ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    players = fetch_all_players()
    if not players:
        players = load_fallback_rosters()
    print(f"📦 Seeding {len(players)} players to Supabase...")
    upsert_rosters(players)
    print("🏁 Done.")
