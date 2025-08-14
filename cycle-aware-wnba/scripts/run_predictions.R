# Q4Trackr: Run Model Predictions Script
# Loads sample data, applies feature engineering and model, outputs predictions

library(tidyverse)
source("models/model_formula.R")

# Load sample data
df <- read_csv("data/raw/physio_cycle_sample.csv")
df_fe <- engineer_features(df)

# Train model (for demo; in practice, load pre-trained model)
model <- train_lasso_logistic(df_fe, response = "impact_flag", save_path = "models/lasso_model.rds")

# Predict
preds <- predict_daily("models/lasso_model.rds", df_fe, threshold = 0.5)

# Save predictions
write_csv(preds, "output/predictions.csv")

cat("Predictions written to output/predictions.csv\n")