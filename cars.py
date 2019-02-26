import toolkit

from trafficintelligence import moving

class UserInput(object):
    def __init__(self, alignmentIdx, desiredSpeedParameters, headwayDistribution, headwayParam,
                 seed, volume, geometryParam, driverDistribution, headways=None,
                 driverParam={'tn': {'scale': None, 'sd': None}, 'tiv_min': {'scale': None, 'sd': None},
                              'critGap': {'scale': None, 'sd': None}}):
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
                                               distribution=self.distributions['headways'].getDistribution(),
                                               scale=self.headwayParam,
                                               tiv=tiv,
                                               tivprobcum=tivprobcum)

    def initUser(self, userNum, initialCumulatedHeadway):
        """generates a MovingObject on the VehicleInput alignment"""
        geomNorm = self.distributions['geometry'].getDistribution()
        speedNorm = self.distributions['speed'].getDistribution()
        tauNorm = self.distributions['tau'].getDistribution()
        dNorm = self.distributions['dn'].getDistribution()

        obj = moving.MovingObject(userNum, geometry=geomNorm.rvs, initCurvilinear=True)
        obj.addNewellAttributes(speedNorm.rvs(),
                                tauNorm.rvs(),
                                dNorm.rvs(),#kj=120 veh/km TODO get from distribution #obj.desiredSpeed * obj.tiv_min
                                initialCumulatedHeadway,
                                self.alignmentIdx)

        # # utile?
        # obj.criticalGap = self.driverDistribution.distribution.rvs(
        #     self.driverParam["critGap"]["scale"],
        #     self.driverParam["critGap"]["sd"])

        if len(self.alignment.vehicles) > 0:
            obj.leader = self.alignment.vehicles[-1] # TODO verify?
        self.alignment.vehicles.append(obj)

class CarGeometry:
    def __init__(self, length=None, width=None, polygon=None):
        self.length = length
        self.width = width
        self.polygon = polygon


class Distribution:
    def __init__(self, typeOfDistribution, distributionName, loc, scale, cdf, constant):
        self.typeOfDistribution = typeOfDistribution
        self.distributionName = distributionName
        self.loc = loc
        self.scale = scale
        self.cdf = cdf
        self.constant = constant

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
            return self.constant
        else:
            print('error in distribution type')
