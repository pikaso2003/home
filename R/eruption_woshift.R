library(rstan)
library(actuar)
library(ggplot2)
library(coda)
library(reshape2)


erup <- read.csv('eruption_data.csv',header = FALSE,col.names = 'x')

# Hierarchical Bayesian method

erup.data <- list(
    N=nrow(erup),
    x=erup$x
)

stanmodel.erup <- stan_model(file='erup.stan')
fit.erup <- sampling(stanmodel.erup,data=erup.data,iter=60000,warmup=1000,seed=1,thin=5,chains=6)
rstan::traceplot(fit.erup,inc_warm=TRUE)
erup.alpha <- extract(fit.erup)$alpha
erup.sigma <- extract(fit.erup)$sigma
fit.coda <- mcmc.list(lapply(1:ncol(fit.erup),function(x) mcmc(as.array(fit.erup)[,x,])))
plot(fit.coda)



# sigma : 47.93199351
# alpha : 0.69325076


prob.df <- data.frame(matrix(nrow = sample_n,ncol=1))
colnames(prob.df) <- c('prob')
year <- 161
sample_n=50000
for (i in 1:sample_n){
    temp_n <- sample(seq(1,dim(erup.alpha),1),1)
    temp_alpha <- erup.alpha[temp_n]
    temp_sigma <- erup.sigma[temp_n]
    prob.df[i,] <- 1- exp(-(year+1)/temp_sigma)^temp_alpha/exp(-year/temp_sigma)^temp_alpha
}

# Print(erup.alpha,erup.sigma)
print(mean(erup.alpha))
print(var(erup.alpha))
print(mean(erup.sigma))
print(var(erup.sigma))
print(mean(prob.df$prob))
calc.mean <- mean(prob.df$prob)

output.df <- prob.df[order(prob.df$prob),]
ggplot.df <- data.frame(value=output.df)
g <- ggplot(ggplot.df,aes(x=value))
g <- g+geom_histogram(alpha=0.5,binwidth = 0.0001,color='orange')
plot(g)
write.csv(output.df,file = 'eruoption.csv')
mean(output.df)
