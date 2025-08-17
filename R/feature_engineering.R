# Feature Engineering Functions

#' Engineer features for Cycle-Aware WNBA model
#' @param df Merged dataframe
#' @return Feature dataframe
engineer_features <- function(df) {
  library(zoo)
  library(caret)
  
  # Calculate cycle_day (days since last cycle start)
  df <- df %>%
    group_by(player_id) %>%
    mutate(cycle_day = as.numeric(game_date - cycle_start_date))
  
  # Ovulation flag (1 if cycle_day == ovulation_day)
  df <- df %>%
    mutate(ovulation_flag = ifelse(cycle_day == ovulation_day, 1, 0))
  
  # Symptom score (sum of coded symptoms: cramps, mood, discharge, etc.)
  symptom_cols <- c("cramps", "mood", "discharge")
  df <- df %>%
    mutate(symptom_score = rowSums(select(., all_of(symptom_cols)), na.rm = TRUE))
  
  # Lagged HRV (previous 3-day rolling mean)
  df <- df %>%
    arrange(player_id, game_date) %>%
    group_by(player_id) %>%
    mutate(lagged_HRV = rollmean(HRV, k = 3, fill = NA, align = "right"))
  
  # Normalize numeric features
  num_cols <- c("BBT", "HR", "HRV", "sleep_quality", "sleep_duration", "skin_temp", "breathing_rate", "symptom_score", "lagged_HRV")
  df[num_cols] <- lapply(df[num_cols], function(x) {
    x[is.infinite(x)] <- NA
    (x - mean(x, na.rm = TRUE)) / sd(x, na.rm = TRUE)
  })
  
  # Impute missing data (median imputation)
  preProc <- preProcess(df[num_cols], method = "medianImpute")
  df[num_cols] <- predict(preProc, df[num_cols])
  
  return(df)
}