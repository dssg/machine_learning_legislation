library(maps)
library(maptools)
library(mapdata)

library(RColorBrewer) 
library(classInt) 


round2 <- function(x){
  return(round(x,2))
}
  

earmark_states <- function(congress,legend.title,type){
  
  ## render the map ## 
  intervals <- 5
  colors <- brewer.pal(intervals, "Blues")  ## choosing the colors 
  brks <- classIntervals(congress, n=intervals) 
  brks <- brks$brks
  cols = colors[findInterval(congress, brks, all.inside=TRUE
  )]
  n = length(cols)
  cols_ak = cols[1]
  cols_hi = cols[2]
  cols_rest = cols[3:n]
  
  if(type=='total'){
    brks <- as.integer(brks)
    legend.text <- c(paste0(brks[1], "-", brks[2]),
                     paste0(brks[2]+1, "-", brks[3]),
                     paste0(brks[3]+1, "-", brks[4]),
                     paste0(brks[4] +1, "-", brks[5]),
                     paste0("Greater than ", brks[5]))
  }
  else{
    brks <- round2(brks)
    legend.text <- c(paste0(brks[1], "-", brks[2]),
                     paste0(brks[2], "-", brks[3]),
                     paste0(brks[3], "-", brks[4]),
                     paste0(brks[4], "-", brks[5]),
                     paste0("Greater than ", brks[5]))
  }
  
  
  
  layout(rbind(c(0,2,0,0,0,2),c(1,0,1,3,3,2),c(1,3.5,1,3,3,2)),
        heights=c(.8, 0, .3),widths=c(0, 1, 0, 0, 1, 2))
  
  par(mar=rep(0,4))
  par(oma=c(8,rep(0, 3)))
  layout.show(3)
  map("world2Hires", "USA:Alaska",col=cols_ak,fill=TRUE)
  par(mar=rep(0,4))
  map("state",col=cols_rest,fill=TRUE)
  if(type=='total'){
    legend("bottomright",fill=colors,legend=legend.text,title =legend.title,
           cex=.95)
  }
  else{
    legend("bottomright",fill=colors,legend=legend.text,title =legend.title,
           cex=.9)
  }
  
  par(mar=rep(0,4))
  map("world2Hires", "Hawaii",col=cols_hi,fill=TRUE,myborder = 0)
  

  
}
