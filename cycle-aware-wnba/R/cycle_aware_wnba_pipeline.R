# Cycle-Aware WNBA: Modular Predictive Pipeline (R)
# Tags: wnba, cycle-aware, predictive-modeling, r, shiny, public-good
# ---------------------------------------------------------------
# Ethically models how menstrual cycle phases may impact WNBA player performance.
# All functions are privacy-conscious, reproducible, and ready for civic deployment.

# 1. ------------------- Data Ingestion --------------------------

#' Ingest and merge WNBA stats/schedule (wehoop) with physiological/cycle tracking data
#' @param physio_cycle_path Path to local CSV file (or Supabase logic)
#' @param season WNBA season year (default: current year)
#' @return merged data.frame
ingest_cycle_aware_data <- function(physio_cycle_path, season = as.numeric(format(Sys.Date(), "%Y"))) {
  require(wehoop)
  require(dplyr)
  require(readr)
  
  # Get schedule and player stats via wehoop
  schedule <- wehoop::wnba_schedule(season = season)
  stats <- wehoop::wnba_player_box(season = season)
  
  # Load physiological/cycle tracking data
  physio_cycle <- read_csv(physio_cycle_path)
  
  # Merge on player_id and date
  merged <- stats %>%
    left_join(schedule, by = "game_id") %>%
    left_join(physio_cycle, by = c("player_id", "game_date" = "date"))
  
  return(merged)
}

# 2. ------------------- Feature Engineering ----------------------

#' Engineer features: cycle_day, ovulation_flag, symptom_score, lagged HRV; normalize & impute
#' @param df Raw merged data.frame
#' @return feature-engineered data.frame
engineer_cycle_aware_features <- function(df) {
  require(dplyr)
  require(zoo)
  require(scales)
  
  # Cycle day calculation (handles NA gracefully)
  df <- df %>%
    mutate(
      cycle_day = as.numeric(difftime(game_date, cycle_start, units = "days")) %% menstruation_duration
    )
  
  # Ovulation flag
  df <- df %>%
    mutate(ovulation_flag = ifelse(cycle_day == ovulation_day, 1, 0))
  
  # Symptom score (sum of standardized symptoms)
  symptom_cols <- c("cramps", "mood", "discharge")
  df <- df %>%
    mutate(symptom_score = rowSums(select(., all_of(symptom_cols)), na.rm = TRUE))
  
  # Lagged HRV per player
  df <- df %>%
    arrange(player_id, game_date) %>%
    group_by(player_id) %>%
    mutate(lagged_hrv = lag(hrv, 1)) %>%
    ungroup()
  
  # Normalize selected features
  norm_cols <- c("bbt", "hr", "hrv", "sleep_quality", "sleep_duration", "skin_temp", "breathing_rate",
                 "flow_intensity", "lh", "fsh", "estrogen", "progesterone", "symptom_score", "lagged_hrv")
  df[norm_cols] <- lapply(df[norm_cols], function(x) scales::rescale(x, na.rm = TRUE))
  
  # Impute missing with mean
  df[norm_cols] <- lapply(df[norm_cols], function(x) ifelse(is.na(x), mean(x, na.rm = TRUE), x))
  
  return(df)
}

# 3. ------------------- Model Training ---------------------------

#' Train Lasso logistic regression model (glmnet)
#' @param df feature-engineered data.frame
#' @param response Name of binary response column (e.g., "impact_flag")
#' @param save_path File path to save .rds model
#' @return Fitted model object (cv.glmnet)
train_cycle_aware_lasso <- function(df, response = "impact_flag", save_path = "cycle_aware_lasso.rds") {
  require(glmnet)
  
  x <- as.matrix(df %>% select(-all_of(response)))
  y <- as.numeric(df[[response]])
  
  cvfit <- cv.glmnet(x, y, family = "binomial", alpha = 1, type.measure = "class")
  saveRDS(cvfit, file = save_path)
  return(cvfit)
}

# 4. ------------------- Prediction Function ----------------------

#' Predict daily probabilities and flags per player using trained model
#' @param model_path Path to saved .rds model
#' @param newdata Feature-engineered data.frame
#' @param threshold Probability threshold for "Likely" flag
#' @return data.frame with player_id, date, probability, flag
predict_cycle_aware_daily <- function(model_path, newdata, threshold = 0.5) {
  require(glmnet)
  
  model <- readRDS(model_path)
  x <- as.matrix(newdata)
  probs <- as.numeric(predict(model, newx = x, s = "lambda.min", type = "response"))
  flags <- ifelse(probs >= threshold, "Likely", "Unlikely")
  
  out <- data.frame(
    player_id = newdata$player_id,
    date      = newdata$game_date,
    probability = probs,
    flag = flags
  )
  return(out)
}

# 5. ------------------- Evaluation Metrics -----------------------

#' Compute evaluation metrics: RMSE, MAE, MAPE, Bias, RMSSE, Congruence
#' @param y_true Ground-truth binary vector
#' @param y_pred Predicted binary vector
#' @param y_prob Predicted probabilities
#' @return Named list of metrics
cycle_aware_eval_metrics <- function(y_true, y_pred, y_prob) {
  rmse <- sqrt(mean((y_true - y_pred)^2))
  mae <- mean(abs(y_true - y_pred))
  mape <- mean(abs((y_true - y_pred) / (y_true + 1e-8))) * 100
  bias <- mean(y_pred - y_true)
  rmsse <- sqrt(mean((y_pred - y_true)^2) / mean((y_true - mean(y_true))^2))
  congruence <- cor(y_true, y_prob)
  
  return(list(RMSE = rmse, MAE = mae, MAPE = mape, Bias = bias, RMSSE = rmsse, Congruence = congruence))
}

# 6. ------------------- Dashboard Stub ---------------------------

#' Launch basic Shiny dashboard to visualize predictions and cycle phases
#' Includes ethics disclaimer and privacy framing
#' @param pred_df Data.frame from prediction function
cycle_aware_dashboard <- function(pred_df) {
  require(shiny)
  require(ggplot2)
  
  ui <- fluidPage(
    titlePanel("Cycle-Aware WNBA Dashboard"),
    sidebarLayout(
      sidebarPanel(
        helpText("Ethics Disclaimer: This dashboard is for research and civic health support ONLY. All predictions are probabilistic. Athlete privacy and consent are strictly required.")
      ),
      mainPanel(
        plotOutput("probPlot"),
        tableOutput("predTable")
      )
    )
  )
  
  server <- function(input, output) {
    output$probPlot <- renderPlot({
      ggplot(pred_df, aes(x = date, y = probability, color = flag)) +
        geom_line() + geom_point() +
        facet_wrap(~player_id, scales = "free_x") +
        labs(title = "Daily Menstrual Cycle Impact Probabilities", y = "Probability", x = "Date")
    })
    output$predTable <- renderTable({
      pred_df
    })
  }
  
  shinyApp(ui = ui, server = server)
}

# ---------------------- END OF PIPELINE ---------------------------