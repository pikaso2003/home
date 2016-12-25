# Hybrid Model Test
# Hirayu 25 Dec 2016
# NOTE1 : cross validation computation takes a lot of time. (not paralleled)
# NOTE2 : nnetar is poor estimator should be excluded, due to test I included this methodology.

library(forecastHybrid) # new package inherits methods from forecast
library(ggplot2)
library(scales)
library(tidyverse)


citation("forecastHybrid")


# load data from economics in ggplot2 package
uempmed <- ts(data = economics$uempmed,
              start = c(1967, 7),
              frequency = 12,
              class = 'ts')
cat('BoxCox lambda : ', BoxCox.lambda(uempmed)) # close to zero -> log transformation


# lambada = BoxCox lambda
# you can include external regressor explanatory variables via a.args, e.args and others.
# type "?hybridModel" for more detail.
hm1 <- hybridModel(y = uempmed, models = c('aefnst'),
                   lambda = BoxCox.lambda(uempmed),
                   a.args = NULL,
                   weights = 'cv.errors',
                   errorMethod = c('RMSE', 'MAE', 'MASE'),
                   verbose = TRUE)


f1 <- forecast(hm1, 24)
ap1 <- autoplot(f1) +
    ggtitle("Forecast median length of unemployment",
            subtitle = "Six component models, weights chosen by cross-validation") +
    labs(y = "Weeks", x = "")
plot(ap1)


par(mfrow = c(3, 2), bty = "l", cex = 0.8)
plot(f1$thetam)
plot(f1$ets)
plot(f1$stlm)
plot(f1$auto.arima)
plot(f1$nnetar)
plot(f1$tbats)
