import json
from collections import Counter

def predict_cycle_phase(player):
    # Extract features
    day = player.get("cycle_day", 1)
    hrv = player.get("HRV", 50)
    bbt = player.get("BBT", 36.5)
    mood = player.get("mood_score", 2)
    sleep = player.get("sleep_quality", 0.7)
    pain = player.get("pain_score", 1)

    # Heuristics for demo purposes
    if 1 <= day <= 5 or pain >= 2 or bbt < 36.5:
        return "Menstruation"
    elif 6 <= day <= 13 and hrv > 60 and mood > 1:
        return "Follicular"
    elif 14 <= day <= 16 and bbt > 36.7 and hrv > 55:
        return "Ovulation"
    else:
        return "Luteal"

def satirical_overlay(phase):
    overlays = {
        "Menstruation": "CrampCast™ Watch",
        "Follicular": "MoodSwingMeter™ Alert",
        "Ovulation": "Egg-citement Index",
        "Luteal": "SnackSurge™ Incoming"
    }
    return overlays.get(phase, "Cycle Mysteries™ Detected")

def main():
    with open("wnba_rosters.json", "r") as f:
        players = json.load(f)

    phase_counts = Counter()
    player_results = []

    for player in players:
        phase = predict_cycle_phase(player)
        phase_counts[phase] += 1
        overlay = satirical_overlay(phase)
        player_results.append({
            "name": player.get("name", "Unknown"),
            "team": player.get("team", "Unknown"),
            "phase": phase,
            "overlay": overlay
        })

    # Print summary table
    print("\nMenstrual Cycle Phase Summary")
    print("-" * 34)
    for phase in ["Menstruation", "Follicular", "Ovulation", "Luteal"]:
        print(f"{phase:15}: {phase_counts.get(phase, 0):3}")

    print("\nIndividual Player Predictions")
    print("-" * 34)
    for result in player_results:
        print(f"{result['name']} ({result['team']}): {result['phase']} | {result['overlay']}")

    print("\nCivic Disclaimer:")
    print("This prediction is for public-good modeling only. No biometric data was exploited.")

if __name__ == "__main__":
    main()