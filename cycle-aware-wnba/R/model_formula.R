# Cycle-Aware WNBA Logistic Lasso Model Formula & Optimization
# Tags: cycle-aware-model, glmnet, predictive-ethics, wnba-performance

# --------------------------------------------------------------
# Core formula for predicting cycle-related performance impact:
# --------------------------------------------------------------

#' Get optimized feature matrix and response for cycle-aware glmnet model
#' Drops multicollinear/redundant features, adds interactions, supports easy expansion.
#' @param df Feature-engineered data.frame
#' @param response Name of response variable (default: "impact_flag")
#' @return list(x = feature matrix, y = response vector, features = feature names)
prepare_cycle_features <- function(df, response = "impact_flag") {
  require(caret)
  require(dplyr)
  
  # Core features
  base_feats <- c(
    "cycle_day", "ovulation_flag", "symptom_score", "lagged_hrv",
    "bbt", "hr", "hrv", "sleep_quality", "sleep_duration",
    "skin_temp", "breathing_rate", "flow_intensity",
    "lh", "fsh", "estrogen", "progesterone"
  )
  
  # Add interaction terms
  df <- df %>%
    mutate(
      cycle_symptom_interaction = cycle_day * symptom_score,
      hr_laggedhrv_interaction = hr * lagged_hrv
    )
  inter_feats <- c("cycle_symptom_interaction", "hr_laggedhrv_interaction")
  
  # Optionally: lagged performance metrics if available
  perf_feats <- c("lagged_pts", "lagged_ast", "lagged_reb")
  perf_feats <- perf_feats[perf_feats %in% names(df)]
  
  # Remove highly collinear features (VIF threshold > 5)
  all_feats <- c(base_feats, inter_feats, perf_feats)
  df_mod <- df %>% select(all_of(all_feats))
  vif_scores <- car::vif(lm(as.formula(paste(response, "~", paste(all_feats, collapse = "+"))), data = df))
  keep_feats <- names(vif_scores[vif_scores < 5])
  
  # Feature matrix and response
  x <- as.matrix(df_mod %>% select(all_of(keep_feats)))
  y <- as.numeric(df[[response]])
  
  return(list(x = x, y = y, features = keep_feats))
}

# --------------------------------------------------------------
# Model Training (Logistic Lasso, Cross-Validation, Thresholds)
# --------------------------------------------------------------

#' Train logistic regression with Lasso regularization, cross-validate lambda
#' @param x feature matrix
#' @param y response vector
#' @param nfolds number of CV folds
#' @return fitted cv.glmnet model
train_cycle_lasso <- function(x, y, nfolds = 5) {
  require(glmnet)
  cvfit <- cv.glmnet(x, y, family = "binomial", alpha = 1, nfolds = nfolds, type.measure = "class")
  return(cvfit)
}

# --------------------------------------------------------------
# Prediction & Threshold Testing
# --------------------------------------------------------------

#' Predict probabilities & flags with flexible thresholds
#' @param model fitted glmnet CV model
#' @param x new feature matrix
#' @param thresholds vector of thresholds to test
#' @return data.frame of probabilities and flags for each threshold
predict_cycle_impact <- function(model, x, thresholds = c(0.4, 0.5, 0.6)) {
  probs <- as.numeric(predict(model, newx = x, s = "lambda.min", type = "response"))
  flag_tbl <- sapply(thresholds, function(th) ifelse(probs >= th, "Likely", "Unlikely"))
  out <- data.frame(probability = probs, flag_0.4 = flag_tbl[,1], flag_0.5 = flag_tbl[,2], flag_0.6 = flag_tbl[,3])
  return(out)
}

# --------------------------------------------------------------
# Feature Importance & Explainability
# --------------------------------------------------------------

#' Output feature importance (abs(coef)), visualize coefficients
#' @param model fitted glmnet CV model
#' @param features Feature names
#' @return data.frame of feature importances
cycle_feature_importance <- function(model, features) {
  coefs <- as.numeric(coef(model, s = "lambda.min"))[-1] # drop intercept
  importance <- abs(coefs)
  out <- data.frame(feature = features, coefficient = coefs, importance = importance)
  out <- out[order(-out$importance), ]
  return(out)
}

#' Visualize coefficients (barplot)
#' @param importance_df output from cycle_feature_importance
plot_cycle_coefficients <- function(importance_df) {
  require(ggplot2)
  ggplot(importance_df, aes(x = reorder(feature, importance), y = coefficient)) +
    geom_bar(stat = "identity", fill = "steelblue") +
    coord_flip() +
    labs(title = "Cycle-Aware Model Feature Coefficients", x = "Feature", y = "Coefficient")
}

# --------------------------------------------------------------
# Ethical Framing & Documentation
# --------------------------------------------------------------

#' Print biological rationale and disclaimer for each feature
cycle_feature_rationale <- function() {
  rationale <- list(
    cycle_day = "Days since cycle start; reflects hormonal progression",
    ovulation_flag = "Ovulation period may impact energy, mood, and hydration",
    symptom_score = "Aggregates self-reported symptoms linked to cycle effects",
    lagged_hrv = "Heart rate variability may capture stress/fatigue trends",
    bbt = "Basal body temperature varies across the cycle, indicating phase",
    hr = "Heart rate may change due to hormonal shifts",
    hrv = "Current HRV reflects stress and recovery",
    sleep_quality = "Sleep disturbances can correlate with cycle phase",
    sleep_duration = "Reduced sleep may amplify cycle-linked effects",
    skin_temp = "Thermal patterns can flag luteal phase changes",
    breathing_rate = "Respiratory changes may indicate pain or fatigue",
    flow_intensity = "Heavy flows can reduce performance capacity",
    lh = "Luteinizing hormone peaks at ovulation",
    fsh = "Follicle-stimulating hormone tracks follicular phase",
    estrogen = "Estrogen rises pre-ovulation, impacts mood and energy",
    progesterone = "Progesterone peaks post-ovulation, affects recovery"
  )
  cat("Biological rationale for included features:\n")
  for (f in names(rationale)) cat(sprintf("- %s: %s\n", f, rationale[[f]]))
  cat("\nEthics Disclaimer:\n- All data must be opt-in, anonymized, and used only for civic/public-good research.\n- Do not overinterpret predictions. Always consult qualified health staff.\n- Model outputs are probabilistic and should never drive discriminatory decisions.\n")
}

# --------------------------------------------------------------
# Modularity for Research Deployment
# --------------------------------------------------------------

#' Easily update features/response for reproducible civic research
#' See 'prepare_cycle_features' for swapping features or response.
#' All components are ready for integration into larger civic pipelines.

# --------------------------------------------------------------
# End of model_formula.R
# --------------------------------------------------------------