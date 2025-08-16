/**
 * ⚡ CrampCast™ - Satirical Cramp Prediction Module
 * 
 * Purpose: Predicts likelihood of physical cramps disrupting game performance
 * Inputs: Medical history, hydration levels, recent schedule
 * Outputs: Probability of cramps (0%-100%)
 * 
 * Satirical Overlay:
 * | Input Emoji | Meaning |
 * |-------------|---------|
 * | 💧          | Hydration levels |
 * | 🏃‍♀️        | Recent physical activity |
 */

class CrampCast {
  constructor() {
    this.moduleName = "CrampCast™";
    this.version = "1.0.0";
    this.ethicalNotice = "Satirical health analysis only. Not for medical use.";
    
    // Satirical cramp indicators with emoji overlays
    this.crampIndicators = {
      hydration: { emoji: "💧", weight: 0.3, tooltip: "Hydration levels monitored" },
      activity: { emoji: "🏃‍♀️", weight: 0.4, tooltip: "Recent physical activity impact" },
      stress: { emoji: "😰", weight: 0.2, tooltip: "Game stress factor" },
      recovery: { emoji: "🛋️", weight: 0.1, tooltip: "Recovery time analysis" }
    };

    // Satirical severity levels
    this.severityLevels = {
      1: { level: "Minimal", emoji: "✅", tooltip: "All systems green" },
      2: { level: "Low", emoji: "🟡", tooltip: "Minor discomfort possible" },
      3: { level: "Moderate", emoji: "🟠", tooltip: "Noticeable impact likely" },
      4: { level: "High", emoji: "🔴", tooltip: "Significant disruption risk" },
      5: { level: "Severe", emoji: "🚨", tooltip: "Bench protocol advised" }
    };
  }

  /**
   * Predict cramp likelihood based on satirical health metrics
   * @param {string} playerName - Name of the player
   * @param {string} gameDate - Date of the game
   * @returns {Object} Cramp prediction with satirical overlays
   */
  async predictCramps(playerName, gameDate) {
    try {
      // Satirical cramp calculation using mock health data
      const hydrationScore = this.assessSatiricalHydration();
      const activityImpact = this.calculateActivityImpact(gameDate);
      const stressLevel = this.assessGameStress(gameDate);
      const recoveryFactor = this.calculateRecoveryFactor();
      
      const crampProbability = this.calculateCrampProbability(
        hydrationScore, activityImpact, stressLevel, recoveryFactor
      );
      
      const severity = this.determineSeverityLevel(crampProbability);
      const prediction = this.generateCrampPrediction(severity);
      
      return {
        player: playerName,
        module: this.moduleName,
        probability: Number((crampProbability * 100).toFixed(1)),
        severity: severity,
        severityInfo: this.severityLevels[severity],
        prediction: prediction,
        factors: {
          hydration: hydrationScore,
          activity: activityImpact,
          stress: stressLevel,
          recovery: recoveryFactor
        },
        indicators: this.crampIndicators,
        timestamp: new Date().toISOString(),
        ethicalNotice: this.ethicalNotice
      };
    } catch (error) {
      throw new Error(`CrampCast™ prediction failed: ${error.message}`);
    }
  }

  /**
   * Assess satirical hydration levels
   */
  assessSatiricalHydration() {
    // Mock hydration assessment (0-1 scale, higher is better)
    const baseHydration = 0.6 + Math.random() * 0.4;
    
    // Add some satirical factors
    const coffeeIntake = Math.random() > 0.5 ? -0.1 : 0; // Too much coffee
    const socialMediaTime = Math.random() * 0.05; // Distraction from drinking water
    
    return Math.max(0, Math.min(1, baseHydration + coffeeIntake - socialMediaTime));
  }

  /**
   * Calculate activity impact on cramp likelihood
   */
  calculateActivityImpact(gameDate) {
    // Satirical recent activity assessment
    const daysThisWeek = new Date(gameDate).getDay();
    const weekdayFactor = daysThisWeek < 5 ? 0.8 : 1.2; // Weekends = more rest
    
    // Random "training intensity" factor
    const trainingIntensity = 0.5 + Math.random() * 0.5;
    
    return weekdayFactor * trainingIntensity;
  }

  /**
   * Assess game stress levels
   */
  assessGameStress(gameDate) {
    // Mock stress calculation based on game importance
    const isPlayoffs = Math.random() > 0.8; // Random playoff determination
    const rivalryGame = Math.random() > 0.7; // Random rivalry factor
    
    let stress = 0.5; // Base stress
    if (isPlayoffs) stress += 0.3;
    if (rivalryGame) stress += 0.2;
    
    return Math.min(1, stress);
  }

  /**
   * Calculate recovery factor
   */
  calculateRecoveryFactor() {
    // Satirical recovery time simulation
    const sleepQuality = 0.6 + Math.random() * 0.4;
    const restDays = Math.floor(Math.random() * 3); // 0-2 rest days
    
    return (sleepQuality + (restDays * 0.1)) / 1.2;
  }

  /**
   * Calculate overall cramp probability
   */
  calculateCrampProbability(hydration, activity, stress, recovery) {
    // Weighted combination of factors (inverted for some)
    const hydrationFactor = (1 - hydration) * this.crampIndicators.hydration.weight;
    const activityFactor = activity * this.crampIndicators.activity.weight;
    const stressFactor = stress * this.crampIndicators.stress.weight;
    const recoveryFactor = (1 - recovery) * this.crampIndicators.recovery.weight;
    
    return Math.min(1, hydrationFactor + activityFactor + stressFactor + recoveryFactor);
  }

  /**
   * Determine severity level (1-5) based on probability
   */
  determineSeverityLevel(probability) {
    if (probability <= 0.2) return 1;
    if (probability <= 0.4) return 2;
    if (probability <= 0.6) return 3;
    if (probability <= 0.8) return 4;
    return 5;
  }

  /**
   * Generate satirical cramp prediction text
   */
  generateCrampPrediction(severity) {
    const predictions = {
      1: "Smooth sailing ahead! Hydration game strong.",
      2: "Minor tension possible. Keep stretching protocol active.",
      3: "Moderate discomfort detected. Bench heating pad on standby.",
      4: "High risk zone! Emergency snack deployment recommended.", 
      5: "Code Red! Massage therapist and emotional support snacks required."
    };
    
    return predictions[severity];
  }

  /**
   * Get module info and capabilities
   */
  getModuleInfo() {
    return {
      name: this.moduleName,
      version: this.version,
      purpose: "Predicts likelihood of physical cramps disrupting game performance",
      inputs: ["Medical history", "Hydration levels", "Recent schedule"],
      outputs: ["Cramp probability (0-100%)", "Severity level (1-5)", "Satirical prediction"],
      ethicalNotice: this.ethicalNotice,
      satiricalOverlay: this.crampIndicators,
      severityLevels: this.severityLevels
    };
  }
}

module.exports = CrampCast;