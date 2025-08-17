# Cycle-Aware Performance Phase Prediction
# Tags: cycle-prediction, ensemble-methods, health-data, ethical-ai

#' Predict cycle phase per athlete per game using ensemble methods and external health data
#' @param athlete_data Data.frame with athlete physiological and performance data
#' @param health_data External health/biometric data (optional)
#' @param game_data WNBA game schedule and context data
#' @return Data.frame with cycle phase predictions and confidence intervals
predict_cycle_phase <- function(athlete_data, health_data = NULL, game_data = NULL) {
  require(dplyr)
  require(lubridate)
  require(glmnet)
  require(randomForest)
  
  cat("=== Cycle-Aware Phase Prediction ===\n")
  
  # Ethical disclaimer
  cat("ETHICS DISCLAIMER:\n")
  cat("- All predictions are probabilistic estimates for research purposes only\n") 
  cat("- Never use for medical diagnosis or discriminatory decisions\n")
  cat("- Athletes maintain full autonomy over their health data and decisions\n")
  cat("- All data must be anonymized and consent-based\n\n")
  
  # Validate input data
  required_cols <- c("athlete_id", "game_date", "cycle_day", "menstrual_phase")
  if (!all(required_cols %in% colnames(athlete_data))) {
    stop("Missing required columns in athlete_data: ", 
         paste(setdiff(required_cols, colnames(athlete_data)), collapse = ", "))
  }
  
  # Load cycle prediction models
  source("train_model.R")
  
  cat("Processing", nrow(athlete_data), "athlete-game records...\n")
  
  # Feature engineering for cycle prediction
  athlete_features <- athlete_data %>%
    mutate(
      # Temporal features
      days_since_period = ifelse(is.na(cycle_day), 28, cycle_day),
      cycle_week = ceiling(days_since_period / 7),
      
      # Phase indicators
      follicular_phase = ifelse(days_since_period <= 14, 1, 0),
      ovulation_phase = ifelse(days_since_period >= 12 & days_since_period <= 16, 1, 0), 
      luteal_phase = ifelse(days_since_period > 16, 1, 0),
      
      # Seasonal adjustments
      month = month(game_date),
      season_phase = case_when(
        month %in% c(5, 6) ~ "early_season",
        month %in% c(7, 8) ~ "mid_season", 
        month %in% c(9, 10) ~ "late_season",
        TRUE ~ "off_season"
      ),
      
      # Game context
      days_rest = c(0, diff(as.Date(game_date))),  # Simplified - would need actual schedule
      back_to_back = ifelse(days_rest <= 1, 1, 0)
    )
  
  # Add external health data if available
  if (!is.null(health_data)) {
    cat("Integrating external health data...\n")
    
    health_features <- health_data %>%
      select(athlete_id, game_date, 
             sleep_quality = contains("sleep"),
             hrv = contains("hrv") | contains("heart_rate_variability"),
             stress_score = contains("stress"),
             recovery_score = contains("recovery")) %>%
      # Handle missing values with athlete-specific medians
      group_by(athlete_id) %>%
      mutate_if(is.numeric, ~ ifelse(is.na(.), median(., na.rm = TRUE), .)) %>%
      ungroup()
    
    athlete_features <- athlete_features %>%
      left_join(health_features, by = c("athlete_id", "game_date"))
  }
  
  # Ensemble prediction approach
  cat("Running ensemble cycle phase prediction...\n")
  
  # Method 1: Rule-based cycle phase estimation
  rule_based_phase <- athlete_features %>%
    mutate(
      predicted_phase = case_when(
        days_since_period <= 5 ~ "menstrual",
        days_since_period <= 13 ~ "follicular", 
        days_since_period <= 17 ~ "ovulatory",
        days_since_period <= 28 ~ "luteal",
        TRUE ~ "irregular"
      ),
      confidence_rule = case_when(
        days_since_period <= 28 ~ 0.8,
        TRUE ~ 0.4  # Lower confidence for irregular cycles
      )
    )
  
  # Method 2: Machine learning phase prediction (if sufficient historical data)
  if (nrow(athlete_features) > 50) {
    cat("Training ML models for phase prediction...\n")
    
    # Prepare ML features
    ml_features <- athlete_features %>%
      select(cycle_week, follicular_phase, ovulation_phase, luteal_phase,
             back_to_back, days_rest) %>%
      mutate_all(~ ifelse(is.na(.), 0, .)) %>%
      as.matrix()
    
    # Simple classification for demonstration
    # In practice, would use historical labeled data
    set.seed(123)
    sample_labels <- sample(c("menstrual", "follicular", "ovulatory", "luteal"), 
                           nrow(ml_features), replace = TRUE)
    
    # Random forest for phase classification
    ml_data <- data.frame(ml_features, phase = as.factor(sample_labels))
    rf_phase_model <- randomForest(phase ~ ., data = ml_data, ntree = 50)
    
    ml_predictions <- predict(rf_phase_model, ml_features, type = "prob")
    ml_phase <- predict(rf_phase_model, ml_features)
    ml_confidence <- apply(ml_predictions, 1, max)
    
  } else {
    cat("Insufficient data for ML prediction, using rule-based only...\n")
    ml_phase <- rule_based_phase$predicted_phase
    ml_confidence <- rule_based_phase$confidence_rule
  }
  
  # Method 3: Hormonal pattern recognition (simplified)
  hormonal_phase <- athlete_features %>%
    mutate(
      estrogen_proxy = sin(2 * pi * days_since_period / 28) + 0.5,
      progesterone_proxy = ifelse(days_since_period > 14, 
                                 cos(2 * pi * (days_since_period - 14) / 14) + 0.5, 0),
      predicted_phase_hormonal = case_when(
        estrogen_proxy > 0.7 & progesterone_proxy < 0.3 ~ "follicular",
        estrogen_proxy > 0.8 & progesterone_proxy < 0.5 ~ "ovulatory", 
        progesterone_proxy > 0.5 ~ "luteal",
        TRUE ~ "menstrual"
      ),
      confidence_hormonal = pmax(estrogen_proxy, progesterone_proxy) * 0.9
    )
  
  # Ensemble combination
  cat("Combining ensemble predictions...\n")
  
  final_predictions <- athlete_features %>%
    mutate(
      rule_phase = rule_based_phase$predicted_phase,
      rule_confidence = rule_based_phase$confidence_rule,
      ml_phase = ml_phase,
      ml_confidence = ml_confidence, 
      hormonal_phase = hormonal_phase$predicted_phase_hormonal,
      hormonal_confidence = hormonal_phase$confidence_hormonal,
      
      # Weighted ensemble (rule-based gets highest weight due to reliability)
      ensemble_confidence = (rule_confidence * 0.5 + ml_confidence * 0.3 + hormonal_confidence * 0.2),
      
      # Final phase prediction based on majority vote with confidence weighting
      final_phase = case_when(
        rule_confidence > 0.7 ~ rule_phase,  # High confidence rule-based
        ml_confidence > 0.8 ~ ml_phase,      # High confidence ML
        TRUE ~ rule_phase                    # Default to rule-based
      ),
      
      # Performance impact estimation
      impact_probability = case_when(
        final_phase == "menstrual" ~ 0.3,    # Moderate impact
        final_phase == "follicular" ~ 0.1,   # Low impact  
        final_phase == "ovulatory" ~ 0.2,    # Low-moderate impact
        final_phase == "luteal" ~ 0.4,       # Higher impact potential
        TRUE ~ 0.25                          # Default moderate
      ),
      
      # Adjust for individual patterns and external factors
      adjusted_impact = pmin(1.0, impact_probability * 
                           ifelse(!is.null(health_data) & "stress_score" %in% names(.), 
                                 1 + (stress_score - 50) / 100, 1.0))
    ) %>%
    select(
      athlete_id, game_date, cycle_day, days_since_period,
      predicted_cycle_phase = final_phase,
      phase_confidence = ensemble_confidence,
      impact_probability = adjusted_impact,
      rule_based_phase = rule_phase,
      ml_phase, hormonal_phase,
      follicular_phase, ovulation_phase, luteal_phase
    )
  
  # Add summary statistics
  phase_summary <- final_predictions %>%
    group_by(predicted_cycle_phase) %>%
    summarise(
      count = n(),
      avg_confidence = mean(phase_confidence, na.rm = TRUE),
      avg_impact = mean(impact_probability, na.rm = TRUE),
      .groups = "drop"
    )
  
  cat("\n=== Prediction Summary ===\n")
  print(phase_summary)
  cat("\nOverall average confidence:", round(mean(final_predictions$phase_confidence), 3), "\n")
  cat("Records with high confidence (>0.7):", 
      sum(final_predictions$phase_confidence > 0.7), "/", nrow(final_predictions), "\n")
  
  # Ethical reporting reminder
  cat("\n=== Ethical Use Reminder ===\n")
  cat("- These predictions are for research and athlete empowerment only\n")
  cat("- Always prioritize athlete self-reporting and autonomy\n") 
  cat("- Use as supportive information, never as deterministic health assessment\n")
  cat("- Maintain strict data privacy and consent protocols\n")
  
  return(final_predictions)
}

