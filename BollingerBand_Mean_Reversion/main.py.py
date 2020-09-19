from universe_selection import FactorUniverseSelectionModel
from Risk.MaximumDrawdownPercentPerSecurity import MaximumDrawdownPercentPerSecurity
from bb_alpha_model import BBAlphaModel
class TradingBot(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2016, 1, 1)
        self.SetCash(100000)
        
        self.UniverseSettings.Resolution = Resolution.Daily
        self.AddUniverseSelection(FactorUniverseSelectionModel())
        
        ## Add warmup here
        self.SetWarmUp(timedelta(20))

        ## Alpha model
        self.AddAlpha(BBAlphaModel())

        ## Portfolio construction model
        self.SetPortfolioConstruction(EqualWeightingPortfolioConstructionModel())

        ## Risk management model
        self.SetRiskManagement(MaximumDrawdownPercentPerSecurity(0.2))

        ## Execution model
        self.SetExecution(ImmediateExecutionModel())