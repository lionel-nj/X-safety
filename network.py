import itertools
import sqlite3

import matplotlib.pyplot as plt
import networkx as nx
from scipy import stats
from trafficintelligence import utils, moving, storage

import agents
import toolkit


def getItemByIdx(items, idx):
    '''Returns an item given its id'''
    i = 0
    while i < len(items) and items[i].idx != idx:
        i += 1
    if i < len(items):
        return items[i]
    else:
        print('Index {} does not exist in items'.format(idx))
        return None


class Alignment:
    """Description of road lanes (centre line of a lane)
    point represents the lane geometry (type is moving.Trajectory) """

    def __init__(self, idx=None, points=None, width=None, controlDevice=None, connectedAlignmentIndices=None):
        self.idx = idx
        self.width = width
        self.points = points
        self.controlDevice = controlDevice
        self.connectedAlignmentIndices = connectedAlignmentIndices

    def save(self, filename):
        toolkit.saveYaml(filename, self)

    @staticmethod
    def load(filename):
        return toolkit.loadYaml(filename)

    def plot(self, options='', **kwargs):
        self.points.plot(options, **kwargs)

    def getNextAlignment(self, nextS, user, instant, world, timeStep):
        '''Returns the list of alignments to the next alignment and longitudinal coordinate S on that alignment for objects finding their path'''
        # warning, recursive function
        alignmentDistance = self.getTotalDistance()
        if nextS <= alignmentDistance:
            return [self], nextS
        elif self.getConnectedAlignments() is not None:
            # TODO use proportions at connection
            # TODO check control devices
            cd = self.getControlDevice()
            if cd is not None:
                # cd.setUser(user)
                user.setArrivalInstantAtControlDevice(instant)
                if cd.permissionToGo(instant, user, world, timeStep):
                    user.resetArrivalInstantAtControlDevice()
                    alignments, s = self.connectedAlignments[0].getNextAlignment(nextS - alignmentDistance, user, instant, world, timeStep)
                else:
                    alignments, s = [self], self.getTotalDistance()
            else:
                alignments, s = self.connectedAlignments[0].getNextAlignment(nextS - alignmentDistance, user, instant, world, timeStep)
            return [self] + alignments, s
        else:  # simulation finished, exited network
            return None, None

    def getControlDevice(self):
        return self.controlDevice

    def getCumulativeDistance(self, i):
        return self.points.cumulativeDistances[i]

    def getTotalDistance(self):
        return self.points.getTotalDistance()

    def getIdx(self):
        return self.idx

    def getEntryNode(self):
        return self.entryNode

    def getExitNode(self):
        return self.exitNode

    def getConnectedAlignmentIndices(self):
        return self.connectedAlignmentIndices

    def getConnectedAlignments(self):
        return self.connectedAlignments


class ControlDevice:
    """class for control devices :stop signs, traffic light etc ...
    adapted from traffic_light_simulator package in pip3"""

    def __init__(self, idx, alignmentIdx):  # , category
        self.idx = idx
        # self.category = category
        self.alignmentIdx = alignmentIdx

    def getIdx(self):
        return self.idx
    # categories = {1: 'stop',
    #               2: 'traffic light',
    #               3: 'yield',
    #                  4: 'etc'}

    def getAlignmentIdx(self):
        return self.alignmentIdx

    def reset(self):
        pass

    def getState(self):
        return None

    def update(self, instant):
        pass

    def permissionToGo(self, instant, user, world, timeStep):
        return None

