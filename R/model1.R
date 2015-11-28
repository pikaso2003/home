library(rstan)
set.seed(123)


stancode <-'

  data{
    int N;
    real T[N];
    real Y[N];
  }

  parameters{
    real a;
    real b;
    real<lower=0> sig;
  }

  model{
    for(i in 1:N){
      Y[i]~normal(b*T[i]+a,sig);
    }
    a~normal(0,100);
    b~normal(0,100);
    sig~uniform(0,10000);
  }

'

N<-20
a<-0.5
b<-3
T<-1:N/10
Y<-rnorm(n = N,mean = b*T+a,sd = 1)
data<-list(N=N,T=T,Y=Y)

stanmodel <- stan_model(model_code = stancode)
fit <- sampling(stanmodel,
                data=data,
                chains=4,
                init=function(){
                  list(a=runif(1,-1,1),b=runif(1,-1,1),sig=1)
                },
                iter=1000
                )

write.table(data.frame(summary(fit)$summary),
            file = 'model1_fit_summary.txt',sep = '\t',quote = FALSE)

pdf(file = 'traceplot_model1.pdf',width = 600/72,height = 600/72)
traceplot(fit)
dev.off()

