library(cvTools)
library(doParallel)

# 10 fold CV
folds <- cvFolds(NROW(iris), K=10)
foreach(i=1:10) %dopar% {
  train <- iris[folds$subsets[folds$which != i], ]
  validation <- iris[folds$subsets[folds$which == i], ]
  # Write modeling and evaluation code here.
  # In this example, I'm just returning training and validation data sets
  # for illustrative purpose.
  return(list(train=train, validation=validation))
}