class TrafficLight(ControlDevice):
    def __init__(self, idx, alignmentIdx, redTime, greenTime, amberTime, initialState):
        super(TrafficLight, self).__init__(idx, alignmentIdx)
        self.redTime = redTime
        self.greenTime = greenTime
        self.amberTime = amberTime
        self.initialState = initialState
        self.reset()

    def getState(self):
        """ returns art for the current color """
        return self.state

    def switch(self):
        """ swith state to next state in the sequence """
        if self.state == 'red':
            self.state = 'green'
        elif self.state == 'amber':
            self.state = 'red'
        else:
            self.state = 'amber'

    def update(self, timeStep):
        """Updates the current state for a TrafficLight object for the duration of state"""
        if self.state == 'green':
            if self.remainingGreen > 0:
                self.remainingGreen -= timeStep
            else:
                self.switch()
                self.remainingGreen = self.greenTime
        elif self.state == 'red':
            if self.remainingRed > 0:
                self.remainingRed -= timeStep
            else:
                self.switch()
                self.remainingRed = self.redTime
        else:
            if self.remainingAmber > 0:
                self.remainingAmber -= timeStep
            else:
                self.switch()
                self.remainingAmber = self.amberTime

    def reset(self):
        """ resets the defaut parameters of a traffic light .. useful to avoid different initial
        state between two replications of a same simulation """
        self.state = self.initialState
        self.remainingRed = self.redTime
        self.remainingAmber = self.amberTime
        self.remainingGreen = self.greenTime

    def permissionToGo(self, instant):
        if self.state == 'green':
            return True
        elif self.state == 'amber':
            return True
        else:
            return False


class StopSign(ControlDevice):
    def __init__(self, idx, alignmentIdx, stopDuration):
        super(StopSign, self).__init__(idx, alignmentIdx)
        self.user = None
        self.stopDuration = stopDuration

    def permissionToGo(self, instant, user, world, timeStep):
        if user.getWaitingTimeAtControlDevice(instant) < self.stopDuration/timeStep:
            return False
        else:
            if world.estimateGap(user, instant, timeStep) > user.getCriticalGap()/timeStep:
                return True
            else:
                return False  # pas passer

class YieldSign(ControlDevice):
    def __init__(self, idx, alignmentIdx):
        super(YieldSign, self).__init__(idx, alignmentIdx)


# class ETC(ControlDevice):
#     def __init__(self, idx, alignmentIdx, category=1, initialState='green'):
#         super().__init__(idx, category, alignmentIdx)
#         self.initialState = initialState
#         self.states = [self.initialState]


