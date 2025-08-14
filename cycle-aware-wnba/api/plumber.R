# Q4Trackr Plumber API

library(plumber)
library(tidyverse)
source("../models/model_formula.R")

#* @post /predict
#* @json
function(req, res) {
  input <- jsonlite::fromJSON(req$postBody)
  df <- as_tibble(input)
  df_fe <- engineer_features(df)
  preds <- predict_daily("../models/lasso_model.rds", df_fe)
  res$body <- jsonlite::toJSON(preds)
  res
}