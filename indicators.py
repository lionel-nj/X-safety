#! /usr/bin/env python
'''Class for indicators, temporal indicators, and safety indicators'''

from matplotlib.pyplot import plot, ylim
from numpy import arange, floor, mean
from scipy import percentile

from trafficintelligence import moving
from trafficintelligence.utils import LCSS as utilsLCSS


def multivariateName(indicatorNames):
    return '_'.join(indicatorNames)


# need for a class representing the indicators, their units, how to print them in graphs...
class TemporalIndicator(object):
    '''Class for temporal indicators
    i.e. indicators that take a value at specific instants

    values should be
    * a dict, for the values at specific time instants
    * or a list with a time interval object if continuous measurements

    it should have more information like name, unit'''

    def __init__(self, name, values, timeInterval=None, maxValue=None):
        self.name = name
        if timeInterval is None:
            self.values = values
            instants = sorted(self.values.keys())
            if len(instants) > 0:
                self.timeInterval = moving.TimeInterval(instants[0], instants[-1])
            else:
                self.timeInterval = moving.TimeInterval()
        else:
            assert len(values) == timeInterval.length()
            self.timeInterval = timeInterval
            self.values = {}
            for i in range(int(round(self.timeInterval.length()))):
                self.values[self.timeInterval[i]] = values[i]
        self.maxValue = maxValue

    def __len__(self):
        return len(self.values)

    def empty(self):
        return len(self.values) == 0

    def __getitem__(self, t):
        'Returns the value at time t'
        return self.values.get(t)

    def getIthValue(self, i):
        sortedKeys = sorted(self.values.keys())
        if 0 <= i < len(sortedKeys):
            return self.values[sortedKeys[i]]
        else:
            return None

    def __iter__(self):
        self.iterInstantNum = 0  # index in the interval or keys of the dict
        return self

    def __next__(self):
        if self.iterInstantNum >= len(self.values):  # (self.timeInterval and self.iterInstantNum>=self.timeInterval.length())\
            #     or (self.iterInstantNum >= self.values)
            raise StopIteration
        else:
            self.iterInstantNum += 1
            return self.getIthValue(self.iterInstantNum - 1)

    def getTimeInterval(self):
        return self.timeInterval

    def getName(self):
        return self.name

    def getValues(self, withNone=True):
        result = [self.__getitem__(t) for t in self.timeInterval]
        if withNone:
            return result
        else:
            return [x for x in result if x is not None]

    def getInstants(self):
        return list(self.values.keys())

    def plot(self, options='', xfactor=1., yfactor=1., timeShift=0, **kwargs):
        if self.getTimeInterval().length() == 1:
            marker = 'o'
        else:
            marker = ''
        time = sorted(self.values.keys())
        plot([(x + timeShift) / xfactor for x in time], [self.values[i] / yfactor for i in time], options + marker, **kwargs)
        if self.maxValue:
            ylim(ymax=self.maxValue)

    @classmethod
    def createMultivariate(cls, indicators):
        '''Creates a new temporal indicator where the value at each instant is a list
        of the indicator values at the instant, in the same order
        the time interval will be the union of the time intervals of the indicators
        name is concatenation of the indicator names'''
        if len(indicators) < 2:
            print('Error creating multivariate indicator with only {} indicator'.format(len(indicators)))
            return None

        timeInterval = moving.TimeInterval.unionIntervals([indic.getTimeInterval() for indic in indicators])
        values = {}
        for t in timeInterval:
            tmpValues = [indic[t] for indic in indicators]
            uniqueValues = set(tmpValues)
            if len(uniqueValues) >= 2 or uniqueValues.pop() is not None:
                values[t] = tmpValues
        return cls(multivariateName([indic.name for indic in indicators]), values)


# TODO static method avec class en parametre pour faire des indicateurs agrege, list par instant

def l1Distance(x, y):  # lambda x,y:abs(x-y)
    if x is None or y is None:
        return float('inf')
    else:
        return abs(x - y)


def multiL1Matching(x, y, thresholds, proportionMatching=1.):
    n = 0
    nDimensions = len(x)
    for i in range(nDimensions):
        if l1Distance(x[i], y[i]) <= thresholds[i]:
            n += 1
    return n >= nDimensions * proportionMatching