class World:
    """Description of the world, including the road (alignments), control devices (signs, traffic lights) and crossing point """

    def __init__(self, alignments=None, controlDevices=None, userInputs=None):
        self.alignments = alignments  # liste d alignements
        self.userInputs = userInputs  # liste des intersections (objets)
        self.controlDevices = controlDevices  # liste de CD

    def __repr__(self):
        return "alignments: {}, control devices: {}, user inputs: {}".format(self.alignments, self.controlDevices, self.userInputs)

    @staticmethod
    def load(filename):
        """loads a yaml file"""
        return toolkit.loadYaml(filename)

    def save(self, filename):
        """saves data to yaml file"""
        toolkit.saveYaml(filename, self)

    def saveCurvilinearTrajectoriesToSqlite(self, db):
        connection = sqlite3.connect(db)
        storage.saveTrajectoriesToTable(connection, self.completed, 'curvilinear')  # completion with curvilinear trajectories tables
        saveObjects(db, self.completed)


    @staticmethod
    def takeEntry(elem):
        return elem.getTimeInterval()[0]

    def reset(self, alignments, controlDevices, userInputs):
        """alignments = list of Alignment class objects"""
        self.controlDevices = controlDevices
        self.alignments = alignments
        self.userInputs = userInputs
        self.save("default.yml")

    def plot(self, options='', **kwargs):
        for a in self.alignments:
            a.plot(options, **kwargs)

    def plotUserTrajectories(self, timeStep, plotPerLane=True):
        if plotPerLane:
            for al in self.alignments:
                plt.figure(al.idx)
                for u in self.users + self.completed:
                    if u.timeInterval is not None:
                        u.plotCurvilinearPositions(al.idx)
                plt.xlabel('time ({}s)'.format(timeStep))
                plt.ylabel('longitudinal coordinate (m)')
                plt.title('Lane {}'.format(al.idx))
        else:
            plt.figure()
            for u in self.users + self.completed:
                if u.timeInterval is not None:
                    u.plotCurvilinearPositions()
            plt.xlabel('time ({}s)'.format(timeStep))
            plt.ylabel('longitudinal coordinate (m)')
        plt.show()

    def getAlignments(self):
        return self.alignments

    def getUserInputs(self):
        return self.userInputs

    def updateControlDevices(self, timeStep):
        if self.controlDevices is not None:
            for cd in self.controlDevices:
                cd.update(timeStep)

    def resetControlDevices(self):
        """resets original information for traffic lights"""
        if self.controlDevices is not None:
            for cd in self.controlDevices:
                cd.reset()

    def getUserByNum(self, userNum):
        """returns an user given its num"""
        for user in self.users+self.completed:
            if user.num == userNum:
                return user
        print("userNum does not match any existing user")
        return None

    def initUsers(self, instant, timeStep, userNum):
        """Initializes new users """
        for ui in self.userInputs:
            futureCumulatedHeadways = []
            for h in ui.cumulatedHeadways:
                if instant <= h / timeStep < instant + 1:
                    self.users.append(ui.initUser(userNum, h))
                    userNum += 1
                else:
                    futureCumulatedHeadways.append(h)
            ui.cumulatedHeadways = futureCumulatedHeadways
        return userNum

    def updateUsers(self, instant, timeStep):
        self.newlyCompleted = []
        for u in self.users:
            u.updateCurvilinearPositions(instant, timeStep, self)
        for u in self.newlyCompleted:
            self.users.remove(u)
            self.completed.append(u)

    def initNodesToAlignments(self):
        """sets an entry and an exit node to each alignment"""
        al = self.alignments[self.userInputs[0].getAlignmentIdx()]
        al.entryNode = al.idx
        al.exitNode = al.idx + 1
        if al.getConnectedAlignmentIndices() is not None:
            for connectedAlignmentIdx in al.getConnectedAlignmentIndices():
                self.alignments[connectedAlignmentIdx].entryNode = al.exitNode
                self.alignments[connectedAlignmentIdx].exitNode = connectedAlignmentIdx + 1
            centerNode = al.exitNode
        for ui in self.userInputs:
            if ui.getIdx() != self.userInputs[0].getIdx():
                self.alignments[ui.getAlignmentIdx()].entryNode = ui.getAlignmentIdx() + 1
                self.alignments[ui.getAlignmentIdx()].exitNode = centerNode

    def initGraph(self):
        """sets graph attribute to self"""
        G = nx.DiGraph()
        self.initNodesToAlignments()
        edgesProperties = []
        for al in self.alignments:
            edgesProperties.append((al.getEntryNode(), al.getExitNode(), al.getTotalDistance()))
        G.add_weighted_edges_from(edgesProperties)
        if self.controlDevices is not None:
            for cd in self.controlDevices:
                controlDevice = "cd{}".format(cd.getIdx())
                G.add_node(controlDevice)
                origin = self.alignments[cd.getAlignmentIdx()].getEntryNode()
                target = self.alignments[cd.getAlignmentIdx()].getExitNode()
                weight = self.alignments[cd.getAlignmentIdx()].getTotalDistance()
                G.add_weighted_edges_from([(origin, controlDevice, weight), (controlDevice, target, 0)])
        self.graph = G

    def distanceAtInstant(self, user1, user2, instant, method='curvilinear'):
        """"computes the distance between 2 users"""
        if user1.getFirstInstant() <= instant and user2.getFirstInstant() <= instant:
            if method == 'curvilinear':

                if moving.Interval.intersection(user1.timeInterval, user2.timeInterval) is not None:
                    s1, _, user1AlignmentIdx = user1.getCurvilinearPositionAtInstant(instant)
                    s2, _, user2AlignmentIdx = user2.getCurvilinearPositionAtInstant(instant)
                    if user1AlignmentIdx == user2AlignmentIdx:
                        return abs(s1 - s2) - user1.orderUsersByFirstInstant(user2)[0].geometry
                    else:
                        user1UpstreamDistance = user1.getCurvilinearPositionAtInstant(instant)[0]
                        user1DownstreamDistance = self.alignments[user1.getCurvilinearPositionAtInstant(instant)[2]].getTotalDistance() - user1UpstreamDistance
                        user2UpstreamDistance = user2.getCurvilinearPositionAtInstant(instant)[0]
                        user2DownstreamDistance = self.alignments[user2.getCurvilinearPositionAtInstant(instant)[2]].getTotalDistance() - user2UpstreamDistance

                        G = self.graph

                        G.add_node('user1')
                        G.add_node('user2')

                        user1Origin = self.alignments[user1AlignmentIdx].entryNode
                        user1Target = self.alignments[user1AlignmentIdx].exitNode
                        user2Origin = self.alignments[user2AlignmentIdx].entryNode
                        user2Target = self.alignments[user2AlignmentIdx].exitNode

                        G.add_weighted_edges_from([(user1Origin, 'user1', user1UpstreamDistance)])
                        G.add_weighted_edges_from([('user1', user1Target, user1DownstreamDistance)])
                        # G.add_weighted_edges_from([(user1Target, 'user1', user1UpstreamDistance_2)])

                        G.add_weighted_edges_from([(user2Origin, 'user2', user2UpstreamDistance)])
                        G.add_weighted_edges_from([('user2', user2Target, user2DownstreamDistance)])
                        # G.add_weighted_edges_from([(user2Target, 'user2', user2DownstreamDistance)])

                        distance = nx.shortest_path_length(G, source='user1', target='user2', weight='weight')

                        situation, pastCP = self.getUsersSituationAtInstant(user1, user2, instant)
                        if situation == 'CF':
                            leader = user1.orderUsersByFirstInstant(user2)[0]
                            distance -= leader.geometry

                        elif situation == 'X1':
                            distance -= user1.geometry - user2.geometry

                        elif situation == 'X3':
                            distance -= pastCP.geometry

                        G.remove_node('user1')
                        G.remove_node('user2')
                        return distance

            elif method == 'euclidian':
                user1, user2 = user1.orderUsersByFirstInstant(user2)
                s1 = user1.getCurvilinearPositionAtInstant(instant)
                s2 = user2.getCurvilinearPositionAtInstant(instant)
                p1 = moving.getXYfromSY(s1[0], s1[1], s1[2], [al.points for al in self.alignments])
                p2 = moving.getXYfromSY(s2[0], s2[1], s2[2], [al.points for al in self.alignments])
                situation = self.getUsersSituationAtInstant(user1, user2, instant)
                if situation == 'CF':
                    distance = (p1-p2).norm2() - user1.geometry
                else:
                    distance = (p1-p2).norm2()
                return distance

        else:
            print('user do not coexist, therefore can not compute distance')
    def travelledAlignments(self, user, instant):
        """"returns a list of the alignments that user travelled on"""
        if instant is not None:
            alignments = list(set(user.curvilinearPositions.lanes[:instant - user.timeInterval.first]))
            travelledAlignments = []
            for alIndices in alignments:
                travelledAlignments.append(self.alignments[alIndices].points)
            return travelledAlignments
        else:
            alignments = list(set(user.curvilinearPositions.lanes))
            travelledAlignments = []
            for alIndices in alignments:
                travelledAlignments.append(self.alignments[alIndices].points)
            return travelledAlignments

    def duplicateLastVelocities(self):
        for user in self.users + self.completed:
            if user.curvilinearVelocities is not None:
                if len(user.curvilinearVelocities) > 0:
                    user.curvilinearVelocities.duplicateLastPosition()

    def prepare(self, duration):
        '''Prepares the world before simulation
        - verify alignments and controlDevices are stored in order
        - init user inputs, links to alignments
        - links the alignments using connectedAlignments
        - links controlDevices to their alignments
        - initializes lists of users
        - initializes the graph

        TODO move checks to other checks, eg that no alignment is so short that is can be bypassed by fast user'''

        # verify alignments and controlDevices are stored in order
        i = 0
        while i < len(self.alignments) and self.alignments[i].idx == i:
            i += 1
        if i < len(self.alignments):  # we have to realign
            self.alignments.sort(key=lambda al: al.idx)
        if self.controlDevices is not None:
            i = 0
            while i < len(self.controlDevices) and self.controlDevices[i].idx == i:
                i += 1
            if i < len(self.controlDevices):  # we have to realign
                self.alignments.sort(key=lambda cd: cd.idx)

        # initialize user inputs
        for ui in self.userInputs:
            ui.lastGeneratedUser = None
            # link to alignment
            for al in self.alignments:
                if al.idx == ui.alignmentIdx:
                    ui.alignment = al
            ui.initDistributions()
            ui.generateHeadways(duration)

        # compute cumulative distances for each alignment :
        for al in self.alignments:
            al.points.computeCumulativeDistances()

        # resetting all control devices to default values
        self.resetControlDevices()

        # connecting alignments
        for al in self.alignments:
            if al.getConnectedAlignmentIndices() is not None:
                al.connectedAlignments = [self.alignments[connectedAlignmentIdx] for connectedAlignmentIdx in al.getConnectedAlignmentIndices()]
            else:
                al.connectedAlignments = None

            # connecting control devices to their alignments
            if self.controlDevices is None:
                al.controlDevice = None
            else:
                for cd in self.controlDevices:
                    if al.idx == cd.alignmentIdx:
                        al.controlDevice = cd
                    else:
                        al.controlDevice = None

        # linking self to its graph
        self.initGraph()

        # TODO verify consistency, users cannot pass more than one alignment in one step

        # initializing the lists of users
        self.users = []
        self.completed = []

    def getIntersectionCPAtInstant(self, user, instant):
        alIdx = user.getCurvilinearPositionAtInstant(instant)[2]
        return self.getIntersectionCP(alIdx)

    def getIntersectionCP(self, alIdx):
        """"returns the curvilinear positions of the crossing point on all its alignments
        alIdx : alignment to project on"""
        al = self.alignments[alIdx]
        if al.getConnectedAlignmentIndices() is None:
            return 0
        else:
            return al.getTotalDistance()

    def getIncomingTrafficAlignmentIdx(self, user, instant):
        """"returns the alignment id of the adjacent alignment where the traffic comes from"""
        if instant in list(user.timeInterval):
            _temp = self.alignments[user.getCurvilinearPositionAtInstant(instant)[2]].getConnectedAlignmentIndices()
            if _temp is not None:
                for al in self.alignments:  # determiner l'alignement sur lequel le traffic adjacent arrive
                    if al.idx != user.getCurvilinearPositionAtInstant(instant)[2]:
                        if al.getConnectedAlignmentIndices() is not None:
                            return al.idx

    def checkTraffic(self, user, instant):
        """"returns the closest user to cross the intersection in the adjacent alignments"""
        lane = self.getIncomingTrafficAlignmentIdx(user, instant)
        if lane is not None:
            if user.leader is not None:
                if user.leader.getCurvilinearPositionAtInstant(instant)[2] != user.getCurvilinearPositionAtInstant(instant)[2]:

                    adjacentUsers = []
                    for _user in self.completed + self.users:
                        if _user.num != user.num:
                            if _user.timeInterval is not None and instant in list(_user.timeInterval):
                                if _user.getCurvilinearPositionAtInstant(instant)[2] == lane:
                                    adjacentUsers.append(_user)

                    sortedUserList = sorted(adjacentUsers, key=lambda x: x.getCurvilinearPositionAtInstant(instant)[0], reverse=True)
                    if sortedUserList != []:
                        return sortedUserList[0]
                    else:
                        return None
                else:
                    return None
            else:
                adjacentUsers = []
                for _user in self.completed + self.users:
                    if _user.num != user.num:
                        if _user.timeInterval is not None and instant in list(_user.timeInterval):
                            if _user.getCurvilinearPositionAtInstant(instant)[2] == lane:
                                adjacentUsers.append(_user)

                sortedUserList = sorted(adjacentUsers, key=lambda x: x.getCurvilinearPositionAtInstant(instant)[0], reverse=True)
                if sortedUserList != []:
                   return sortedUserList[0]
                else:
                    return None
        else:
            return None

    def estimateGap(self, user, instant, timeStep):
        """returns an estimate of the gap at X intersection, based on the speed of the incoming vehicle,
        and the distance remaining between the center of the intersection"""
        if user.timeInterval is not None:
            incomingUser = self.checkTraffic(user, instant)
            if incomingUser is None:
                print('inf1', user.num, instant)
                return float('inf')
            else:
                v = incomingUser.getCurvilinearVelocityAtInstant(instant-1)[0] / timeStep
                if v != 0:
                    d = self.distanceAtInstant(incomingUser, user, instant) - (self.alignments[user.getCurvilinearPositionAtInstant(instant)[2]].getTotalDistance() - user.getCurvilinearPositionAtInstant(instant)[0])
                    return d / v
                else:
                    return float('inf')
        else:
            return float('inf')

    def travelledAlignmentsDistanceAtInstant(self, user, instant):
        s = 0
        for al in self.travelledAlignments(user, instant):
            s += al.getTotalDistance()
        return s

    def isGapAcceptable(self, user, instant):
        if user.criticalGap < self.estimateGap(user, instant):
            return True
        else:
            return False

    def isClearingTimeAcceptable(self, user, timeStep):
        # todo : a verifier
        v = user.curvilinearVelocities[-1][0] / timeStep
        d = self.alignments[user.curvilinearPositions[-1][2]].connectedAlignments[2].width + user.geometry
        clearingTime = d / v
        if clearingTime < user.supposedAmberTime:
            return True
        else:
            return False

    def getIntersectionXYcoords(self):
        for al in self.alignments:
            if al.getConnectedAlignmentIndices() is not None and len(al.getConnectedAlignmentIndices()) > 1:
                break
        try:
            intersection = al.points.getLineIntersections(self.alignments[al.getConnectedAlignmentIndices()[1]].points[0], self.alignments[al.getConnectedAlignmentIndices()[1]].points[1])[1]
            return intersection[0]
        except:
            return None

    def getControlDevicePositionOnAlignment(self, alIdx):
        al = self.alignments[alIdx]
        if al.controlDevice is None:
            return 0
        else:
            return al.getTotalDistance()

    def assignValue(self, args):
        self.userInputs[0].distributions['headway'].scale = args.headway - 1
        self.userInputs[0].distributions['speed'].loc = args.speed
        self.userInputs[0].distributions['dn'].loc = args.dn
        self.userInputs[0].distributions['tau'].loc = args.tau
        self.userInputs[0].distributions['length'].loc = args.l

    def getUsersSituationAtInstant(self, user, other, instant):
        """returns CF if car are in a CF situation
        X1 if both cars are past the intersection
        X2 if both cars are before the intersection
        X3 if one of the cars is before the intersection and the other one is past it
        nb: if cars are in a CF situation but not leading one another, X1, X2 OR X3 is returned, to be improved ... """

        oldest, youngest = user.orderUsersByFirstInstant(other)
        if youngest.leader is not None:
            if oldest.num == youngest.leader.num:
                return 'CF', None

        user1CP = self.getIntersectionCPAtInstant(user, instant)
        user2CP = self.getIntersectionCPAtInstant(other, instant)

        if user1CP < user.getCurvilinearPositionAtInstant(instant)[0]:
            if user2CP < other.getCurvilinearPositionAtInstant(instant)[0]:
                return 'X1', None
            else:
                return 'X3', user

        elif user1CP >= user.getCurvilinearPositionAtInstant(instant)[0]:
            if user2CP > other.getCurvilinearPositionAtInstant(instant)[0]:
                return 'X2', None
            else:
                return 'X3', other

    def finalize(self, lastInstant):
        for u in self.users:
            if u.timeInterval is not None:
                if u.getLastInstant() != lastInstant:
                    self.completed.append(u)
                    self.users.remove(u)

    def updateControlDevices(self, timeStep):
        if self.controlDevices is not None:
            for cd in self.controlDevices:
                cd.cycle(timeStep)

    def getGraph(self):
        return self.graph


