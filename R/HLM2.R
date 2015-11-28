# Read data
url <- "https://raw.githubusercontent.com/mages/diesunddas/master/Data/ClarkTriangle.csv"
dat <- read.csv(url)
# Relabel accident years
dat$origin <- dat$AY-min(dat$AY)+1
dat <- dat[order(dat$dev),]
# Add future dev years
nyears <- 12
newdat <- data.frame(
  origin=rep(1:10, each=nyears),
  AY=rep(sort(unique(dat$AY)), each=nyears),  
  dev=rep(seq(from=6, to=nyears*12-6, by=12), 10)
)
newdat <- merge(dat, newdat, all=TRUE)
newdat <- newdat[order(newdat$dev),]

