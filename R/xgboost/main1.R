# http://xgboost.readthedocs.io/en/latest/R-package/xgboostPresentation.html

library(xgboost)
library(Matrix)

i <- c(1, 3, 4)
j <- c(6, 5, 2)
x <- c(10, 2, 9)
(sm <- sparseMatrix(i = i, j = j, x = x, dims = c(6, 6)))

data("agaricus.train")
data("agaricus.test")
train <- agaricus.train
test <- agaricus.test

str(train)
dim(train$data)
class(train$data)

xgbst <- xgboost(data = train$data,
                 label = train$label,
                 params = list(max.depth = 2,
                               eta = 1,
                               nthread = 2,
                               objective = 'binary:logistic'),
                 nrounds = 5,
                 verbose = 1)
pred <- predict(xgbst, test$data)
sum(as.numeric(pred > 0.5) != test$label)/length(test$label)

dtrain <- xgb.DMatrix(data = train$data, label = train$label)
dtest <- xgb.DMatrix(data = test$data, label = test$label)
watchlist <- list(train=dtrain, test=dtest)

xgbst.ad <- xgb.train(params = list(booster='gbtree',
                                    silent=0,
                                    objective='binary:logistic'),
                      data = dtrain,
                      nrounds = 5,
                      watchlist = watchlist,
                      verbose = 1)
