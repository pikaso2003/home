library(MASS)
library(flexsurv)


# N <- 10000
# from <- data.frame(n=1:N)
# from$c <- rgamma(N, shape=2, rate=3)
# from$w <- rweibull(N, shape=1.5, scale=4)
# from$g <- rgengamma(N, mu = 1.5, sigma=3, Q=4)
# from <- from[,-1]

erup <- read.csv('eruption_data.csv',header = FALSE,col.names = 'x')
data <- erup$x

fit.data <- fitdistr(data,"weibull",start = list(shape=0.693,scale=47.9))
print(fit.data)
print(fit.data$vcov)
# shape=0.69325076,scale=47.93199351



prob.df <- data.frame(matrix(nrow = sample_n,ncol=1))
colnames(prob.df) <- c('prob')
year <- 161
sample_n=50000
for (i in 1:sample_n){
    temp_coeff <- mvrnorm(n=1,mu = fit.data$estimate,Sigma = fit.data$vcov)
    temp_alpha <- temp_coeff[1]
    temp_sigma <- temp_coeff[2]
    prob.df[i,] <- 1- exp(-(year+1)/temp_sigma)^temp_alpha/exp(-year/temp_sigma)^temp_alpha
}

output.df <- prob.df[order(prob.df$prob),]
output.df <- output.df[output.df>0]
ggplot.df <- data.frame(value=output.df)
g <- ggplot(ggplot.df,aes(x=value))
g <- g+geom_histogram(alpha=0.5,binwidth = 0.0001,color='orange')
plot(g)
write.csv(output.df,file = 'eruption.csv')
mean(output.df)

