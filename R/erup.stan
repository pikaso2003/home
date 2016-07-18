data{
    int N;
    real x[N];
}

parameters{
    real<lower=0> alpha;
    real<lower=0> sigma;
}

model{
    for (i in 1:N)
        x[i]~weibull(alpha,sigma);
        alpha~uniform(0,1000);
        sigma~uniform(0,1000);
}
