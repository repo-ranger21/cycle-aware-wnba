# Parity Check: Reproducibility and Audit Utility
# Tags: reproducibility, audit, environment-validation, quality-assurance

#' Validate reproducibility across different environments and audit model consistency
#' @param model_path Path to trained model for validation
#' @param test_data Test dataset for consistency checks
#' @param reference_results Reference results for comparison (optional)
#' @return List with reproducibility test results and recommendations
parity_check <- function(model_path = NULL, test_data = NULL, reference_results = NULL) {
  require(digest)
  require(sessionInfo)
  require(dplyr)
  
  cat("=== Cycle-Aware WNBA Parity Check ===\n")
  cat("Validating reproducibility and environment consistency\n")
  cat("Timestamp:", format(Sys.time(), "%Y-%m-%d %H:%M:%S"), "\n\n")
  
  # Initialize results list
  parity_results <- list(
    timestamp = Sys.time(),
    environment = list(),
    model_checks = list(),
    data_checks = list(),
    reproducibility_score = 0,
    recommendations = character()
  )
  
  # 1. Environment Validation
  cat("=== Environment Validation ===\n")
  
  # R version check
  r_version <- R.version.string
  cat("R Version:", r_version, "\n")
  parity_results$environment$r_version <- r_version
  
  # Package versions
  required_packages <- c("dplyr", "glmnet", "randomForest", "ggplot2", 
                        "lubridate", "caret", "pROC", "shiny")
  
  package_info <- data.frame()
  missing_packages <- character()
  
  for (pkg in required_packages) {
    if (requireNamespace(pkg, quietly = TRUE)) {
      version <- as.character(packageVersion(pkg))
      package_info <- rbind(package_info, data.frame(
        package = pkg, 
        version = version,
        available = TRUE
      ))
      cat("✓", pkg, "version", version, "\n")
    } else {
      missing_packages <- c(missing_packages, pkg)
      package_info <- rbind(package_info, data.frame(
        package = pkg,
        version = NA,
        available = FALSE
      ))
      cat("✗", pkg, "MISSING\n")
    }
  }
  
  parity_results$environment$packages <- package_info
  parity_results$environment$missing_packages <- missing_packages
  
  # System information
  sys_info <- Sys.info()
  cat("Operating System:", sys_info[["sysname"]], sys_info[["release"]], "\n")
  cat("Machine:", sys_info[["machine"]], "\n")
  parity_results$environment$system <- sys_info
  
  # Random seed consistency test
  cat("\n=== Random Seed Consistency ===\n")
  set.seed(42)
  random_test_1 <- rnorm(10)
  set.seed(42)  
  random_test_2 <- rnorm(10)
  
  seed_consistent <- all.equal(random_test_1, random_test_2)
  if (isTRUE(seed_consistent)) {
    cat("✓ Random seed reproducibility: PASS\n")
    parity_results$reproducibility_score <- parity_results$reproducibility_score + 20
  } else {
    cat("✗ Random seed reproducibility: FAIL\n")
    parity_results$recommendations <- c(parity_results$recommendations,
                                       "Random seed reproducibility failed - check R installation")
  }
  
  # 2. Model Validation (if model provided)
  if (!is.null(model_path) && file.exists(model_path)) {
    cat("\n=== Model Validation ===\n")
    
    tryCatch({
      model <- readRDS(model_path)
      
      # Model structure check
      required_components <- c("lasso", "rf", "features", "auc", "metadata")
      model_components <- names(model)
      missing_components <- setdiff(required_components, model_components)
      
      if (length(missing_components) == 0) {
        cat("✓ Model structure: COMPLETE\n")
        parity_results$reproducibility_score <- parity_results$reproducibility_score + 20
      } else {
        cat("✗ Model missing components:", paste(missing_components, collapse = ", "), "\n")
        parity_results$recommendations <- c(parity_results$recommendations,
                                           paste("Model missing:", paste(missing_components, collapse = ", ")))
      }
      
      # Model metadata check
      if (!is.null(model$metadata)) {
        metadata <- model$metadata
        cat("Model training date:", as.character(metadata$training_date), "\n")
        cat("Training set size:", metadata$n_train, "\n")
        cat("Validation AUC:", round(model$auc, 3), "\n")
        
        parity_results$model_checks$metadata <- metadata
        parity_results$model_checks$auc <- model$auc
      }
      
      # Feature consistency check
      if (!is.null(model$features)) {
        cat("Model features (", length(model$features), "):", 
            paste(head(model$features, 5), collapse = ", "), 
            ifelse(length(model$features) > 5, "...", ""), "\n")
        parity_results$model_checks$features <- model$features
      }
      
      parity_results$model_checks$structure_valid <- TRUE
      
    }, error = function(e) {
      cat("✗ Model loading failed:", e$message, "\n")
      parity_results$model_checks$structure_valid <- FALSE
      parity_results$recommendations <- c(parity_results$recommendations,
                                         paste("Model loading error:", e$message))
    })
  } else if (!is.null(model_path)) {
    cat("\n=== Model Validation ===\n")
    cat("✗ Model file not found:", model_path, "\n")
    parity_results$recommendations <- c(parity_results$recommendations,
                                       "Model file not found - check path")
  }
  
  # 3. Data Validation (if test data provided)  
  if (!is.null(test_data)) {
    cat("\n=== Data Validation ===\n")
    
    # Data structure check
    expected_cols <- c("athlete_id", "game_date", "cycle_day")
    available_cols <- names(test_data)
    missing_cols <- setdiff(expected_cols, available_cols)
    
    if (length(missing_cols) == 0) {
      cat("✓ Required columns present\n")
      parity_results$reproducibility_score <- parity_results$reproducibility_score + 15
    } else {
      cat("✗ Missing required columns:", paste(missing_cols, collapse = ", "), "\n")
      parity_results$recommendations <- c(parity_results$recommendations,
                                         paste("Missing data columns:", paste(missing_cols, collapse = ", ")))
    }
    
    # Data quality checks
    row_count <- nrow(test_data)
    na_counts <- sapply(test_data, function(x) sum(is.na(x)))
    
    cat("Dataset size:", row_count, "rows,", ncol(test_data), "columns\n")
    cat("Missing values per column:\n")
    for (col in names(na_counts)[na_counts > 0]) {
      cat("  ", col, ":", na_counts[col], "(", round(100 * na_counts[col] / row_count, 1), "%)\n")
    }
    
    parity_results$data_checks <- list(
      row_count = row_count,
      col_count = ncol(test_data),
      missing_values = na_counts,
      columns = available_cols
    )
    
    # Data consistency check (hash)
    data_hash <- digest(test_data, algo = "md5")
    cat("Data hash (MD5):", data_hash, "\n")
    parity_results$data_checks$hash <- data_hash
    
    if (row_count > 0 && all(na_counts < row_count * 0.5)) {
      parity_results$reproducibility_score <- parity_results$reproducibility_score + 15
    }
  }
  
  # 4. Reproducibility Test (if model and data available)
  if (!is.null(model_path) && !is.null(test_data) && file.exists(model_path)) {
    cat("\n=== Reproducibility Test ===\n")
    
    tryCatch({
      # Load prediction function
      source("modeling/predict_cycle_phase.R", local = TRUE)
      
      # Run prediction twice with same data
      set.seed(123)
      pred_1 <- predict_cycle_phase(test_data)
      
      set.seed(123)
      pred_2 <- predict_cycle_phase(test_data) 
      
      # Compare results
      if (nrow(pred_1) == nrow(pred_2)) {
        numeric_cols <- sapply(pred_1, is.numeric)
        numeric_diffs <- sapply(names(pred_1)[numeric_cols], function(col) {
          max(abs(pred_1[[col]] - pred_2[[col]]), na.rm = TRUE)
        })
        
        max_diff <- max(numeric_diffs, na.rm = TRUE)
        
        if (max_diff < 1e-10) {
          cat("✓ Prediction reproducibility: PERFECT\n")
          parity_results$reproducibility_score <- parity_results$reproducibility_score + 30
        } else if (max_diff < 1e-6) {
          cat("✓ Prediction reproducibility: GOOD (max diff:", scientific(max_diff), ")\n")
          parity_results$reproducibility_score <- parity_results$reproducibility_score + 25
        } else {
          cat("⚠ Prediction reproducibility: MARGINAL (max diff:", scientific(max_diff), ")\n")
          parity_results$reproducibility_score <- parity_results$reproducibility_score + 10
          parity_results$recommendations <- c(parity_results$recommendations,
                                             "Prediction reproducibility concerns - check random processes")
        }
      } else {
        cat("✗ Prediction reproducibility: FAILED - different result sizes\n")
        parity_results$recommendations <- c(parity_results$recommendations,
                                           "Prediction results have different sizes between runs")
      }
      
    }, error = function(e) {
      cat("✗ Reproducibility test failed:", e$message, "\n")
      parity_results$recommendations <- c(parity_results$recommendations,
                                         paste("Reproducibility test error:", e$message))
    })
  }
  
  # 5. Reference Comparison (if reference results provided)
  if (!is.null(reference_results)) {
    cat("\n=== Reference Comparison ===\n")
    
    # Compare against reference benchmark
    if ("auc" %in% names(reference_results) && !is.null(parity_results$model_checks$auc)) {
      auc_diff <- abs(parity_results$model_checks$auc - reference_results$auc)
      if (auc_diff < 0.01) {
        cat("✓ AUC matches reference (diff:", round(auc_diff, 4), ")\n")
      } else if (auc_diff < 0.05) {
        cat("⚠ AUC close to reference (diff:", round(auc_diff, 4), ")\n")
        parity_results$recommendations <- c(parity_results$recommendations,
                                           "AUC differs from reference - investigate model changes")
      } else {
        cat("✗ AUC significantly different from reference (diff:", round(auc_diff, 4), ")\n") 
        parity_results$recommendations <- c(parity_results$recommendations,
                                           "AUC significantly different - major model change detected")
      }
    }
  }
  
  # 6. Final Assessment
  cat("\n=== Final Assessment ===\n")
  cat("Overall Reproducibility Score:", parity_results$reproducibility_score, "/100\n")
  
  if (parity_results$reproducibility_score >= 90) {
    assessment <- "EXCELLENT"
    cat("🏆 Assessment: EXCELLENT - Production ready\n")
  } else if (parity_results$reproducibility_score >= 70) {
    assessment <- "GOOD" 
    cat("✅ Assessment: GOOD - Minor issues to address\n")
  } else if (parity_results$reproducibility_score >= 50) {
    assessment <- "MARGINAL"
    cat("⚠️  Assessment: MARGINAL - Significant improvements needed\n") 
  } else {
    assessment <- "POOR"
    cat("❌ Assessment: POOR - Major reproducibility issues\n")
  }
  
  parity_results$assessment <- assessment
  
  # Recommendations
  if (length(parity_results$recommendations) > 0) {
    cat("\n=== Recommendations ===\n")
    for (i in seq_along(parity_results$recommendations)) {
      cat(i, ".", parity_results$recommendations[i], "\n")
    }
  } else {
    cat("\n✅ No specific recommendations - system appears healthy\n")
  }
  
  return(parity_results)
}

