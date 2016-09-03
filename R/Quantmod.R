library(quantmod)

## https://www.r-bloggers.com/fundamental-and-technical-analysis-of-shares-exercises/


sym <- stockSymbols()
cat(sym$Symbol)

## ex1 Load FB (Facebook) market data from Yahoo and assign it to an xts object SNE.
SNE <- getSymbols(Symbols = 'SNE', env = NULL)


## ex2 Display monthly closing prices of Facebook in 2015.
Cl(to.monthly(SNE["2015::2015-12-31"]))


## ex3 Plot weekly returns of FB in 2016.
plot(weeklyReturn(SNE, subset="2016::"), main="Weekly return of Facebook")


## ex4 Plot a candlestick chart of FB in 2016.
candleChart(SNE, name="SONY", subset = '2016::2016-12-31')


## ex5
## Plot a line chart of FB in 2016.,
## and add boilinger bands and a Relative Strength index to the chart.

chartSeries(SNE, subset="2016::2016-12-31", type="line", name="SONY")
addBBands()
addRSI()


## ex6 Get yesterday’s EUR/USD rate.
getFX('USD/JPY', from=Sys.Date()-1, env = NULL)


## ex7 Get financial data for FB and display it.
SNE.f <- getFin("SNE", env=NULL)
viewFin(SNE.f)


## ex8 Calculate the current ratio for FB for years 2013, 2014 and 2015
SNE.bs <- viewFin(SNE.f, "BS","A")
SNE.bs["Total Current Assets",c("2013-3-31", "2014-3-31", "2015-3-31")]/
    SNE.bs["Total Current Liabilities",c("2013-3-31", "2014-3-31", "2015-3-31")]


## ex9 Based on the last closing price and income statement for 12 months
## ending on December 31th 2015, Calculate the PE ratio for FB
price <- Cl(SNE[NROW(SNE)])
SNE.is <- viewFin(SNE.f, "IS", "a")
EPS <- SNE.is["Diluted Normalized EPS", "2016-03-31"]
price/EPS


## ex10 write a function getROA(symbol, year)
## which will calculate return on asset for given stock symbol and year.
## What is the ROI for FB in 2014.
getROA03 <- function(symbol, year)
{
  symbol.f <- getFin(symbol, env=NULL)
  symbol.ni <- viewFin(symbol.f, "IS", "A")["Net Income", paste(year, sep="", "-03-31")]
  symbol.ta <- viewFin(symbol.f, "BS", "A")["Total Assets", paste(year, sep="", "-03-31")]

  symbol.ni/symbol.ta*100
}

getROA12 <- function(symbol, year)
{
  symbol.f <- getFin(symbol, env=NULL)
  symbol.ni <- viewFin(symbol.f, "IS", "A")["Net Income", paste(year, sep="", "-12-31")]
  symbol.ta <- viewFin(symbol.f, "BS", "A")["Total Assets", paste(year, sep="", "-12-31")]

  symbol.ni/symbol.ta*100
}

getROA12("FB", "2015")

