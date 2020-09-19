from QuantConnect.Data.UniverseSelection import * 
from Selection.FundamentalUniverseSelectionModel import FundamentalUniverseSelectionModel

class FactorUniverseSelectionModel(FundamentalUniverseSelectionModel):
    
    def __init__(self):
        super().__init__(True, None, None)

    def SelectCoarse(self, algorithm, coarse):
        universe = self.FilterDollarVolume(coarse)
        return [c.Symbol for c in universe]

    def SelectFine(self, algorithm, fine):
        universe = self.FilterFactor(fine)
        return [f.Symbol for f in universe]

    def FilterDollarVolume(self, coarse):
        sorted_dollar_volume = sorted([c for c in coarse if c.HasFundamentalData], key=lambda c: c.DollarVolume, reverse=True)
        return sorted_dollar_volume[:1000]

    def FilterFactor(self, fine):
        filter_factor = sorted(fine, key=lambda f: f.ValuationRatios.CashReturn, reverse=True)
        return filter_factor[:40]