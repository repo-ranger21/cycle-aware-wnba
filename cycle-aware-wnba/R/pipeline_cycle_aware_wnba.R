# Cycle-Aware WNBA Predictive Pipeline (Modular R Implementation)
# ---------------------------------------------------------------
# All functions are privacy-conscious and ready for ethical deployment.
# See function documentation for details.

# 1. ------------------- Data Ingestion --------------------------

#' Ingest WNBA schedule & stats using wehoop, merge with phys/cycle data
#' @param physio_cycle_path Path to local CSV (or Supabase logic)
#' @return Merged data.frame
ingest_data <- function(physio_cycle_path) {
  # Load required packages
  require(wehoop)
  require(dplyr)
  require(readr)
  
  # Pull WNBA game schedule and player stats
  schedule <- wehoop::wnba_schedule(season = lubridate::year(Sys.Date()))
  stats <- wehoop::wnba_player_box(season = lubridate::year(Sys.Date()))
  
  # Load physiological/cycle tracking data
  physio_cycle <- read_csv(physio_cycle_path)
  
  # Merge by player_id and game_date
  merged <- stats %>%
    left_join(schedule, by = c("game_id")) %>%
    left_join(physio_cycle, by = c("player_id", "game_date" = "date"))
  
  return(merged)
}

# 2. ------------------- Feature Engineering ----------------------

#' Engineer cycle-aware features: cycle_day, symptom_score, ovulation_flag, lagged HRV
#' Normalize inputs, handle missing data.
#' @param df Raw merged data.frame
#' @return Feature-engineered data.frame
engineer_features <- function(df) {
  require(dplyr)
  require(zoo)
  require(scales)
  
  # Cycle day calculation
  df <- df %>%
    mutate(cycle_day = as.numeric(difftime(game_date, cycle_start, units = "days")) %% menstruation_duration)
  
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
  
  # Handle missing with mean imputation
  df[norm_cols] <- lapply(df[norm_cols], function(x) ifelse(is.na(x), mean(x, na.rm = TRUE), x))
  
  return(df)
}

# 3. ------------------- Model Training ---------------------------

#' Train logistic regression with Lasso regularization
#' @param df Feature-engineered data.frame
#' @param response Name of response column (binary: performance impact)
#' @param save_path File path to save model as .rds
#' @return Fitted glmnet model
train_lasso_logistic <- function(df, response = "impact_flag", save_path = "lasso_model.rds") {
  require(glmnet)
  
  # Prepare data
  x <- as.matrix(df %>% select(-all_of(response)))
  y <- as.numeric(df[[response]])
  
  # Cross-validated Lasso logistic regression
  cvfit <- cv.glmnet(x, y, family = "binomial", alpha = 1, type.measure = "class")
  
  # Save model
  saveRDS(cvfit, file = save_path)
  return(cvfit)
}

# 4. ------------------- Prediction Function ----------------------

#' Load model and predict daily probabilities/flags per player
#' @param model_path Path to saved .rds model
#' @param newdata New feature-engineered data.frame
#' @param threshold Probability threshold for "Likely" flag
#' @return Data.frame with player_id, date, probability, flag
predict_daily <- function(model_path, newdata, threshold = 0.5) {
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
#' @param y_true Ground-truth vector
#' @param y_pred Predicted values (binary)
#' @param y_prob Predicted probabilities
#' @return Named list of metrics
eval_metrics <- function(y_true, y_pred, y_prob) {
  rmse <- sqrt(mean((y_true - y_pred)^2))
  mae <- mean(abs(y_true - y_pred))
  mape <- mean(abs((y_true - y_pred) / (y_true + 1e-8))) * 100
  bias <- mean(y_pred - y_true)
  rmsse <- sqrt(mean((y_pred - y_true)^2) / mean((y_true - mean(y_true))^2))
  congruence <- cor(y_true, y_prob)
  
  return(list(RMSE = rmse, MAE = mae, MAPE = mape, Bias = bias, RMSSE = rmsse, Congruence = congruence))
}

# 6. ------------------- Dashboard Stub ---------------------------

#' Basic Shiny dashboard stub for predictions & cycle phase visualization
#' Privacy/ethics disclaimer included.
cycle_dashboard <- function(pred_df) {
  require(shiny)
  require(ggplot2)
  
  ui <- fluidPage(
    titlePanel("Cycle-Aware WNBA Dashboard"),
    sidebarLayout(
      sidebarPanel(
        helpText("This dashboard is for research and athlete support ONLY. All predictions are probabilistic. Athlete privacy and consent is strictly required.")
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
        labs(title = "Daily Impact Probabilities", y = "Probability", x = "Date")
    })
    output$predTable <- renderTable({
      pred_df
    })
  }
  
  shinyApp(ui = ui, server = server)
}

# ---------------------- END OF PIPELINE ---------------------------