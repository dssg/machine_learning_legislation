library(shiny)

# ui.R

shinyUI(fluidPage(
  titlePanel("Congressional Earmarks from 1995-2010"),
  
  sidebarLayout(
    sidebarPanel(
      
      radioButtons("type", label = "",
                   choices = list("Total Earmarks" = "total", 
                                  "Per Capita Earmarks" = "pc")),
      br(),
      
      selectInput("var", 
                  label = "Choose a Congress to Display",
                  choices = c("104th Congress","105th Congress",
                              "106th Congress", "107th Congress", 
                              "108th Congress", "109th Congress", 
                              "110th Congress", "111th Congress",
                              "All"),
                  selected = "All")
      
      
      ),
    
    mainPanel(
      tabsetPanel(type = "tabs", 
                  tabPanel("Earmarks Map", plotOutput("map")),
                  tabPanel("Top Recipients by Topic", tableOutput("table"))
      )
    )
  )
)
)       