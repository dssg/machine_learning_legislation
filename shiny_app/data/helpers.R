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
  map('state',col=cols,fill=TRUE,lty = 1, lwd = 1, 
      mar = c(0,0,0,0))
  
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
  
  legend("bottomleft",fill=colors,legend=legend.text,title =legend.title,
         cex=0.75)
  
}
