/**
 * 🔄 MoodSwingMeter™ - Satirical Mood Swing Analysis Module
 * 
 * Purpose: Forecasts mood swings and their impact on gameplay
 * Inputs: Hormonal data, social triggers, sleep patterns
 * Outputs: Mood swing severity (Stable, Moderate, Turbulent)
 * 
 * Satirical Overlay:
 * | Output Emoji | Meaning |
 * |--------------|---------|
 * | 🌈           | Stable |
 * | 🌪️           | Turbulent |
 */

class MoodSwingMeter {
  constructor() {
    this.moduleName = "MoodSwingMeter™";
    this.version = "1.0.0";
    this.ethicalNotice = "Satirical mood analysis. No real hormonal data processed.";
    
    // Satirical mood swing levels with emoji overlays
    this.swingLevels = {
      stable: { 
        emoji: "🌈", 
        level: "Stable", 
        tooltip: "Steady emotional state. Optimal for consistent gameplay.",
        range: [0, 0.3]
      },
      moderate: { 
        emoji: "🌊", 
        level: "Moderate", 
        tooltip: "Some emotional fluctuation. Enhanced creativity possible.",
        range: [0.3, 0.7]
      },
      turbulent: { 
        emoji: "🌪️", 
        level: "Turbulent", 
        tooltip: "High emotional volatility. Expect unpredictable brilliance.",
        range: [0.7, 1.0]
      }
    };

    // Satirical influencing factors
    this.factors = {
      sleep: { weight: 0.3, emoji: "😴", tooltip: "Sleep quality impact" },
      social: { weight: 0.25, emoji: "📱", tooltip: "Social media exposure" },
      schedule: { weight: 0.2, emoji: "📅", tooltip: "Game schedule density" },
      nutrition: { weight: 0.15, emoji: "🥗", tooltip: "Nutritional balance" },
      weather: { weight: 0.1, emoji: "🌤️", tooltip: "Weather influence" }
    };
  }

  /**
   * Analyze mood swing patterns based on satirical metrics
   * @param {string} playerName - Name of the player
   * @param {string} gameDate - Date of the game
   * @returns {Object} Mood swing analysis with satirical overlays
   */
  async analyzeMoodSwings(playerName, gameDate) {
    try {
      // Calculate satirical mood swing factors
      const sleepImpact = this.assessSleepPatterns();
      const socialTriggers = this.analyzeSocialTriggers();
      const scheduleStress = this.calculateScheduleStress(gameDate);
      const nutritionBalance = this.assessNutritionalState();
      const weatherInfluence = this.calculateWeatherImpact(gameDate);
      
      // Calculate overall volatility score
      const volatilityScore = this.calculateVolatilityScore({
        sleep: sleepImpact,
        social: socialTriggers,
        schedule: scheduleStress,
        nutrition: nutritionBalance,
        weather: weatherInfluence
      });
      
      const swingLevel = this.determineSwingLevel(volatilityScore);
      const prediction = this.generateSwingPrediction(swingLevel, volatilityScore);
      
      return {
        player: playerName,
        module: this.moduleName,
        volatilityScore: Number(volatilityScore.toFixed(2)),
        level: swingLevel.level,
        emoji: swingLevel.emoji,
        tooltip: swingLevel.tooltip,
        prediction: prediction,
        factors: {
          sleep: sleepImpact,
          social: socialTriggers,
          schedule: scheduleStress,
          nutrition: nutritionBalance,
          weather: weatherInfluence
        },
        factorWeights: this.factors,
        timestamp: new Date().toISOString(),
        ethicalNotice: this.ethicalNotice
      };
    } catch (error) {
      throw new Error(`MoodSwingMeter™ analysis failed: ${error.message}`);
    }
  }

  /**
   * Assess satirical sleep pattern impact
   */
  assessSleepPatterns() {
    // Mock sleep quality assessment (0-1 scale, higher is better stability)
    const baseQuality = 0.5 + Math.random() * 0.5;
    
    // Satirical factors
    const socialMediaBefore = Math.random() > 0.6 ? -0.2 : 0; // Doom scrolling impact
    const caffeineIntake = Math.random() > 0.4 ? -0.1 : 0; // Late caffeine
    const gameAnxiety = Math.random() > 0.7 ? -0.15 : 0; // Pre-game nerves
    
    return Math.max(0, Math.min(1, baseQuality + socialMediaBefore + caffeineIntake + gameAnxiety));
  }

