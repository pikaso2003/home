glmModelPlot <- function(x, y, xlim,ylim, meanPred,  LwPred, UpPred, 
                         plotData, main=NULL){
  ## Based on code by Arthur Charpentier:
  ## http://freakonometrics.hypotheses.org/9593
  par(mfrow=c(1,1))
  n <- 2
  N <- length(meanPred)
  zMax <- max(unlist(sapply(plotData, "[[", "z")))*1.5
  mat <- persp(xlim, ylim, matrix(0, n, n), main=main,
               zlim=c(0, zMax), theta=-30, 
               ticktype="detailed",box=FALSE)
  C <- trans3d(x, UpPred, rep(0, N),mat)
  lines(C, lty=2)
  C <- trans3d(x, LwPred, rep(0, N), mat)
  lines(C, lty=2)
  C <- trans3d(c(x, rev(x)), c(UpPred, rev(LwPred)),
               rep(0, 2*N), mat)
  polygon(C, border=NA, col=adjustcolor("yellow", alpha.f = 0.5))
  C <- trans3d(x, meanPred, rep(0, N), mat)
  lines(C, lwd=2, col="grey")
  C <- trans3d(x, y, rep(0,N), mat)
  points(C, lwd=2, col="#00526D")
  for(j in N:1){
    xp <- plotData[[j]]$x
    yp <- plotData[[j]]$y
    z0 <- plotData[[j]]$z0
    zp <- plotData[[j]]$z
    C <- trans3d(c(xp, xp), c(yp, rev(yp)), c(zp, z0), mat)
    polygon(C, border=NA, col="light blue", density=40)
    C <- trans3d(xp, yp, z0, mat)
    lines(C, lty=2)
    C <- trans3d(xp, yp, zp, mat)
    lines(C, col=adjustcolor("blue", alpha.f = 0.5))
  }
}

stanLogTransformed <-"
data {
int N;
vector[N] units;
vector[N] temp;
}
transformed data {  
vector[N] log_units;        
log_units <- log(units);
}
parameters {
real alpha;
real beta;
real tau;
}
transformed parameters {
real sigma;
sigma <- 1.0 / sqrt(tau);
}
model{
// Model
log_units ~ normal(alpha + beta * temp, sigma);
// Priors
alpha ~ normal(0.0, 1000.0);
beta ~ normal(0.0, 1000.0);
tau ~ gamma(0.001, 0.001);
}
generated quantities{
vector[N] units_pred;
for(i in 1:N)
units_pred[i] <- exp(normal_rng(alpha + beta * temp[i], sigma));
}
"

temp <- c(11.9,14.2,15.2,16.4,17.2,18.1,18.5,19.4,22.1,22.6,23.4,25.1)
units <- c(185L,215L,332L,325L,408L,421L,406L,412L,522L,445L,544L,614L)
icecream <- data.frame(temp,units)
library(rstan)

stanmodel <- stan_model(model_code = stanLogTransformed)
fit <- sampling(stanmodel,
                data = list(N=length(units),
                            units=units,
                            temp=temp),
                iter = 1000, warmup=200)
stanoutput <- extract(fit)

## Extract generated posterior predictive quantities
Sims <- data.frame(stanoutput[["units_pred"]])

## Calculate summary statistics
SummarySims <- apply(Sims, 2, summary)
colnames(SummarySims) <- paste(icecream$temp,"oC")

## Extract estimated parameters
(parms <- sapply(stanoutput[c("alpha", "beta", "sigma")], mean))
##      alpha       beta      sigma 
## 4.41543439 0.08186099 0.14909969

## Use parameters to predict median and mean
PredMedian <- exp(parms['alpha'] + parms['beta']*temp)
PredMean <- exp(parms['alpha'] + parms['beta']*temp + 0.5*parms['sigma']^2)

## Compare predictions based on parameters with simulation statistics
round(rbind(SummarySims, PredMedian, PredMean),1)
##            11.9 oC 14.2 oC 15.2 oC 16.4 oC 17.2 oC 18.1 oC
## Min.         116.1   101.6   123.6   140.6   164.0   209.5
## 1st Qu.      196.2   237.6   259.1   285.7   307.5   329.7
## Median       218.5   263.7   286.1   318.3   338.8   364.1
## Mean         221.9   267.2   290.2   321.0   342.6   369.3
## 3rd Qu.      243.5   292.2   317.5   350.4   372.7   403.4
## Max.         418.7   542.4   740.9   688.0   736.0   778.5
## PredMedian   218.5   264.1   286.8   316.5   338.1   364.1
## PredMean     220.9   267.0   289.9   320.0   341.8   368.1
##            18.5 oC 19.4 oC 22.1 oC 22.6 oC 23.4 oC 25.1 oC
## Min.         198.9   177.2   241.9   271.6   249.1   337.0
## 1st Qu.      339.6   368.7   456.5   476.9   508.7   577.9
## Median       375.2   405.2   506.2   527.4   562.9   645.2
## Mean         379.3   410.4   512.2   534.3   572.1   653.7
## 3rd Qu.      412.2   446.0   557.5   582.6   625.4   718.2
## Max.         678.1   984.9   944.6  1054.0  1282.0  1358.0
## PredMedian   376.3   405.3   506.2   527.4   563.4   648.0
## PredMean     380.4   409.6   511.6   533.1   569.5   655.0

meanPred <- apply(Sims, 2, mean)
LwPred <- apply(Sims, 2, quantile, 0.05)
UpPred <- apply(Sims, 2, quantile, 0.95)
xlim <- c(min(icecream$temp)*0.95, max(temp)*1.05)
ylim <- c(floor(min(units)*0.95),
          ceiling(max(units)*1.05))
plotStan <- lapply(
  seq(along=temp),
  function(i){
    stp = 251
    d = density(Sims[, i, ], n=stp)
    y = seq(ylim[1], ylim[2], length=stp)
    z = approx(d$x, d$y, y)$y 
    z[is.na(z)] <- 0
    x = rep(icecream$temp[i], stp)
    z0 = rep(0, stp)
    return(list(x=x, y=y, z0=z0, z=z))
  }
)
# https://gist.github.com/mages/dedfb0d97082f0f0e0ab
glmModelPlot(x=temp, y=units,
             xlim=xlim, ylim=ylim,
             meanPred = meanPred, LwPred = LwPred,
             UpPred = UpPred, plotData = plotStan,
             main = "Log-transformed LM prediction")

