class MultidimensionalTransdimensionalPrism(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2010, 2, 1)               # Earliest start date for all ETFs in universe 2/1/10
        self.SetEndDate(2020, 6, 30)
        self.SetCash(100000) 
        self.AddEquity("TQQQ", Resolution.Daily)    # 3x QQQ
        self.AddEquity("UBT", Resolution.Daily)     # 3x 20yr Treasury
        self.AddEquity("TNA", Resolution.Daily)     # 3x 10yr Treasury
        self.tkr = ["TQQQ", "UBT", "TNA"]
        
        self.initBenchmarkPrice = None
        self.benchmarkTicker = "SPY"
        self.SetBenchmark(self.benchmarkTicker)
        
        self.rebal = 2                              # Rebalance every 2 weeks
        self.rebalTimer = self.rebal - 1            # Initialize to trigger first week
        self.flag1 = 0                              # Flag to initate trades
        
        # Increment rebalance timer at every week start
        self.Schedule.On(self.DateRules.WeekStart("UBT"), self.TimeRules.AfterMarketOpen("UBT", 50), self.Rebalance)


    def OnData(self, data):
        # If ready to rebalance, set each holding 100% capital
        if self.flag1 == 1:                     
            self.SetHoldings(self.tkr[0], 0.4)
            self.SetHoldings(self.tkr[1], 0.3)
            self.SetHoldings(self.tkr[2], 0.3)
            self.rebalTimer = 0                     # Reset rebalance timer
        self.flag1 = 0    
        
        # Simulate buy and hold the benchmark and plot its daily value
        self.UpdateBenchmarkValue()
        self.Plot('Strategy Equity', self.benchmarkTicker, self.benchmarkValue)
        
        
    def Rebalance(self):
        self.rebalTimer +=1
        if self.rebalTimer == self.rebal:
            self.flag1 = 1
            
   
    def UpdateBenchmarkValue(self):
            
        ''' Simulate buy and hold the Benchmark '''
        
        if self.initBenchmarkPrice is None:
            self.initBenchmarkCash = self.Portfolio.Cash
            self.initBenchmarkPrice = self.Benchmark.Evaluate(self.Time)
            self.benchmarkValue = self.initBenchmarkCash
        else:
            currentBenchmarkPrice = self.Benchmark.Evaluate(self.Time)
            self.benchmarkValue = (currentBenchmarkPrice / self.initBenchmarkPrice) * self.initBenchmarkCash