# Q4Trackr Shiny Dashboard (with Satirical UX Toggle)

library(shiny)
library(tidyverse)
library(ggplot2)
source("../models/model_formula.R")

preds <- read_csv("../output/predictions.csv")

ui <- fluidPage(
  titlePanel("Q4Trackr: Cycle-Aware WNBA Dashboard"),
  sidebarLayout(
    sidebarPanel(
      checkboxInput("satire", "Enable Satirical UX (CrampCast™, MoodSwingMeter™)", TRUE),
      helpText("For real civic reporting, disable satirical overlays.")
    ),
    mainPanel(
      plotOutput("probPlot"),
      tableOutput("predTable"),
      conditionalPanel(
        condition = "input.satire == true",
        h4("CrampCast™"),
        plotOutput("crampPlot"),
        h4("MoodSwingMeter™"),
        plotOutput("moodPlot")
      )
    )
  )
)

server <- function(input, output) {
  output$probPlot <- renderPlot({
    ggplot(preds, aes(x = date, y = probability, color = flag)) +
      geom_point(size = 3) +
      facet_wrap(~player_id) +
      labs(title = "Win Probabilities", x = "Date", y = "Probability")
  })
  output$predTable <- renderTable({ preds })

  output$crampPlot <- renderPlot({
    ggplot(preds, aes(x = player_id, y = probability, fill = flag)) +
      geom_bar(stat = "identity") +
      labs(title = "CrampCast™: Satirical Cramps Intensity", y = "Intensity", x = "Player")
  })

  output$moodPlot <- renderPlot({
    ggplot(preds, aes(x = player_id, y = probability, fill = flag)) +
      geom_bar(stat = "identity") +
      labs(title = "MoodSwingMeter™: Satirical Mood Swings", y = "Mood Swing", x = "Player")
  })
}

shinyApp(ui = ui, server = server)