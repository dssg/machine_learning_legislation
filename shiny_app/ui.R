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
                  choices = c("104th Congress (1995-1997)",
                              "105th Congress (1997-1999)",
                              "106th Congress (1999-2001)", 
                              "107th Congress (2001-2003)", 
                              "108th Congress (2003-2005)", 
                              "109th Congress (2005-2007)", 
                              "110th Congress (2007-2009)", 
                              "111th Congress (2009-2010)", 
                              "1995-2010"),
                  selected = "1995-2010")
      
      
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