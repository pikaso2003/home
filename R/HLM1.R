library(rstan)


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


rstan_options(auto_write = TRUE)
options(mc.cores = parallel::detectCores()) 
mlstanDso <- stan_model(file = "Hierachical_Model_for_Loss_Reserving.stan",
                        model_name = "MultiLevelGrowthCurve") 
mlfit <- sampling(mlstanDso, iter=7000, warmup=2000, 
                  thin=2, cores=2, chains=4, seed=1037025002,
                  data = list(N = nrow(dat),
                              cum=dat$cum,
                              origin=dat$origin,
                              n_origin=length(unique(dat$origin)),
                              dev=dat$dev,
                              new_N=nrow(newdat),
                              new_origin=newdat$origin,
                              new_dev=newdat$dev))
print(mlfit, c("mu_ult", "omega", "theta", "sigma_ult", "sigma"),
      probs=c(0.5, 0.75, 0.975))
# Inference for Stan model: MultiLevelGrowthCurve.
# 4 chains, each with iter=7000; warmup=2000; thin=2; 
# post-warmup draws per chain=2500, total post-warmup draws=10000.
# 
#              mean se_mean     sd     50%     75%   97.5% n_eff Rhat
# mu_ult    5350.74    4.74 277.13 5341.67 5527.94 5918.22  3414    1
# omega        1.31    0.00   0.03    1.31    1.33    1.38  3561    1
# theta       47.46    0.05   2.39   47.32   48.95   52.57  2161    1
# sigma_ult  645.15    2.66 197.55  607.11  738.68 1135.91  5528    1
# sigma        2.96    0.00   0.32    2.93    3.16    3.69  7471    1
# 
# Samples were drawn using NUTS(diag_e) at Tue Nov  3 20:25:23 2015.
# For each parameter, n_eff is a crude measure of effective sample size,
# and Rhat is the potential scale reduction factor on split chains (at 
# convergence, Rhat=1).      
ult <- as.data.frame(rstan::extract(mlfit, paste0("ult[", 1:10, "]")))
summary(apply(ult, 1, sum))
#   Min. 1st Qu.  Median    Mean 3rd Qu.    Max. 
#  47120   52360   53630   53710   54950   62710 
rstan::traceplot(mlfit, c("mu_ult", "omega", "theta", "sigma_ult", "sigma"))
stan_dens(mlfit, pars=paste0("ult[", 1:10, "]"), fill="skyblue")

Y_mean <- rstan::extract(mlfit, "Y_mean")
Y_mean_cred <- apply(Y_mean$Y_mean, 2, quantile, c(0.05, 0.95)) 
Y_mean_mean <- apply(Y_mean$Y_mean, 2, mean)
Y_pred <- rstan::extract(mlfit, "Y_pred")
Y_pred_cred <- apply(Y_pred$Y_pred, 2, quantile, c(0.05, 0.95)) 
Y_pred_mean <- apply(Y_pred$Y_pred, 2, mean)
dat2 <- merge(newdat, dat, all=TRUE)
dat2 <- dat2[order(dat2$dev),]
dat2$Y_pred_mean <- Y_pred_mean
dat2$Y_pred_cred5 <- Y_pred_cred[1,]
dat2$Y_pred_cred95 <- Y_pred_cred[2,]
library(lattice)
key <- list(
  rep=FALSE, 
  lines=list(col=c("#00526D", "purple"), type=c("p","l"), pch=1),
  text=list(lab=c("Observation","Mean Estimate")),
  rectangles = list(col=adjustcolor("yellow", alpha.f=0.5), border="grey"),
  text=list(lab="95% Prediction credible interval"))
xyplot( Y_pred_cred5 + Y_pred_cred95 + Y_pred_mean + cum ~ dev | factor(AY), 
        data=dat2, as.table=TRUE,
        xlab="dev", ylab="cum", 
        main="Weibull Growth Curve with Random Effect",
        scales=list(alternating=1), layout=c(5,2), key=key,
        panel=function(x, y){
          n <- length(x)
          k <- n/2
          upper <- y[(k/2+1):k]
          lower <- y[1:(k/2)]
          x <- x[1:(k/2)]
          panel.polygon(c(x, rev(x)), c(upper, rev(lower)),
                        col = adjustcolor("yellow", alpha.f = 0.5), 
                        border = "grey")
          panel.lines(x, y[(k+1):(k+n/4)], col="purple")
          panel.points(x, y[(n*3/4+1):n], lwd=2, col="#00526D")
        })

