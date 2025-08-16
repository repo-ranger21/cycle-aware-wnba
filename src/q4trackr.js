#!/usr/bin/env node

/**
 * 🩸 Q4Trackr: Cycle-Aware WNBA Predictions
 * "We don't just model performance. We audit the uterus."
 * 
 * Main application entry point for satirical WNBA cycle predictions
 * Built with ethical considerations and privacy-first principles
 */

const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const path = require('path');
require('dotenv').config();

// Import our satirical modules
const MoodMeeter = require('./modules/MoodMeeter');
const CrampCast = require('./modules/CrampCast');
const MoodSwingMeter = require('./modules/MoodSwingMeter');
const Ovulytics = require('./modules/Ovulytics');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, '../public')));

// Ethical disclaimer middleware
app.use((req, res, next) => {
  res.setHeader('X-Ethics-Notice', 'Satirical content only. No real medical data used.');
  res.setHeader('X-Privacy-Policy', 'Privacy-first. Consent required. Civic humor only.');
  next();
});

// Initialize our satirical modules
const moodMeeter = new MoodMeeter();
const crampCast = new CrampCast();
const moodSwingMeter = new MoodSwingMeter();
const ovulytics = new Ovulytics();

// Sample player for demonstration
const samplePlayer = "Skylar Diggins-Smith";
const gameDate = new Date().toISOString().split('T')[0];

// API Routes
app.get('/', (req, res) => {
  res.json({
    message: "🩸 Q4Trackr: Cycle-Aware WNBA Predictions",
    tagline: "We don't just model performance. We audit the uterus.",
    ethical_notice: "This is satirical content designed for civic humor and critical thinking, not real medical decisions.",
    modules: {
      "MoodMeeter™": "Measures player mood dynamics during games",
      "CrampCast™": "Predicts likelihood of physical cramps disrupting game performance",
      "MoodSwingMeter™": "Forecasts mood swings and their impact on gameplay", 
      "Ovulytics™": "Tracks ovulation phases for tongue-in-cheek game predictions"
    },
    sample_endpoint: `/prediction/${samplePlayer}`
  });
});

app.get('/prediction/:playerName', async (req, res) => {
  try {
    const playerName = req.params.playerName || samplePlayer;
    
    // Get predictions from each module
    const moodData = await moodMeeter.analyzeMood(playerName, gameDate);
    const crampData = await crampCast.predictCramps(playerName, gameDate);
    const moodSwingData = await moodSwingMeter.analyzeMoodSwings(playerName, gameDate);
    const ovulationData = await ovulytics.trackOvulation(playerName, gameDate);
    
    // Combine predictions into the expected JSON format
    const prediction = {
      player: playerName,
      mood_index: moodData.moodIndex,
      cramp_severity: crampData.severity,
      mood_swing: moodSwingData.level,
      ovulation_phase: ovulationData.phase,
      q4_prediction: generateQ4Prediction(moodData, crampData, moodSwingData, ovulationData),
      timestamp: new Date().toISOString(),
      ethical_disclaimer: "Satirical analysis using fabricated metrics. No real personal data collected."
    };
    
    res.json(prediction);
  } catch (error) {
    res.status(500).json({
      error: "Prediction analysis failed",
      message: error.message,
      ethical_notice: "This system uses satirical data only"
    });
  }
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    modules: ['MoodMeeter™', 'CrampCast™', 'MoodSwingMeter™', 'Ovulytics™'],
    ethical_compliance: 'active'
  });
});

// Generate Q4 prediction based on all module outputs
function generateQ4Prediction(moodData, crampData, moodSwingData, ovulationData) {
  const predictions = [
    "Clutch performance likely. Snacks advised.",
    "Expect stellar defense. Hydration recommended.",
    "Q4 dominance predicted. Emotional support snacks ready.",
    "Peak performance window. Refs beware of intensity.",
    "Balanced gameplay expected. Zen mode activated.",
    "Energy dip possible. Bench support advised.",
    "Mood volatility detected. Expect entertaining gameplay.",
    "Optimal performance phase. Watch for record-breaking plays."
  ];
  
  // Pseudo-random selection based on combined metrics (for satirical purposes)
  const combinedScore = moodData.moodIndex + crampData.severity + 
                       (moodSwingData.level === 'Turbulent' ? 3 : moodSwingData.level === 'Moderate' ? 2 : 1);
  const index = Math.floor(combinedScore) % predictions.length;
  
  return predictions[index];
}

// Start the server
app.listen(PORT, () => {
  console.log(`
🩸 Q4Trackr Server Running on port ${PORT}
   
   "We don't just model performance. We audit the uterus."
   
   Satirical WNBA cycle predictions now available at:
   http://localhost:${PORT}
   
   Sample prediction: http://localhost:${PORT}/prediction/${samplePlayer}
   
   🛡️  Ethical Notice: All data is satirical and fictional.
   🛡️  Privacy: No real athlete data is collected or used.
   🛡️  Purpose: Civic humor and critical thinking only.
  `);
});

module.exports = app;