  /**
   * Analyze satirical social triggers
   */
  analyzeSocialTriggers() {
    // Mock social media sentiment impact
    const triggers = [
      { type: "fan_support", impact: -0.2 }, // Positive, reduces volatility
      { type: "criticism", impact: 0.4 }, // Increases volatility
      { type: "trade_rumors", impact: 0.5 }, // High volatility
      { type: "teammate_drama", impact: 0.3 }, // Moderate increase
      { type: "media_praise", impact: -0.1 }, // Slight stabilizing
      { type: "neutral", impact: 0.1 } // Baseline
    ];
    
    const randomTrigger = triggers[Math.floor(Math.random() * triggers.length)];
    return Math.max(0, Math.min(1, 0.5 + randomTrigger.impact));
  }

  /**
   * Calculate schedule stress impact
   */
  calculateScheduleStress(gameDate) {
    const date = new Date(gameDate);
    const dayOfWeek = date.getDay();
    
    // Back-to-back games increase volatility
    const isBackToBack = Math.random() > 0.7; // Mock back-to-back detection
    const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;
    const isTuesday = dayOfWeek === 2; // Tuesdays are somehow always chaotic
    
    let stress = 0.3; // Base stress
    if (isBackToBack) stress += 0.4;
    if (isWeekend) stress += 0.1; // Weekend games
    if (isTuesday) stress += 0.2; // Tuesday chaos factor
    
    return Math.min(1, stress);
  }

  /**
   * Assess nutritional state impact
   */
  assessNutritionalState() {
    // Satirical nutrition factors
    const factors = [
      { type: "balanced", volatility: 0.2 },
      { type: "sugar_crash", volatility: 0.7 },
      { type: "caffeine_overload", volatility: 0.6 },
      { type: "hangry", volatility: 0.8 },
      { type: "comfort_food", volatility: 0.4 },
      { type: "superfood_mode", volatility: 0.1 }
    ];
    
    const randomFactor = factors[Math.floor(Math.random() * factors.length)];
    return randomFactor.volatility;
  }

  /**
   * Calculate weather influence (satirical)
   */
  calculateWeatherImpact(gameDate) {
    // Mock weather influence on mood volatility
    const weatherTypes = [
      { type: "sunny", volatility: 0.2 },
      { type: "rainy", volatility: 0.4 },
      { type: "stormy", volatility: 0.7 },
      { type: "overcast", volatility: 0.5 },
      { type: "perfect", volatility: 0.1 }
    ];
    
    const randomWeather = weatherTypes[Math.floor(Math.random() * weatherTypes.length)];
    return randomWeather.volatility;
  }

  /**
   * Calculate overall volatility score
   */
  calculateVolatilityScore(factorValues) {
    let score = 0;
    
    Object.keys(factorValues).forEach(factor => {
      const weight = this.factors[factor].weight;
      score += factorValues[factor] * weight;
    });
    
    return Math.min(1, score);
  }

  /**
   * Determine swing level based on volatility score
   */
  determineSwingLevel(score) {
    if (score <= this.swingLevels.stable.range[1]) {
      return this.swingLevels.stable;
    } else if (score <= this.swingLevels.moderate.range[1]) {
      return this.swingLevels.moderate;
    } else {
      return this.swingLevels.turbulent;
    }
  }

  /**
   * Generate satirical mood swing prediction
   */
  generateSwingPrediction(swingLevel, volatilityScore) {
    const predictions = {
      "Stable": [
        "Emotional zen mode activated. Expect consistent performance.",
        "Steady as she goes. Perfect for clutch situations.",
        "Balanced energy detected. Optimal for team chemistry."
      ],
      "Moderate": [
        "Some emotional waves expected. Enhanced creativity possible.",
        "Moderate volatility detected. Potential for surprise plays.",
        "Emotional flexibility active. Adaptable gameplay anticipated."
      ],
      "Turbulent": [
        "High emotional intensity! Expect fireworks on the court.",
        "Emotional rollercoaster engaged. Unpredictable brilliance incoming.",
        "Volatility at maximum! Hold onto your statistical models."
      ]
    };
    
    const levelPredictions = predictions[swingLevel.level];
    return levelPredictions[Math.floor(Math.random() * levelPredictions.length)];
  }

  /**
   * Get module info and capabilities
   */
  getModuleInfo() {
    return {
      name: this.moduleName,
      version: this.version,
      purpose: "Forecasts mood swings and their impact on gameplay",
      inputs: ["Hormonal data", "Social triggers", "Sleep patterns"],
      outputs: ["Mood swing severity", "Volatility score", "Performance prediction"],
      ethicalNotice: this.ethicalNotice,
      satiricalOverlay: this.swingLevels,
      factors: this.factors
    };
  }
}

module.exports = MoodSwingMeter;