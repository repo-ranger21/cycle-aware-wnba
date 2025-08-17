# Betting Spreads Synchronization Utility
# Tags: spreads-sync, data-integration, reproducible-research

#' Sync betting spreads from external sources and align with game IDs and cycle phases
#' @param game_data WNBA game schedule data with game_ids
#' @param cycle_data Athlete cycle phase data
#' @param spread_sources List of external spread data sources
#' @return Data.frame with aligned spreads, game IDs, and cycle phases
sync_betting_spreads <- function(game_data, cycle_data, spread_sources = NULL) {
  require(dplyr)
  require(lubridate)
  require(httr)
  require(jsonlite)
  
  cat("=== Betting Spreads Synchronization ===\n")
  
  # Ethics disclaimer for gambling data usage
  cat("ETHICS NOTICE:\n")
  cat("- Betting data is used solely for research and performance analysis\n")
  cat("- No gambling promotion or encouragement intended\n") 
  cat("- Focus on understanding performance patterns, not betting outcomes\n")
  cat("- All data usage complies with responsible research practices\n\n")
  
  # Default spread sources (placeholder URLs for demonstration)
  if (is.null(spread_sources)) {
    spread_sources <- list(
      espn = "https://site.api.espn.com/apis/site/v2/sports/basketball/wnba/scoreboard",
      sportsbook = "https://api.example-sportsbook.com/wnba/lines",  # Placeholder
      odds_api = "https://api.the-odds-api.com/v4/sports/basketball_wnba/odds"  # Placeholder
    )
  }
  
  cat("Syncing spreads from", length(spread_sources), "sources...\n")
  
  # Initialize spreads collection
  all_spreads <- data.frame()
  
  # Sync from each source
  for (source_name in names(spread_sources)) {
    cat("Fetching from", source_name, "...\n")
    
    tryCatch({
      # Simulate spread data fetching (replace with actual API calls)
      spread_data <- simulate_spread_data(game_data, source_name)
      
      if (nrow(spread_data) > 0) {
        spread_data$source <- source_name
        all_spreads <- bind_rows(all_spreads, spread_data)
        cat("  Retrieved", nrow(spread_data), "spread records\n")
      }
    }, error = function(e) {
      cat("  Error fetching from", source_name, ":", e$message, "\n")
    })
  }
  
  if (nrow(all_spreads) == 0) {
    warning("No spread data retrieved from any source")
    return(data.frame())
  }
  
  cat("Total spread records retrieved:", nrow(all_spreads), "\n")
  
  # Clean and standardize spread data
  cat("Standardizing spread data...\n")
  
  standardized_spreads <- all_spreads %>%
    mutate(
      game_date = as.Date(game_date),
      # Standardize team names
      home_team = standardize_team_names(home_team),
      away_team = standardize_team_names(away_team),
      # Clean spread values
      spread = as.numeric(spread),
      total_over_under = as.numeric(total_over_under),
      # Add timestamp for tracking
      sync_timestamp = Sys.time()
    ) %>%
    filter(!is.na(spread)) %>%  # Remove invalid spreads
    arrange(game_date, home_team)
  
  # Align with game IDs
  cat("Aligning spreads with game IDs...\n")
  
  aligned_spreads <- standardized_spreads %>%
    left_join(
      game_data %>% select(game_id, game_date, home_team, away_team),
      by = c("game_date", "home_team", "away_team")
    ) %>%
    filter(!is.na(game_id))  # Keep only matched games
  
  cat("Aligned", nrow(aligned_spreads), "spread records with game IDs\n")
  
  # Integrate with cycle phase data
  if (!is.null(cycle_data) && nrow(cycle_data) > 0) {
    cat("Integrating cycle phase data...\n")
    
    cycle_enhanced_spreads <- aligned_spreads %>%
      left_join(
        cycle_data %>% 
          select(athlete_id, game_date, predicted_cycle_phase, 
                 phase_confidence, impact_probability) %>%
          group_by(game_date) %>%
          summarise(
            avg_menstrual_impact = mean(ifelse(predicted_cycle_phase == "menstrual", 
                                             impact_probability, 0), na.rm = TRUE),
            avg_luteal_impact = mean(ifelse(predicted_cycle_phase == "luteal", 
                                          impact_probability, 0), na.rm = TRUE),
            high_impact_players = sum(impact_probability > 0.3, na.rm = TRUE),
            total_players = n(),
            .groups = "drop"
          ),
        by = "game_date"
      ) %>%
      mutate(
        # Calculate cycle-adjusted metrics
        cycle_adjustment_factor = (avg_menstrual_impact + avg_luteal_impact) / 2,
        high_impact_ratio = high_impact_players / pmax(total_players, 1),
        
        # Adjust spreads based on cycle impact (research purpose)
        cycle_adjusted_spread = spread + (cycle_adjustment_factor * 2 - 1),  # +/-1 adjustment
        
        # Create cycle impact categories
        cycle_impact_category = case_when(
          high_impact_ratio > 0.4 ~ "high_cycle_impact",
          high_impact_ratio > 0.2 ~ "moderate_cycle_impact", 
          TRUE ~ "low_cycle_impact"
        )
      )
    
    final_spreads <- cycle_enhanced_spreads
    cat("Added cycle phase integration to", nrow(final_spreads), "records\n")
    
  } else {
    final_spreads <- aligned_spreads
    cat("No cycle data provided - spreads only\n")
  }
  
  # Add data quality metrics
  final_spreads <- final_spreads %>%
    mutate(
      data_quality_score = case_when(
        !is.na(game_id) & !is.na(spread) & !is.na(total_over_under) ~ 1.0,
        !is.na(game_id) & !is.na(spread) ~ 0.8,
        !is.na(game_id) ~ 0.6,
        TRUE ~ 0.3
      ),
      
      # Flag potential outliers
      spread_outlier = abs(spread) > 20,  # Unusual spreads
      total_outlier = total_over_under < 120 | total_over_under > 220  # Unusual totals
    )
  
  # Summary statistics
  cat("\n=== Sync Summary ===\n")
  cat("Total games with spreads:", length(unique(final_spreads$game_id)), "\n")
  cat("Average spread:", round(mean(final_spreads$spread, na.rm = TRUE), 2), "\n")
  cat("Average total:", round(mean(final_spreads$total_over_under, na.rm = TRUE), 1), "\n")
  cat("Data quality > 0.8:", sum(final_spreads$data_quality_score > 0.8), "/", nrow(final_spreads), "\n")
  
  if ("cycle_impact_category" %in% names(final_spreads)) {
    cycle_summary <- table(final_spreads$cycle_impact_category)
    cat("\nCycle Impact Distribution:\n")
    print(cycle_summary)
  }
  
  return(final_spreads)
}

