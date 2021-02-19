import math
class BenchmarkPlotTemplateAlgorithm(QCAlgorithm):

    def Initialize(self):

        self.SetStartDate(2012, 1, 1)
        self.SetCash(100000)
        # select a ticker as benchmark (will plot Buy&Hold of this benchmark)
        
        
        # Diversification through ETFs
        self.ticker = 'TNA' # 3x small cap
        self.symbol = self.AddEquity(self.ticker, Resolution.Daily).Symbol
        self.benchmarkTicker = 'SPY' # QQQ
        self.SetBenchmark(self.benchmarkTicker)
        self.initBenchmarkPrice = None

        self.rsi = self.RSI(self.ticker, 3, Resolution.Daily)
        self.kch = self.KCH(self.ticker, 21, 1, MovingAverageType.Exponential, Resolution.Daily)
        self.rocp = self.ROCP(self.ticker, 50, Resolution.Daily)
        self.sma = self.SMA(self.ticker, 50, Resolution.Daily)
        self.SetWarmUp(timedelta(20))
        self.holdings = 0


    def OnData(self, slice):
        
        price = self.Securities[self.symbol].Close

        # self.Debug(self.bb.LowerBand.Current.Value > price)
        # Trial and error to get the best value
        if (self.holdings <= 0 and self.rsi.IsReady and self.rsi.Current.Value < 12):
            stopLoss = self.StopMarketOrder(self.symbol, 10, price * 0.98)
            self.SetHoldings(self.symbol, 1.0)
            self.holdings = 1
            
        elif (self.holdings > 0 and self.rsi.Current.Value > 85):
            self.Debug("Dumped >> " + str(self.Securities[self.symbol].Price))
            self.Liquidate(self.symbol)   
            self.SetHoldings(self.symbol, 0.0)
            self.holdings = 0
        
            
        # Simulate buy and hold the benchmark and plot its daily value
        self.UpdateBenchmarkValue()
        self.Plot('Strategy Equity', self.benchmarkTicker, self.benchmarkValue)
        

    def UpdateBenchmarkValue(self):
            
        ''' Simulate buy and hold the Benchmark '''
        
        if self.initBenchmarkPrice is None or self.initBenchmarkPrice == 0:
            self.initBenchmarkCash = self.Portfolio.Cash
            self.initBenchmarkPrice = self.Benchmark.Evaluate(self.Time)
            self.benchmarkValue = self.initBenchmarkCash
        else:
            currentBenchmarkPrice = self.Benchmark.Evaluate(self.Time)
            self.benchmarkValue = (currentBenchmarkPrice / self.initBenchmarkPrice) * self.initBenchmarkCash