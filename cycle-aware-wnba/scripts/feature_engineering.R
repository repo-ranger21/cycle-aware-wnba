# Q4Trackr: Modular Feature Engineering Script

library(tidyverse)
library(lubridate)

#' Detect cycle phase
detect_cycle_phase <- function(cycle_day, menstruation_duration, ovulation_day) {
  if (cycle_day == 0) return("Menstruation")
  if (cycle_day == ovulation_day) return("Ovulation")
  if (cycle_day < ovulation_day) return("Follicular")
  return("Luteal")
}

#' Encode matchup strength (e.g., 1=weak, 2=neutral, 3=strong)
encode_matchup <- function(opponent_rating) {
  case_when(
    opponent_rating < 0.4 ~ "Weak",
    opponent_rating < 0.7 ~ "Neutral",
    TRUE ~ "Strong"
  )
}

#' Calculate player fatigue index
fatigue_index <- function(rest_days, sleep_quality, lagged_hrv) {
  round((1/rest_days) + (1-sleep_quality) + (1-lagged_hrv), 2)
}

#' Main modular feature engineering
feature_engineering <- function(df) {
  df %>%
    mutate(
      cycle_phase = mapply(detect_cycle_phase, cycle_day, menstruation_duration, ovulation_day),
      matchup_strength = encode_matchup(opponent_rating),
      fatigue_idx = fatigue_index(rest_days, sleep_quality, lagged_hrv)
    )
}