# Simulate spread data for demonstration (replace with actual API calls)
simulate_spread_data <- function(game_data, source_name) {
  require(dplyr)
  
  # Create simulated spread data based on game schedule
  simulated <- game_data %>%
    sample_n(min(50, nrow(game_data))) %>%  # Simulate partial coverage
    mutate(
      spread = rnorm(n(), mean = 0, sd = 5),  # Random spreads around 0
      total_over_under = rnorm(n(), mean = 165, sd = 15),  # WNBA typical totals
      home_odds = -110,  # Standard odds
      away_odds = -110,
      source = source_name
    ) %>%
    select(game_date, home_team, away_team, spread, total_over_under, 
           home_odds, away_odds, source)
  
  return(simulated)
}

# Standardize team names across different sources
standardize_team_names <- function(team_names) {
  # Mapping for common team name variations
  team_mapping <- list(
    "Las Vegas Aces" = c("LV Aces", "Vegas Aces", "LAS"),
    "New York Liberty" = c("NY Liberty", "New York", "NYL"),
    "Seattle Storm" = c("Seattle", "SEA"),
    "Phoenix Mercury" = c("Phoenix", "PHX"),
    "Minnesota Lynx" = c("Minnesota", "MIN"),
    "Connecticut Sun" = c("Connecticut", "CONN", "CON"),
    "Chicago Sky" = c("Chicago", "CHI"),
    "Atlanta Dream" = c("Atlanta", "ATL"),
    "Washington Mystics" = c("Washington", "WAS"),
    "Indiana Fever" = c("Indiana", "IND"),
    "Dallas Wings" = c("Dallas", "DAL"),
    "Los Angeles Sparks" = c("LA Sparks", "Los Angeles", "LAS")
  )
  
  standardized <- team_names
  for (standard_name in names(team_mapping)) {
    for (variant in team_mapping[[standard_name]]) {
      standardized[standardized == variant] <- standard_name
    }
  }
  
  return(standardized)
}

# Utility to export synchronized spreads
export_spreads <- function(spreads_data, file_path) {
  require(readr)
  
  write_csv(spreads_data, file_path)
  cat("Spreads data exported to:", file_path, "\n")
  
  # Create summary report
  summary_path <- gsub("\\.csv$", "_summary.txt", file_path)
  
  summary_text <- paste0(
    "Betting Spreads Sync Summary\n",
    "Generated: ", Sys.time(), "\n",
    "Total Records: ", nrow(spreads_data), "\n",
    "Unique Games: ", length(unique(spreads_data$game_id)), "\n",
    "Date Range: ", min(spreads_data$game_date), " to ", max(spreads_data$game_date), "\n",
    "Data Sources: ", paste(unique(spreads_data$source), collapse = ", "), "\n",
    "Average Data Quality: ", round(mean(spreads_data$data_quality_score), 3), "\n"
  )
  
  writeLines(summary_text, summary_path)
  cat("Summary report saved to:", summary_path, "\n")
}

# Schedule regular syncing (for production use)
schedule_spread_sync <- function(game_data, cycle_data, output_dir, interval_hours = 6) {
  cat("Scheduling spread sync every", interval_hours, "hours\n")
  cat("Output directory:", output_dir, "\n")
  
  # This would integrate with a scheduler like cron in production
  cat("Note: Implement with system scheduler for production deployment\n")
  
  # Example sync function call
  sync_function <- function() {
    spreads <- sync_betting_spreads(game_data, cycle_data)
    output_file <- file.path(output_dir, paste0("spreads_", Sys.Date(), ".csv"))
    export_spreads(spreads, output_file)
  }
  
  return(sync_function)
}