class LCSS(utilsLCSS):
    '''Adapted LCSS class for indicators, same pattern'''

    def __init__(self, similarityFunc, delta=float('inf'), minLength=0, aligned=False, lengthFunc=min):
        utilsLCSS.__init__(self, similarityFunc=similarityFunc, delta=delta, aligned=aligned, lengthFunc=lengthFunc)
        self.minLength = minLength

    def checkIndicator(self, indicator):
        return indicator is not None and len(indicator) >= self.minLength

    def compute(self, indicator1, indicator2, computeSubSequence=False):
        if self.checkIndicator(indicator1) and self.checkIndicator(indicator2):
            return self._compute(indicator1.getValues(), indicator2.getValues(), computeSubSequence)
        else:
            return 0

    def computeNormalized(self, indicator1, indicator2, computeSubSequence=False):
        if self.checkIndicator(indicator1) and self.checkIndicator(indicator2):
            return self._computeNormalized(indicator1.getValues(), indicator2.getValues(), computeSubSequence)
        else:
            return 0.

    def computeDistance(self, indicator1, indicator2, computeSubSequence=False):
        if self.checkIndicator(indicator1) and self.checkIndicator(indicator2):
            return self._computeDistance(indicator1.getValues(), indicator2.getValues(), computeSubSequence)
        else:
            return 1.


class SeverityIndicator(TemporalIndicator):
    '''Class for severity indicators
    field mostSevereIsMax is True
    if the most severe value taken by the indicator is the maximum'''

    def __init__(self, name, values, timeInterval=None, mostSevereIsMax=True, maxValue=None):
        TemporalIndicator.__init__(self, name, values, timeInterval, maxValue)
        self.mostSevereIsMax = mostSevereIsMax

    def getMostSevereValue(self, minNInstants=None, centile=None):
        '''if there are more than minNInstants observations,
        returns either the average of these maximum values
        or if centile is not None the n% centile from the most severe value

        eg for TTC, centile = 15 returns the 15th centile (value such that 15% of observations are lower)'''
        values = list(self.values.values())
        if centile is not None:
            if self.mostSevereIsMax:
                c = 100 - centile
            else:
                c = centile
            return percentile(values, c)
        elif minNInstants is not None and minNInstants <= self.__len__():
            values = sorted(values, reverse=self.mostSevereIsMax)  # inverted if most severe is max -> take the first values
            return mean(values[:minNInstants])
        else:
            return None

    def getInstantOfMostSevereValue(self):
        '''Returns the instant at which the indicator reaches its most severe value'''
        if self.mostSevereIsMax:
            return max(self.values, key=self.values.get)
        else:
            return min(self.values, key=self.values.get)


# functions to aggregate discretized maps of indicators
# TODO add values in the cells between the positions (similar to discretizing vector graphics to bitmap)

def indicatorMap(indicatorValues, trajectory, squareSize):
    '''Returns a dictionary
    with keys for the indices of the cells (squares)
    in which the trajectory positions are located
    at which the indicator values are attached

    ex: speeds and trajectory'''

    assert len(indicatorValues) == trajectory.length()
    indicatorMap = {}
    for k in range(trajectory.length()):
        p = trajectory[k]
        i = floor(p.x / squareSize)
        j = floor(p.y / squareSize)
        if (i, j) in indicatorMap:
            indicatorMap[(i, j)].append(indicatorValues[k])
        else:
            indicatorMap[(i, j)] = [indicatorValues[k]]
    for k in indicatorMap:
        indicatorMap[k] = mean(indicatorMap[k])
    return indicatorMap


# def indicatorMapFromPolygon(value, polygon, squareSize):
#     '''Fills an indicator map with the value within the polygon
#     (array of Nx2 coordinates of the polygon vertices)'''
#     points = []
#     for x in arange(min(polygon[:,0])+squareSize/2, max(polygon[:,0]), squareSize):
#         for y in arange(min(polygon[:,1])+squareSize/2, max(polygon[:,1]), squareSize):
#             points.append([x,y])
#     inside = nx.points_inside_poly(array(points), polygon)
#     indicatorMap = {}
#     for i in range(len(inside)):
#         if inside[i]:
#             indicatorMap[(floor(points[i][0]/squareSize), floor(points[i][1]/squareSize))] = 0
#     return indicatorMap

def indicatorMapFromAxis(value, limits, squareSize):
    '''axis = [xmin, xmax, ymin, ymax] '''
    indicatorMap = {}
    for x in arange(limits[0], limits[1], squareSize):
        for y in arange(limits[2], limits[3], squareSize):
            indicatorMap[(floor(x / squareSize), floor(y / squareSize))] = value
    return indicatorMap


def combineIndicatorMaps(maps, squareSize, combinationFunction):
    '''Puts many indicator maps together
    (averaging the values in each cell
    if more than one maps has a value)'''
    indicatorMap = {}
    for m in maps:
        for k, v in m.items():
            if k in indicatorMap:
                indicatorMap[k].append(v)
            else:
                indicatorMap[k] = [v]
    for k in indicatorMap:
        indicatorMap[k] = combinationFunction(indicatorMap[k])
    return indicatorMap


if __name__ == "__main__":
    import doctest
    import unittest

    suite = doctest.DocFileSuite('tests/indicators.txt')
    unittest.TextTestRunner().run(suite)
#     #doctest.testmod()
#     #doctest.testfile("example.txt")