# Utility to save parity check results
save_parity_results <- function(parity_results, output_dir = "output") {
  require(jsonlite)
  
  if (!dir.exists(output_dir)) {
    dir.create(output_dir, recursive = TRUE)
  }
  
  # Generate filename with timestamp
  timestamp <- format(parity_results$timestamp, "%Y%m%d_%H%M%S")
  filename <- file.path(output_dir, paste0("parity_check_", timestamp, ".json"))
  
  # Save as JSON
  write_json(parity_results, filename, pretty = TRUE, auto_unbox = TRUE)
  cat("Parity check results saved to:", filename, "\n")
  
  # Create summary report
  summary_file <- file.path(output_dir, paste0("parity_summary_", timestamp, ".txt"))
  
  summary_text <- paste0(
    "Cycle-Aware WNBA Parity Check Summary\n",
    "=====================================\n",
    "Date: ", format(parity_results$timestamp, "%Y-%m-%d %H:%M:%S"), "\n",
    "Assessment: ", parity_results$assessment, "\n",
    "Score: ", parity_results$reproducibility_score, "/100\n\n",
    
    "Environment:\n",
    "- R Version: ", parity_results$environment$r_version, "\n",
    "- Missing Packages: ", 
    ifelse(length(parity_results$environment$missing_packages) == 0, 
           "None", paste(parity_results$environment$missing_packages, collapse = ", ")), "\n\n",
    
    "Recommendations:\n",
    paste(paste("- ", parity_results$recommendations), collapse = "\n"), "\n",
    ifelse(length(parity_results$recommendations) == 0, "- None", "")
  )
  
  writeLines(summary_text, summary_file)
  cat("Summary report saved to:", summary_file, "\n")
  
  return(filename)
}

