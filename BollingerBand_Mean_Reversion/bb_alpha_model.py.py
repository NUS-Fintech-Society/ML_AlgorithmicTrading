from clr import AddReference
AddReference("QuantConnect.Common")
AddReference("QuantConnect.Algorithm")
AddReference("QuantConnect.Algorithm.Framework")
AddReference("QuantConnect.Indicators")

from QuantConnect import *
from QuantConnect.Indicators import *
from QuantConnect.Algorithm import *
from QuantConnect.Algorithm.Framework import *
from QuantConnect.Algorithm.Framework.Alphas import *
from scipy import stats

class BBAlphaModel(AlphaModel):
    def __init__(self,
                 period = 20, 
                 standardDeviation = 3, 
                 resolution = Resolution.Daily):
        
        self.standardDeviation = standardDeviation
        self.maType = MovingAverageType.Simple
        self.period = period
        self.resolution = resolution
        self.symbolData = {}
        resolutionString = Extensions.GetEnumString(resolution, Resolution)
        self.Name = '{}({},{},{})'.format(self.__class__.__name__, standardDeviation, period, resolutionString)

    def Update(self, algorithm, data):
        '''Updates this alpha model with the latest data from the algorithm.
        This is called each time the algorithm receives data for subscribed securities
        Args:
            algorithm: The algorithm instance
            data: The new data available
        Returns:
            The new insights generated'''

        insights = []
        for symbol, symbolData in self.symbolData.items():
            # adds data onto the rolling window
            symbolData.smaWindow.Add(symbolData.SMA.Current.Value)
            
            if not symbolData.IsReady:
                continue

            # computes the linear regression of rolling window to get the trend
            y_axis = []
            x_axis = []
            for interval in range(symbolData.period):
                y_axis.append(symbolData.smaWindow[interval])
                x_axis.append(interval + 1)
            
            x_axis.reverse()
            slope, intercept, r_value, p_value, std_err = stats.linregress(x_axis, y_axis)
            price = symbolData.Security.Price

            # liquidate condition
            # - (1) current price is within 5% of middle band
            if (0.95 * symbolData.BB.MiddleBand.Current.Value) <= price <= (1.05 * symbolData.BB.MiddleBand.Current.Value):
                insights.append(Insight.Price(symbol, timedelta(days = 1), InsightDirection.Flat))

            # buying condition
            # - (1) no downward trend
            # - (2) price dips below lower band
            if (slope > 0) and (price < symbolData.BB.LowerBand.Current.Value):
                insights.append(Insight.Price(symbol, timedelta(days = 1), InsightDirection.Up, confidence=self.CalculateConfidence(slope)))
    
            # selling condition
            # - (1) no upward trend
            # - (2) and exceeds the upper band            
            if (slope < 0) and (price > symbolData.BB.UpperBand.Current.Value):
                insights.append(Insight.Price(symbol, timedelta(days = 1), InsightDirection.Down, confidence=self.CalculateConfidence(slope)))

        return insights

    def OnSecuritiesChanged(self, algorithm, changes):
        '''Event fired each time the we add/remove securities from the data feed
        Args:
            algorithm: The algorithm instance that experienced the change in securities
            changes: The security additions and removals from the algorithm'''

        ## Pops the removed securities from the list
        for removed in changes.RemovedSecurities:
            data = self.symbolData.pop(removed.Symbol, None)
            ## Following is not needed unless manual universe selection was used
            # if data is not None:
            #     algorithm.SubscriptionManager.RemoveConsolidator(removed.Symbol, data.Consolidator)

        ## Append the added securities onto the list
        for added in changes.AddedSecurities:
            symbolData = self.symbolData.get(added.Symbol)
            bb = algorithm.BB(added.Symbol, self.period, self.standardDeviation, self.maType, self.resolution)
            sma = algorithm.SMA(added.Symbol, self.period, self.resolution)
            self.symbolData[added.Symbol] = SymbolData(added, bb, sma, self.period)

    def CalculateConfidence(self, gradient):
        if abs(gradient) > 1:
            return 1
        return abs(gradient)
    
class SymbolData:
    def __init__(self, security, bb, sma, period):
        self.Security = security
        self.Symbol = security.Symbol
        self.BB = bb
        self.SMA = sma
        self.period = period
        self.smaWindow = RollingWindow[float](period)
        
    @property
    def IsReady(self):
        return self.BB.IsReady and self.SMA.IsReady