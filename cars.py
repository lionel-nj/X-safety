import toolkit

from trafficintelligence import moving


class UserInput(object):
    def __init__(self, alignmentIdx, desiredSpeedParameters, headwayDistribution, headwayParam,
                 seed, volume, geometryParam, driverDistribution, headways=None,
                 driverParam={'tn': {'loc': None, 'scale': None}, 'tiv_min': {'loc': None, 'scale': None},
                              'critGap': {'loc': None, 'scale': None}}):
        self.alignmentIdx = alignmentIdx
        self.desiredSpeedParameters = desiredSpeedParameters
        self.headways = headways
        self.headwayDistribution = headwayDistribution
        self.headwayParam = headwayParam
        self.seed = seed
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
                                               distribution=toolkit.partialLoadFromYaml('distribution.yml', 'headways'),  #self.headwayDistribution.getDistribution(),
                                               scale=self.headwayParam,
                                               tiv=tiv,
                                               tivprobcum=tivprobcum)

    def initUser(self, userNum, initialCumulatedHeadway):
        """generates a MovingObject on the UserInput alignment"""
        speedNorm = toolkit.partialLoadFromYaml('distribution.yml', 'speed').getDistribution()
        tauNorm = toolkit.partialLoadFromYaml('distribution.yml', 'tau').getDistribution()
        dNorm = toolkit.partialLoadFromYaml('distribution.yml', 'dn').getDistribution()

        obj = moving.MovingObject(userNum, geometry=toolkit.partialLoadFromYaml('distribution.yml', 'geometry').getDistribution().rvs(),  #self.driverDistribution.distribution.rvs(self.geometryParam[0],# self.geometryParam[1]),
                                  initCurvilinear=True)
        obj.addNewellAttributes(speedNorm.rvs(),
                                tauNorm.rvs(),
                                dNorm.rvs(),
                                # 1000./120.,   #dn,  #kj=120 veh/km TODO get from distribution  #obj.desiredSpeed * obj.tiv_min,
                                initialCumulatedHeadway,
                                self.alignmentIdx)
        # # utile?
        # obj.criticalGap = self.driverDistribution.distribution.rvs(
        #     self.driverParam["critGap"]["loc"],
        #     self.driverParam["critGap"]["scale"])

        if len(self.alignment.vehicles) > 0:
            obj.leader = self.alignment.vehicles[-1]  # TODO verify?
        self.alignment.vehicles.append(obj)


class CarGeometry:
    def __init__(self, length=None, width=None, polygon=None):
        self.length = length
        self.width = width
        self.polygon = polygon


class Distribution:
    def __init__(self, typeOfDistribution, distributionName, loc=None, scale=None, degeneratedConstant=None, cdf=None):
        self.typeOfDistribution = typeOfDistribution
        self.distributionName = distributionName
        self.loc = loc
        self.scale = scale
        self.degeneratedConstant = degeneratedConstant
        self.cdf = cdf

    def __eq__(self, other):
        return self.distribution.__dict__ == other.__dict__

    @staticmethod
    def load(distribution):
        return toolkit.load_yaml(distribution)

    def save(self, fileName):
        toolkit.save_yaml(fileName, self)

    def getDistribution(self):
        from scipy import stats
        from trafficintelligence import utils

        if self.typeOfDistribution == 'theoric':
            if self.distributionName == 'norm':
                return stats.norm(self.loc, self.scale)
            elif self.distributionName == 'expon':
                return stats.expon(self.loc)
            else:
                print('error in distribution name')
        elif self.typeOfDistribution == 'empirical':
            return utils.EmpiricalContinuousDistribution(self.cdf[0], self.cdf[1])
        elif self.typeOfDistribution == 'degenerated':
            return self.degeneratedConstant
        else:
            print('error in type of distribution')