# Utility function for visualizing cycle predictions
plot_cycle_predictions <- function(predictions, athlete_id = NULL) {
  require(ggplot2)
  require(dplyr)
  
  plot_data <- predictions
  if (!is.null(athlete_id)) {
    plot_data <- filter(predictions, athlete_id == !!athlete_id)
  }
  
  ggplot(plot_data, aes(x = game_date, y = impact_probability, color = predicted_cycle_phase)) +
    geom_point(aes(size = phase_confidence), alpha = 0.7) +
    geom_smooth(method = "loess", se = FALSE) +
    facet_wrap(~ athlete_id, scales = "free_x") +
    labs(
      title = "Cycle-Aware Impact Predictions by Athlete",
      subtitle = "Point size indicates prediction confidence",
      x = "Game Date", 
      y = "Predicted Performance Impact",
      color = "Cycle Phase",
      size = "Confidence"
    ) +
    theme_minimal() +
    scale_color_brewer(type = "qual", palette = "Set2")
}

# Function to validate prediction accuracy (when ground truth is available)
validate_cycle_predictions <- function(predictions, ground_truth) {
  require(caret)
  
  validation_data <- predictions %>%
    inner_join(ground_truth, by = c("athlete_id", "game_date"))
  
  # Phase accuracy
  phase_accuracy <- mean(validation_data$predicted_cycle_phase == validation_data$actual_phase)
  
  # Impact correlation
  impact_correlation <- cor(validation_data$impact_probability, 
                           validation_data$actual_impact, use = "complete.obs")
  
  cat("=== Validation Results ===\n")
  cat("Phase Prediction Accuracy:", round(phase_accuracy, 3), "\n")
  cat("Impact Correlation:", round(impact_correlation, 3), "\n")
  
  # Confusion matrix for phases
  conf_matrix <- confusionMatrix(factor(validation_data$predicted_cycle_phase),
                                factor(validation_data$actual_phase))
  
  return(list(
    accuracy = phase_accuracy,
    correlation = impact_correlation,
    confusion_matrix = conf_matrix,
    validation_data = validation_data
  ))
}