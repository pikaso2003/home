library(actuar)
library(ChainLadder)
library(tweedie)
library(xlsx)
library(ggplot2)
library(reshape2)


mycsv <- "data.csv"
tri <- read.csv(mycsv, header = FALSE)
tri <- as.triangle(as.matrix(tri))
