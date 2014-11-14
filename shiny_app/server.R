library(shiny)
source("data/helpers.R")
library(maps)
library(mapproj)
## load the data ## 
congress_earmarks <- read.csv("data/congress_earmarks.csv")
congress_table <- read.csv("data/earmarks_top5.csv")
colnames(congress_table)<-
  c("Congress","Agriculture and Rural Development", 
    "Commerce, Justice, Science, and Related Agencies", 
    "Defense and Military Affairs",	"Energy and Water Development",
    "Financial Services and General Government",
    "Interior and Environment",
    "Labor, Health, Human Services, and Educaiton",
    "Transportation, Housing, and Urban Development",
    "Total Earmarks")


# server.R
shinyServer(
  function(input, output) {
    output$map <- renderPlot({
      if(input$type == "total"){
        incoming_cong <- switch(input$var, 
                                "104th Congress (1995-1997)"=congress_earmarks[,3],
                                "105th Congress (1997-1999)"=congress_earmarks[,4],
                                "106th Congress (1999-2001)"=congress_earmarks[,5], 
                                "107th Congress (2001-2003)"=congress_earmarks[,6], 
                                "108th Congress (2003-2005)"=congress_earmarks[,7], 
                                "109th Congress (2005-2007)"=congress_earmarks[,8], 
                                "110th Congress (2007-2009)"=congress_earmarks[,9], 
                                "111th Congress (2009-2010)"=congress_earmarks[,10],
                                "1995-2010"=congress_earmarks[,11])
        
      }
      else{
        incoming_cong <- switch(input$var, 
                                "104th Congress (1995-1997)"=congress_earmarks[,12],
                                "105th Congress (1997-1999)"=congress_earmarks[,13],
                                "106th Congress (1999-2001)"=congress_earmarks[,14], 
                                "107th Congress (2001-2003)"=congress_earmarks[,15], 
                                "108th Congress (2003-2005)"=congress_earmarks[,16], 
                                "109th Congress (2005-2007)"=congress_earmarks[,17], 
                                "110th Congress (2007-2009)"=congress_earmarks[,18], 
                                "111th Congress (2009-2010)"=congress_earmarks[,19],
                                "1995-2010"=congress_earmarks[,20])
      }
      
      if(input$type == "total"){
        legend.title = paste0("Number of Earmarks")
        
      } 
      else{
        legend.title = paste0("Earmarks per 10,000 people")
        
      }
      earmark_states(incoming_cong,legend.title=legend.title,type=input$type)
    })
    
    # Generate an HTML table view of the data
    output$table <- renderTable({
      table_cong <- switch(input$var, 
                           "104th Congress (1995-1997)"= 104,
                           "105th Congress (1997-1999)"=105,
                           "106th Congress (1999-2001)"= 106, 
                           "107th Congress (2001-2003)" = 107, 
                           "108th Congress (2003-2005)" = 108, 
                           "109th Congress (2005-2007)" = 109, 
                           "110th Congress (2007-2009)" = 110, 
                           "111th Congress (2009-2010)" = 111,
                            "1995-2010"="All")
      subset(congress_table,congress_table$Congress==table_cong)[,c(2:10)]
    })
    
  }
)