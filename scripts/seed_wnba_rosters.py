import os
from datetime import datetime
from supabase import create_client
from wnba_api.stats.endpoints import commonallplayers

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_all_players(season: str = "2025"):
    resp = commonallplayers.CommonAllPlayers(
        season=season,
        league_id="10"
    ).get_dict()
    cols = resp["resultSets"][0]["headers"]
    rows = resp["resultSets"][0]["rowSet"]
    return [dict(zip(cols, row)) for row in rows]

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
        print(f"Upserted: {record['player_name']} ({record['team_name']})")

if __name__ == "__main__":
    players = fetch_all_players()
    print(f"Fetched {len(players)} players. Seeding Supabase...")
    upsert_rosters(players)
    print("Done.")