# Automated parity check for CI/CD pipelines
automated_parity_check <- function(config_file = "parity_config.json") {
  cat("=== Automated Parity Check ===\n")
  
  # Default configuration
  default_config <- list(
    model_path = "models/ensemble_model.rds",
    test_data_path = "data/processed/test_data.csv", 
    reference_results_path = "output/reference_results.json",
    output_dir = "output",
    fail_threshold = 50
  )
  
  # Load configuration if exists
  if (file.exists(config_file)) {
    config <- jsonlite::fromJSON(config_file)
    # Merge with defaults
    for (key in names(default_config)) {
      if (!(key %in% names(config))) {
        config[[key]] <- default_config[[key]]
      }
    }
  } else {
    config <- default_config
    cat("Using default configuration\n")
  }
  
  # Load test data if available
  test_data <- NULL
  if (file.exists(config$test_data_path)) {
    test_data <- read.csv(config$test_data_path)
  }
  
  # Load reference results if available  
  reference_results <- NULL
  if (file.exists(config$reference_results_path)) {
    reference_results <- jsonlite::fromJSON(config$reference_results_path)
  }
  
  # Run parity check
  results <- parity_check(
    model_path = config$model_path,
    test_data = test_data,
    reference_results = reference_results
  )
  
  # Save results
  save_parity_results(results, config$output_dir)
  
  # Exit with error code if below threshold (for CI/CD)
  if (results$reproducibility_score < config$fail_threshold) {
    cat("\n❌ PARITY CHECK FAILED - Score below threshold\n")
    quit(status = 1)  # Exit with error for CI/CD
  } else {
    cat("\n✅ PARITY CHECK PASSED\n")
    quit(status = 0)  # Exit successfully
  }
}