# Q4Trackr: Install Required R Packages

pkgs <- c(
  "tidyverse",
  "lubridate",
  "glmnet",
  "plumber",
  "shiny",
  "ggplot2",
  "readr",
  "testthat"
)

install_if_missing <- function(pkg) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    install.packages(pkg, repos = "https://cloud.r-project.org")
  }
}

invisible(lapply(pkgs, install_if_missing))