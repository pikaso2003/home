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
library(nlme)
start.vals <- c(ult = 5000, omega = 1.4, theta = 45)
w1 <- nlme(cum ~ ult*(1 - exp(-(dev/theta)^omega)),
           fixed = list(ult~1, omega~1, theta ~ 1),
           random = ult ~ 1 | origin,
           weights = varPower(fixed=.5),
           data=dat, start = start.vals)
summary(w1)
# Nonlinear mixed-effects model fit by maximum likelihood
#   Model: cum ~ ult * (1 - exp(-(dev/theta)^omega)) 
# Data: dat 
#        AIC      BIC    logLik
#   725.7576 735.7943 -357.8788
# 
# Random effects:
#  Formula: ult ~ 1 | origin
#              ult Residual
# StdDev: 543.0296 2.955047
# 
# Variance function:
# Structure: Power of variance covariate
# Formula: ~fitted(.) 
# Parameter estimates:
# power 
#   0.5 
# Fixed effects: list(ult ~ 1, omega ~ 1, theta ~ 1) 
#          Value Std.Error DF  t-value p-value
# ult   5306.605 263.19680 43 20.16212       0
# omega    1.306   0.03394 43 38.49663       0
# theta   46.638   2.42193 43 19.25637       0
#  Correlation: 
#       ult    omega 
# omega -0.430       
# theta  0.668 -0.772
#
# Standardized Within-Group Residuals:
#         Min          Q1         Med          Q3         Max 
# -1.47331314 -0.67337317 -0.04756236  0.40584781  2.94400230 
#
# Number of Observations: 55
# Number of Groups: 10
library(lattice)
xyplot(cum ~ dev | factor(AY), data=dat, layout=c(5,2),
       main="Hierachical Growth Curve Model",
       as.table=TRUE, xlim=range(newdat$dev),
       scales=list(alternating=1),
       key = list(space="top", columns=2,
                  text=list(labels=c("observation", "prediction")),
                  line=FALSE, points=list(pch=c(1,19), col=c(2,1))),
       panel=function(x, y, subscripts, ...){
         panel.xyplot(x, y, t="b", pch=1, cex=0.5, col=2)
         panel.xyplot(dat$dev[subscripts], 
                      predict(w1, newdata=dat[subscripts,]),
                      t="b", pch=19, cex=0.5, col=1)
       })