class UserInput:
    def __init__(self, idx, alignmentIdx, distributions):
        self.idx = idx
        self.alignmentIdx = alignmentIdx
        self.distributions = distributions

    def save(self, filename):
        toolkit.saveYaml(filename, self)

    @staticmethod
    def load(filename):
        return toolkit.loadYaml(filename)

    def initDistributions(self):
        self.headwayDistribution = self.distributions['headway'].getDistribution()
        self.lengthDistribution = self.distributions['length'].getDistribution()
        self.speedDistribution = self.distributions['speed'].getDistribution()
        self.tauDistribution = self.distributions['tau'].getDistribution()
        self.dDistribution = self.distributions['dn'].getDistribution()
        self.gapDistribution = self.distributions['criticalGap'].getDistribution()
        self.amberProbabilityDistribution = self.distributions['amberProbability'].getDistribution()

    def generateHeadways(self, duration):
        """ generates a set a headways"""
        self.headways = utils.maxSumSample(self.headwayDistribution, duration)
        self.cumulatedHeadways = list(itertools.accumulate(self.headways))

    def getUserInputDistribution(self, item):
        """returns the distribution parameters for an item : type, name, parameters"""
        return self.distributions[item].getDistribution()

    def initUser(self, userNum, initialCumulatedHeadway):
        """generates a MovingObject on the VehicleInput alignment"""

        obj = agents.NewellMovingObject(userNum,
                                        geometry=self.lengthDistribution.rvs(),
                                        initCurvilinear=True,
                                        desiredSpeed=self.speedDistribution.rvs(),
                                        tau=self.tauDistribution.rvs(),
                                        d=self.dDistribution.rvs(),
                                        criticalGap=self.gapDistribution.rvs(),
                                        # kj=120 veh/km
                                        initialCumulatedHeadway=initialCumulatedHeadway,
                                        initialAlignment=self.alignment,
                                        amberProbability=self.amberProbabilityDistribution.rvs())
        if self.lastGeneratedUser is not None:
            # obj.leader = self.generatedNum[-1]
            obj.leader = self.lastGeneratedUser
        self.lastGeneratedUser = obj
        return obj

    def getAlignmentIdx(self):
        return self.alignmentIdx

    def getIdx(self):
        return self.idx


