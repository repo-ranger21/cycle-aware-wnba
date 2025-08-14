# model_formula.R
# ---------------------------------------------------------------
# Cycle-Aware WNBA Predictive Formula (Modular R Implementation)
# All functions are privacy-conscious and ready for ethical deployment.
# See function documentation for details.

# 📦 Load Required Libraries
library(tidyverse)
library(lubridate)
library(glmnet)
library(scales)

# ------------------- Feature Engineering -----------------------

#' Engineer cycle-aware features from raw data
#' @param df Raw merged data.frame
#' @return Feature-engineered data.frame
engineer_features <- function(df) {
  df <- df %>%
    mutate(
      cycle_day = as.numeric(difftime(game_date, cycle_start, units = "days")) %% menstruation_duration,
      ovulation_flag = ifelse(cycle_day == ovulation_day, 1, 0),
      symptom_score = rowSums(select(., cramps, mood, discharge), na.rm = TRUE)
    ) %>%
    arrange(player_id, game_date) %>%
    group_by(player_id) %>%
    mutate(lagged_hrv = lag(hrv, 1)) %>%
    ungroup()

  # Normalize selected features
  norm_cols <- c("bbt", "hr", "hrv", "sleep_quality", "sleep_duration", "skin_temp", "breathing_rate",
                 "flow_intensity", "lh", "fsh", "estrogen", "progesterone", "symptom_score", "lagged_hrv")
  df[norm_cols] <- lapply(df[norm_cols], function(x) rescale(x, na.rm = TRUE))
  df[norm_cols] <- lapply(df[norm_cols], function(x) ifelse(is.na(x), mean(x, na.rm = TRUE), x))

  return(df)
}

# ------------------- Model Training ---------------------------

#' Train logistic regression with Lasso regularization
#' @param df Feature-engineered data.frame
#' @param response Name of response column (binary: impact_flag)
#' @param save_path File path to save model as .rds
#' @return Fitted glmnet model
train_lasso_logistic <- function(df, response = "impact_flag", save_path = "models/lasso_model.rds") {
  x <- as.matrix(df %>% select(-all_of(response)))
  y <- as.numeric(df[[response]])

  cvfit <- cv.glmnet(x, y, family = "binomial", alpha = 1, type.measure = "class")
  saveRDS(cvfit, file = save_path)
  return(cvfit)
}

# ------------------- Prediction Function ----------------------

#' Predict daily impact probabilities and flags
#' @param model_path Path to saved .rds model
#' @param newdata Feature-engineered data.frame
#' @param threshold Probability threshold for flagging
#' @return Data.frame with player_id, date, probability, flag
predict_daily <- function(model_path, newdata, threshold = 0.5) {
  model <- readRDS(model_path)
  x <- as.matrix(newdata %>% select(-player_id, -game_date))
  probs <- as.numeric(predict(model, newx = x, s = "lambda.min", type = "response"))
  flags <- ifelse(probs >= threshold, "Likely", "Unlikely")

  out <- data.frame(
    player_id = newdata$player_id,
    date = newdata$game_date,
    probability = round(probs, 3),
    flag = flags
  )
  return(out)
}

# ------------------- Explainability ---------------------------

#' Extract feature importance from trained model
#' @param model Fitted glmnet model
#' @return Named vector of coefficients
get_feature_importance <- function(model) {
  coef_vec <- coef(model, s = "lambda.min")
  importance <- as.matrix(coef_vec)
  importance <- importance[importance != 0, , drop = FALSE]
  return(importance)
}

# Tags: cycle-aware-model, glmnet, predictive-ethics, wnba-performance
