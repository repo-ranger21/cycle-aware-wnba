import React, { useState } from "react";

// --- Placeholder functions for synthetic civic-grade data ---
function getSyntheticCyclePhase(playerName, gameDateTime) {
  // Mock: Returns a random phase for demonstration
  const phases = [
    "Synthetic Menstrual",
    "Synthetic Follicular",
    "Synthetic Ovulatory",
    "Synthetic Luteal",
  ];
  return phases[
    Math.floor(
      (playerName.length + new Date(gameDateTime).getDate()) % phases.length
    )
  ];
}

function getVolatilityIndex(playerName, matchup) {
  // Mock: Returns a pseudo-random volatility index
  return Number(
    (
      0.5 +
      (playerName.length * matchup.length) % 100 / 200
    ).toFixed(2)
  );
}

function getFatigueScore(playerName, gameDateTime) {
  // Mock: Returns a pseudo-random fatigue score
  return (
    60 +
    ((playerName.charCodeAt(0) + new Date(gameDateTime).getHours()) % 40)
  );
}

function getSHAPBreakdown(playerName, matchup) {
  // Mock: Returns a pseudo-random deviation
  return {
    deviation: Number(
      (((playerName.length + matchup.length) % 10) - 5).toFixed(1)
    ),
  };
}

// --- Civic logic for adjusted points and recommendation ---
function calculateAdjustedPoints(pointLine, volatility, fatigue, shapDeviation) {
  // Example civic-grade adjustment (mock logic)
  // Volatility reduces by up to 2 points, fatigue by up to 1.5, SHAP deviation added directly
  return (
    pointLine -
    volatility * 2 +
    (100 - fatigue) * 0.015 +
    shapDeviation
  );
}

function getRecommendation(adjustedPoints, pointLine) {
  return adjustedPoints > pointLine ? "Over" : "Under";
}

// --- Main Component ---
const CivicPredictorCard = ({
  playerName,
  matchup,
  pointLine,
  gameDateTime,
}) => {
  const [prediction, setPrediction] = useState(null);

  const handlePredict = () => {
    // Retrieve synthetic civic metrics
    const cyclePhase = getSyntheticCyclePhase(playerName, gameDateTime);
    const volatility = getVolatilityIndex(playerName, matchup);
    const fatigue = getFatigueScore(playerName, gameDateTime);
    const { deviation: shapDeviation } = getSHAPBreakdown(playerName, matchup);

    // Calculate adjusted points
    const adjustedPoints = calculateAdjustedPoints(
      pointLine,
      volatility,
      fatigue,
      shapDeviation
    );

    // Get recommendation
    const recommendation = getRecommendation(adjustedPoints, pointLine);

    setPrediction({
      cyclePhase,
      volatility,
      fatigue,
      shapDeviation,
      adjustedPoints: adjustedPoints.toFixed(2),
      recommendation,
    });
  };

  return (
    <div style={styles.card}>
      <h2 style={styles.header}>Civic Predictor Card</h2>
      <div style={styles.meta}>
        <div>
          <strong>Player:</strong> {playerName}
        </div>
        <div>
          <strong>Matchup:</strong> {matchup}
        </div>
        <div>
          <strong>Point Line:</strong> {pointLine}
        </div>
        <div>
          <strong>Game Time:</strong> {gameDateTime}
        </div>
      </div>
      <button style={styles.button} onClick={handlePredict}>
        Predict Civic Over/Under
      </button>
      {prediction && (
        <div style={styles.result}>
          <div>
            <strong>Cycle Phase:</strong> {prediction.cyclePhase}
          </div>
          <div>
            <strong>Volatility Index:</strong> {prediction.volatility}
          </div>
          <div>
            <strong>Fatigue Score:</strong> {prediction.fatigue}
          </div>
          <div>
            <strong>SHAP Deviation:</strong> {prediction.shapDeviation}
          </div>
          <div>
            <strong>Adjusted Points:</strong> {prediction.adjustedPoints}
          </div>
          <div>
            <strong>Recommendation:</strong> {prediction.recommendation}
          </div>
        </div>
      )}
      <div style={styles.disclaimer}>
        <em>
          These projections are for ethical modeling only. No biometric data used. No cramps exploited. Volatility flags are synthetic and satirical.
        </em>
      </div>
    </div>
  );
};

// --- Modular Civic Styling ---
const styles = {
  card: {
    border: "1px solid #aaa",
    borderRadius: "12px",
    padding: "1.5rem",
    maxWidth: "400px",
    background: "#f8f9fa",
    boxShadow: "0 2px 6px #e0e0e0",
    margin: "1rem auto",
    fontFamily: "system-ui, sans-serif",
  },
  header: {
    marginTop: 0,
    fontSize: "1.4rem",
    color: "#3b3b3b",
  },
  meta: {
    marginBottom: "1rem",
    fontSize: "1rem",
    color: "#222",
  },
  button: {
    background: "#2c7be5",
    color: "#fff",
    border: "none",
    padding: "0.5rem 1rem",
    borderRadius: "6px",
    fontWeight: 600,
    cursor: "pointer",
    marginBottom: "1rem",
  },
  result: {
    background: "#fff",
    border: "1px solid #dedede",
    borderRadius: "8px",
    padding: "1rem",
    marginBottom: "0.5rem",
    boxShadow: "0 1px 3px #d0d0d0",
  },
  disclaimer: {
    marginTop: "1rem",
    fontSize: "0.85rem",
    color: "#6c757d",
    borderTop: "1px dashed #ccc",
    paddingTop: "0.5rem",
  },
};

export default CivicPredictorCard;