class CarGeometry:
    def __init__(self, length=None, width=None, polygon=None):
        self.width = width
        self.length = length
        self.polygon = polygon


class Distribution(object):
    def __init__(self, distributionType, distributionName=None, loc=None, scale=None, a=None, b=None, cdf=None, degeneratedConstant=None):
        self.loc = loc
        self.scale = scale
        self.a = a
        self.b = b
        self.cdf = cdf
        self.distributionType = distributionType
        self.distributionName = distributionName
        self.degeneratedConstant = degeneratedConstant

    def save(self, fileName):
        return toolkit.saveYaml(fileName, self)

    @staticmethod
    def load(fileName):
        return toolkit.loadYaml(fileName)

    def getDistribution(self):
        """returns the scipy.stats objects that corresponds to the parameters in Distribution object"""

        if self.distributionType == 'theoretic':
            if self.distributionName == 'norm':
                return stats.norm(loc=self.loc, scale=self.scale)
            if self.distributionName == 'truncnorm':
                return stats.truncnorm(loc=self.loc, scale=self.scale, a=self.a, b=self.b)
            elif self.distributionName == 'expon':
                return stats.expon(loc=self.loc, scale=self.scale)
            else:
                raise NameError('error in distribution name')
        elif self.distributionType == 'empirical':
            return utils.EmpiricalContinuousDistribution(self.cdf[0], self.cdf[1])
        elif self.distributionType == 'degenerated':
            return utils.ConstantDistribution(self.degeneratedConstant)
        else:
            raise NameError('error in distribution type')

    def getType(self):
        return self.distributionType

    def getName(self):
        return self.distributionName

    def getScale(self):
        return self.scale

    def getLoc(self):
        return self.loc

    def getCdf(self):
        return self.cdf

    def getConstant(self):
        return self.degeneratedConstant

    def getMinThreshold(self):
        return self.a

    def getMaxThreshold(self):
        return self.b


def createNewellMovingObjectsTable(db):
    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS objects (object_id INTEGER, road_user_type INTEGER, tau REAL, d REAL, desired_speed REAL, geometry REAL, PRIMARY KEY(object_id))")
    storage.createCurvilinearTrajectoryTable(cursor)
    connection.commit()


def saveObjects(filename, objects):
    with sqlite3.connect(filename) as connection:
        cursor = connection.cursor()
        objectQuery = "INSERT INTO objects VALUES (?,?,?,?,?,?)"
        for obj in objects:
            cursor.execute(objectQuery, (obj.getNum(), obj.getUserType(), obj.tau, obj.d, obj.desiredSpeed, obj.geometry))
            connection.commit()


if __name__ == "__main__":
    import doctest

    doctest.testmod()
