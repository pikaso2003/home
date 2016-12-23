library(ROCR)
library(caTools)
library(caret)
library(plotly)

data("GermanCredit")
df1 <-  GermanCredit
df1$Class <- ifelse(df1$Class == "Bad", 1, 0)

set.seed(100)
spl <- sample.split(df1$Class, SplitRatio = 0.7)
Train1 <- df1[spl == TRUE, ]
Test1 <- df1[spl == FALSE, ]
model1 <- glm(Class~., data = Train1, family = binomial)
pred1 <- predict(model1, Test1)
table(Test1$Class, pred1 > 0.5)

pred1.factor <- ifelse(pred1 > 0.5, 1, 0)
confusionMatrix(data = pred1.factor,
                reference = Test1$Class)


ROCRpred1 <- prediction(pred1, Test1$Class)
ROCRperf1 <- performance(ROCRpred1, "tpr", "fpr")
ROCRpred1.df <- data.frame(Cutoff = unlist(ROCRpred1@cutoffs),
                           TP = unlist(ROCRpred1@tp),
                           FP = unlist(ROCRpred1@fp),
                           FN = unlist(ROCRpred1@fn),
                           TN = unlist(ROCRpred1@tn),
                           TPR = unlist(ROCRperf1@y.values),
                           FPR = unlist(ROCRperf1@x.values))
p1 <- ggplot(data = ROCRpred1.df) +
    geom_line(mapping = aes(x = FPR, y = TPR), col = brocolors('crayon')['Razzmatazz'])

ggplotly(p1)
