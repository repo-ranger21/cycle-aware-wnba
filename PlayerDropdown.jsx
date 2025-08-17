import React, { useEffect, useState } from 'react';

// Civic disclaimer and contributor notes
const CIVIC_DISCLAIMER = "Roster reflects public sources and may not capture hardship contracts or cycle-related absences.";
const CONTRIBUTOR_NOTES = "Verify roster changes via WNBA.com before modeling predictions.";

function formatPlayerOption(player) {
  // Format: "A'ja Wilson – Las Vegas Aces (F)"
  let label = `${player.first_name} ${player.last_name} – ${player.team} (${player.position})`;
  if (player.expansion_team) {
    label += " 🆕"; // Badge for expansion team
  }
  return label;
}

function sortPlayers(players) {
  // Sort by last name, then team
  return [...players].sort((a, b) => {
    const lastA = a.last_name.toLowerCase();
    const lastB = b.last_name.toLowerCase();
    if (lastA < lastB) return -1;
    if (lastA > lastB) return 1;
    // If last names are equal, sort by team
    return a.team.localeCompare(b.team);
  });
}

const PlayerDropdown = () => {
  const [players, setPlayers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/wnba_rosters.json')
      .then(res => res.json())
      .then(data => {
        const filtered = data.filter(player =>
          player.roster_status === 'active' &&
          !['waived', 'suspended', 'unsigned'].includes(player.roster_status)
        );
        setPlayers(sortPlayers(filtered));
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  return (
    <div aria-label="WNBA Player Selection">
      <label htmlFor="wnba-player-dropdown">Select a Player:</label>
      <select id="wnba-player-dropdown" name="wnba-player-dropdown" aria-describedby="roster-disclaimer contributor-notes">
        {loading ? (
          <option disabled>Loading...</option>
        ) : (
          players.map(player => (
            <option
              key={player.id}
              value={player.id}
              title={player.expansion_team ? "Expansion team player" : ""}
              aria-label={formatPlayerOption(player)}
            >
              {formatPlayerOption(player)}
            </option>
          ))
        )}
      </select>
      <div id="roster-disclaimer" style={{ marginTop: '1em', fontStyle: 'italic', fontSize: 'small' }}>
        {CIVIC_DISCLAIMER}
      </div>
      <div id="contributor-notes" style={{ marginTop: '0.5em', fontStyle: 'italic', fontSize: 'small', color: '#555' }}>
        {CONTRIBUTOR_NOTES}
      </div>
    </div>
  );
};

export default PlayerDropdown;