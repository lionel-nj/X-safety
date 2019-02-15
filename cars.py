import toolkit


class VehicleInput(object):
    def __init__(self, alignmentIdx, desiredSpeedParameters, headwayDistribution, headwayParam,
                 seed, tSimul, volume, geometryParam, driverDistribution, headways=None,
                 driverParam={'tn': {'scale': None, 'sd': None}, 'tiv_min': {'scale': None, 'sd': None},
                              'critGap': {'scale': None, 'sd': None}}):
        self.alignmentIdx = alignmentIdx
        self.desiredSpeedParameters = desiredSpeedParameters
        self.headways = headways
        self.headwayDistribution = headwayDistribution
        self.headwayParam = headwayParam
        self.seed = seed
        self.tSimul = tSimul
        self.volume = volume
        self.geometryParam = geometryParam
        self.driverParam = driverParam
        self.driverDistribution = driverDistribution.distribution

    def save(self, filename):
        toolkit.save_yaml(filename, self)

    @staticmethod
    def distanceGap(sLeader, sFollowing, lengthLeader):
        """calculates distance gaps between two vehicles"""
        distance = sLeader - sFollowing - lengthLeader
        return distance

    def generateHeadways(self, duration, seed, tiv=None, tivprobcum=None):
        """ generates a set a headways"""
        self.headways = toolkit.generateSample(duration=duration,
                                               seed=seed,
                                               distribution=self.headwayDistribution,
                                               scale=self.headwayParam,
                                               tiv=tiv,
                                               tivprobcum=tivprobcum)


class CarGeometry:
    def __init__(self, length=None, width=None, polygon=None):
        self.length = length
        self.width = width
        self.polygon = polygon


class Distribution:
    def __init__(self, distribution):
        self.distribution = distribution

    def __eq__(self, other):
        return self.distribution.__dict__ == other.__dict__
