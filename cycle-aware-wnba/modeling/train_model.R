# Cycle-Aware WNBA Model Training Pipeline
# Tags: training-pipeline, glmnet, ethical-modeling, reproducible-research

#' Train cycle-aware performance model using ensemble methods
#' @param df Feature-engineered data.frame with cycle and performance features
#' @param response Name of response variable (default: "impact_flag")
#' @param save_path Path to save trained model
#' @return Trained model object
train_cycle_aware_model <- function(df, response = "impact_flag", save_path = NULL) {
  require(glmnet)
  require(randomForest) 
  require(caret)
  require(dplyr)
  
  cat("=== Cycle-Aware WNBA Model Training ===\n")
  
  # Ethics disclaimer
  cat("Ethics Disclaimer:\n")
  cat("- All data must be opt-in, anonymized, and used only for civic/public-good research.\n")
  cat("- Model outputs are probabilistic and should never drive discriminatory decisions.\n")
  cat("- Always consult qualified health staff for athlete-specific decisions.\n\n")
  
  # Load feature engineering functions
  source("../R/model_formula.R")
  
  # Prepare features
  cat("Preparing cycle-aware features...\n")
  feature_data <- prepare_cycle_features(df, response = response)
  
  # Split data for training/validation
  set.seed(42)  # for reproducibility
  train_idx <- sample(nrow(feature_data$x), 0.8 * nrow(feature_data$x))
  
  x_train <- feature_data$x[train_idx, ]
  y_train <- feature_data$y[train_idx]
  x_val <- feature_data$x[-train_idx, ]
  y_val <- feature_data$y[-train_idx]
  
  cat("Training set size:", length(y_train), "\n")
  cat("Validation set size:", length(y_val), "\n")
  
  # Train ensemble models
  cat("\n=== Training Ensemble Models ===\n")
  
  # 1. Lasso Logistic Regression
  cat("Training Lasso model...\n")
  cv_lasso <- cv.glmnet(x_train, y_train, family = "binomial", alpha = 1)
  lasso_model <- glmnet(x_train, y_train, family = "binomial", 
                       alpha = 1, lambda = cv_lasso$lambda.min)
  
  # 2. Random Forest
  cat("Training Random Forest...\n")
  rf_data <- data.frame(x_train, y = as.factor(y_train))
  rf_model <- randomForest(y ~ ., data = rf_data, ntree = 100)
  
  # 3. Ensemble model weights (simple averaging for now)
  cat("Creating ensemble model...\n")
  
  # Validation predictions
  lasso_pred <- predict(lasso_model, x_val, type = "response")[,1]
  rf_pred <- predict(rf_model, data.frame(x_val), type = "prob")[,2]
  
  # Simple ensemble (equal weights)
  ensemble_pred <- (lasso_pred + rf_pred) / 2
  
  # Evaluate ensemble
  val_auc <- pROC::auc(y_val, ensemble_pred)
  cat("Validation AUC:", round(val_auc, 3), "\n")
  
  # Create ensemble model object
  ensemble_model <- list(
    lasso = lasso_model,
    rf = rf_model,
    features = feature_data$features,
    auc = val_auc,
    metadata = list(
      training_date = Sys.time(),
      n_train = length(y_train),
      n_val = length(y_val),
      response = response
    )
  )
  
  # Save model if path provided
  if (!is.null(save_path)) {
    saveRDS(ensemble_model, save_path)
    cat("Model saved to:", save_path, "\n")
  }
  
  return(ensemble_model)
}

#' Make predictions using trained ensemble model
#' @param model_path Path to saved model or model object
#' @param newdata New data for prediction
#' @return Data.frame with predictions
predict_ensemble <- function(model_path, newdata) {
  if (is.character(model_path)) {
    model <- readRDS(model_path)
  } else {
    model <- model_path
  }
  
  # Prepare features for new data
  source("../R/model_formula.R")
  feature_data <- prepare_cycle_features(newdata, response = "dummy")
  
  # Get predictions from both models
  lasso_pred <- predict(model$lasso, feature_data$x, type = "response")[,1]
  rf_pred <- predict(model$rf, data.frame(feature_data$x), type = "prob")[,2]
  
  # Ensemble prediction (simple average)
  ensemble_pred <- (lasso_pred + rf_pred) / 2
  
  # Create output
  result <- data.frame(
    player_id = newdata$player_id,
    game_date = newdata$game_date,
    ensemble_probability = ensemble_pred,
    lasso_probability = lasso_pred,
    rf_probability = rf_pred,
    prediction = ifelse(ensemble_pred >= 0.5, "High Impact", "Low Impact")
  )
  
  return(result)
}

# Model performance evaluation utilities
evaluate_model_performance <- function(model, test_data) {
  require(pROC)
  require(caret)
  
  # Get predictions
  preds <- predict_ensemble(model, test_data)
  actual <- test_data$impact_flag
  
  # Calculate metrics
  auc <- auc(actual, preds$ensemble_probability)
  conf_matrix <- confusionMatrix(factor(ifelse(preds$ensemble_probability >= 0.5, 1, 0)), 
                                factor(actual))
  
  cat("=== Model Performance ===\n")
  cat("AUC:", round(auc, 3), "\n")
  cat("Accuracy:", round(conf_matrix$overall["Accuracy"], 3), "\n")
  cat("Sensitivity:", round(conf_matrix$byClass["Sensitivity"], 3), "\n")
  cat("Specificity:", round(conf_matrix$byClass["Specificity"], 3), "\n")
  
  return(list(
    auc = auc,
    confusion_matrix = conf_matrix,
    predictions = preds
  ))
}