# -*- coding: utf-8 -*-
"""
Created on Sat Dec 06 13:40:42 2014

@author: Huapu (Peter) Pan
"""

######################## Global Market Rotation Class
class GlobalMarketRotation(object):
    def __init__(self, factorPerformance = 0.8, factorVolatility = 0.2,
                 look_back = 63, secList = [], DEBUG = False):
        self.factorPerformance = factorPerformance
        self.factorVolatility = factorVolatility
        self.look_back = look_back
        self.secList = secList
        self.DEBUG = DEBUG
        
    def getBestStock(self):
        historical_prices = history(self.look_back,'1d','price')[self.secList]
        historical_returns = historical_prices.pct_change().dropna()
        performances = historical_returns.sum()
        volatilities = historical_returns.std() * np.sqrt(252)
        
        # Determine min/max of each.  NOTE: volatility is switched
        # since a low volatility should be weighted highly.
        maxP, minP = performances.max(), performances.min()
        minV, maxV = volatilities.max(), volatilities.min()
        
        # Normalize the performance and volatility values to a range
        # between [0..1] then rank them based on a 70/30 weighting.
        stockRanks = {sec: 0.0 for sec in self.secList}
        for s in performances.index:
            p = (performances[s] - minP) / (maxP - minP)
            v = (volatilities[s] - minV) / (maxV - minV)
            
            if self.DEBUG is True:
                print('[%s] p %s, v %s' % (s, p, v))
                print('[%s] perf %s, vol %s' % (s, performances[s], volatilities[s]))
                
            pFactor = self.factorPerformance
            vFactor = self.factorVolatility
           
            if np.isnan(p) or np.isnan(v):
                rank = None 
            else:
                rank = (p * pFactor) + (v * vFactor)
            
            if rank is not None:
                stockRanks[s] = rank
    
        bestStock = max(stockRanks, key=stockRanks.get)
        if len(stockRanks) > 0:
            if self.DEBUG is True and len(stockRanks) < len(self.secList):
                print('FEWER STOCK RANKINGS THAN IN STOCK BASKET!')
            if self.DEBUG is True:
                for s in sorted(stockRanks, key=stockRanks.get, reverse=True):
                    print('RANK [%s] %s' % (s, stockRanks[s]))
                    
            bestStock = max(stockRanks, key=stockRanks.get)
        else:
            if self.DEBUG is True:
                print('NO STOCK RANKINGS FOUND IN BASKET; BEST STOCK IS: NONE')
            
        return bestStock
    