// playerDropdown.js

// Civic disclaimer and contributor onboarding notes
const CIVIC_DISCLAIMER = "Roster reflects public sources and may not capture hardship contracts or cycle-related absences.";
const CONTRIBUTOR_NOTES = "Verify roster changes via WNBA.com before modeling predictions.";

// Format player as "A'ja Wilson – Las Vegas Aces (F)" + badge if expansion team
function formatPlayerOption(player) {
  let label = `${player.first_name} ${player.last_name} – ${player.team} (${player.position})`;
  if (player.expansion_team) label += " 🆕";
  return label;
}

// Sort by last name, then team
function sortPlayers(players) {
  return players.sort((a, b) => {
    let lastA = a.last_name?.toLowerCase() || '';
    let lastB = b.last_name?.toLowerCase() || '';
    if (lastA < lastB) return -1;
    if (lastA > lastB) return 1;
    return (a.team || '').localeCompare(b.team || '');
  });
}

// Main function to load and inject dropdown
function injectPlayerDropdown(jsonUrl, dropdownId = "wnba-player-dropdown") {
  fetch(jsonUrl)
    .then(response => response.json())
    .then(data => {
      // Filter active players only, exclude waived/suspended/unsigned
      const activePlayers = data.filter(player =>
        player.roster_status === 'active'
      );

      const sortedPlayers = sortPlayers(activePlayers);

      // Create dropdown and disclaimer elements
      const container = document.createElement("div");
      container.setAttribute("aria-label", "WNBA Player Selection");

      // Label
      const label = document.createElement("label");
      label.setAttribute("for", dropdownId);
      label.textContent = "Select a Player:";
      container.appendChild(label);

      // Dropdown
      const select = document.createElement("select");
      select.id = dropdownId;
      select.setAttribute("name", dropdownId);
      select.setAttribute("aria-describedby", "roster-disclaimer contributor-notes");

      sortedPlayers.forEach(player => {
        const option = document.createElement("option");
        option.value = player.id || formatPlayerOption(player);
        option.textContent = formatPlayerOption(player);
        if (player.expansion_team) {
          option.title = "Expansion team player";
        }
        option.setAttribute("aria-label", option.textContent);
        select.appendChild(option);
      });

      container.appendChild(select);

      // Civic disclaimer
      const disclaimer = document.createElement("div");
      disclaimer.id = "roster-disclaimer";
      disclaimer.style.marginTop = "1em";
      disclaimer.style.fontStyle = "italic";
      disclaimer.style.fontSize = "small";
      disclaimer.textContent = CIVIC_DISCLAIMER;
      container.appendChild(disclaimer);

      // Contributor notes
      const notes = document.createElement("div");
      notes.id = "contributor-notes";
      notes.style.marginTop = "0.5em";
      notes.style.fontStyle = "italic";
      notes.style.fontSize = "small";
      notes.style.color = "#555";
      notes.textContent = CONTRIBUTOR_NOTES;
      container.appendChild(notes);

      // Inject into document (replace if exists)
      const mount = document.getElementById(dropdownId + "-container") || document.body;
      mount.appendChild(container);
    })
    .catch(err => {
      console.error("Failed to load wnba_rosters.json:", err);
      // Show fallback message
      const fallback = document.createElement("div");
      fallback.textContent = "Unable to load WNBA player roster.";
      document.body.appendChild(fallback);
    });
}

// Usage example (in your HTML):
// <div id="wnba-player-dropdown-container"></div>
// <script src="playerDropdown.js"></script>
// <script>
//   injectPlayerDropdown('/wnba_rosters.json', 'wnba-player-dropdown');
// </script>
