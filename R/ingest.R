# Data Ingestion Functions

# Function to load data
load_data <- function(file_path) {
  data <- read.csv(file_path)
  # Clean and preprocess data as required
  return(data)
}

# Example usage
# data <- load_data('path/to/data.csv')
