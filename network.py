import sqlite3

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from scipy import stats
from trafficintelligence import utils, moving, indicators

import agents
import events
import toolkit


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
        if stats.randint(0, 1).rvs() == 1:
            p = self.points[0]
        else:
            p = self.points[1]
        plt.text(p.x + 5, p.y + 5, str(self.idx))

    def getNextAlignment(self, nextS, user, instant, world):
        '''Returns the list of alignments to the next alignment and longitudinal coordinate S on that alignment for objects finding their path'''
        # warning, recursive function
        alignmentDistance = self.getTotalDistance()
        if nextS <= alignmentDistance:
            return [self], nextS
        elif self.getConnectedAlignments() is not None:
            # TODO use proportions at connection
            # TODO check control devices
            cd = self.getControlDevice()
            nextAlignment = self.drawNextAlignment()
            if cd is not None:
                user.setArrivalInstantAtControlDevice(instant)
                if cd.permissionToGo(instant, user, world):
                    user.resetArrivalInstantAtControlDevice()
                    alignments, s = nextAlignment.getNextAlignment(nextS - alignmentDistance, user, instant, world)
                else:
                    alignments, s = [self], self.getTotalDistance()
            else:
                alignments, s = nextAlignment.getNextAlignment(nextS - alignmentDistance, user, instant, world)
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

    def initConnectedAlignmentDistribution(self):
        connectedAlignmentIndices = self.getConnectedAlignmentIndices()
        if connectedAlignmentIndices is not None:
            self.connectedAlignmentDistribution = stats.rv_discrete(name='custm', values=(list(range(len(connectedAlignmentIndices))), self.getConnectedAlignmentMovementProportions()))

    def getConnectedAlignmentMovementProportion(self, i):
        if self.connectedAlignmentIndices is None:
            return None
        else:
            return self.connectedAlignmentIndices[i]

    def getConnectedAlignmentIndices(self):
        if self.connectedAlignmentIndices is not None:
            return list(self.connectedAlignmentIndices.keys())
        else:
            return None

    def getConnectedAlignmentMovementProportions(self):
        if self.connectedAlignmentIndices is not None:
            return list(self.connectedAlignmentIndices.values())
        else:
            return None

    def getConnectedAlignments(self):
        return self.connectedAlignments

    def assignUserAtInstant(self, user, instant):
        if instant in self.currentUsers:
            self.currentUsers[instant].append(user)
        else:
            self.currentUsers[instant] = [user]

    def getTransversalAlignments(self):
        return self.getTransversalAlignments

    def drawNextAlignment(self):
        return self.connectedAlignments[self.connectedAlignmentDistribution.rvs()]

    def getUsersOnAlignmentAtInstant(self, instant):
        '''returns users on alignment at instant'''
        if instant in self.currentUsers:
            return self.currentUsers[instant]
        else:
            return []

    def getPossiblePathsFromAlignment(self, path=[]):
        path = path + [self]
        if self.getConnectedAlignments() is None:
            return [path]
        else:
            paths = []
            for idx, connectedAlignment in enumerate(self.getConnectedAlignments()):
                if connectedAlignment not in path and self.getConnectedAlignmentMovementProportions()[idx] != 0:
                    newpaths = connectedAlignment.getPossiblePathsFromAlignment(path)
                    for newpath in newpaths:
                        paths.append(newpath)
            return paths

    @staticmethod
    def getAlignmentIntersectionSequence(path):
        result = []
        for item in path:
            result.append(item)
            result.append(item.exitIntersection)
        return result

    @staticmethod
    def getIntersectionSequence(path):
        result = []
        for item in path:
            result.append(item.exitIntersection)
        return result

    def getAllPossibleAlignmentIntersectionSequences(self):
        paths = self.getPossiblePathsFromAlignment()
        return [self.getAlignmentIntersectionSequence(path) for path in paths]

    def getAllPossibleIntersectionSequences(self):
        paths = self.getPossiblePathsFromAlignment()
        result = []
        for path in paths:
            result.append(self.getIntersectionSequence(path))
        return result

    def getFirstUser(self):
        return self.firstUser

    def getExitIntersection(self):
        return self.exitIntersection

    def getEntryIntersection(self):
        return self.entryIntersection


class ControlDevice:
    """class for control devices :stop signs, traffic light etc ...
    adapted from traffic_light_simulator package in pip3"""

    def __init__(self, idx, alignmentIdx):
        self.idx = idx
        self.alignmentIdx = alignmentIdx

    def getIdx(self):
        return self.idx

    def getAlignmentIdx(self):
        return self.alignmentIdx

    def reset(self, timeStep):
        pass

    def getState(self):
        return None

    def update(self, timeStep):
        pass

    def permissionToGo(self, instant, user, world):
        return None


class TrafficLight(ControlDevice):
    states = ['green', 'amber', 'red', 'integralRed']

    def __init__(self, idx, alignmentIdx, greenTime, amberTime, integralRed, cycleDuration, slave=None, master=None):
        super(TrafficLight, self).__init__(idx, alignmentIdx)
        self.slave = slave
        self.master = master
        self.redTime = amberTime + greenTime
        self.amberTime = amberTime
        self.greenTime = greenTime
        self.integralRed = integralRed
        self.cycleDuration = cycleDuration

    def checkDurations(self):
        return self.cycleDuration == self.greenTime + self.amberTime + self.redTime + self.integralRed

    def setSlaveState(self):
        if self.master.state == 'green':
            self.state = 'red'
        elif self.master.state == 'amber':
            self.state = 'red'
        else:
            self.state = 'green'

    def drawInitialState(self):
        if self.slave is not None:
            i = stats.randint(0, 3).rvs()
            self.state = TrafficLight.states[i]
        else:
            self.setSlaveState()

    def getState(self):
        """ returns the current color """
        return self.state

    def switch(self):
        """ switches state to next state in the sequence """
        if self.state == 'red':
            self.state = 'integralRed'
        elif self.state == 'integralRed':
            self.state = 'green'
        elif self.state == 'amber':
            self.state = 'red'
        else:
            self.state = 'amber'

    def update(self, timeStep):
        """Updates the current state for a TrafficLight object for the duration of state"""
        if self.state == 'green':
            if self.remainingGreen > 0:
                self.remainingGreen -= 1
            else:
                self.switch()
                self.remainingGreen = self.greenTime / timeStep

        elif self.state == 'red':
            if self.remainingRed > 0:
                self.remainingRed -= 1
            else:
                self.switch()
                self.remainingRed = (self.greenTime + self.amberTime) / timeStep

        elif self.state == 'integralRed':
            if self.remainingIntegralRed > 0:
                self.remainingIntegralRed -= 1
            else:
                self.switch()
                self.remainingIntegralRed = self.integralRed / timeStep

        else:
            if self.remainingAmber > 1:
                self.remainingAmber -= 1
            else:
                self.switch()
                self.remainingAmber = self.amberTime / timeStep

    def reset(self, timeStep):
        """ resets the defaut parameters of a traffic light"""
        self.remainingRed = (self.amberTime + self.greenTime) / timeStep
        self.remainingAmber = self.amberTime / timeStep
        self.remainingGreen = self.greenTime / timeStep
        self.remainingIntegralRed = self.integralRed / timeStep
        self.drawInitialState()

    def permissionToGo(self, instant, user, world):
        if self.getState() in ['red', 'amber']:
            return False
        else:
            return True


class StopSign(ControlDevice):
    def __init__(self, idx, alignmentIdx, stopDuration):
        super(StopSign, self).__init__(idx, alignmentIdx)
        self.user = None
        self.stopDuration = stopDuration
        # self.reset()

    def permissionToGo(self, instant, user, world):
        if user.getWaitingTimeAtControlDevice(instant) < self.convertedStopDuration:
            return False
        else:
            if world.estimateGap(user) > user.getCriticalGap():  # todo estimate time of arrival of vehicle
                return True
            else:
                return False

    def reset(self, timeStep):
        '''converts stop duration in simulation time'''
        self.convertedStopDuration = self.stopDuration / timeStep


class YieldSign(ControlDevice):
    def __init__(self, idx, alignmentIdx):
        super(YieldSign, self).__init__(idx, alignmentIdx)
        self.user = None

    def permissionToGo(self, instant, user, world):
        return world.estimateGap(user) > user.getCriticalGap()


class World:
    """Description of the world, including the road (alignments), control devices (signs, traffic lights) and crossing point """

    def __init__(self, alignments=None, controlDevices=None, userInputs=None):
        self.alignments = alignments
        self.userInputs = userInputs
        self.controlDevices = controlDevices

    def __repr__(self):
        return "alignments: {}, control devices: {}, user inputs: {}".format(self.alignments, self.controlDevices, self.userInputs)

    @staticmethod
    def load(filename):
        """loads a yaml file"""
        return toolkit.loadYaml(filename)

    def save(self, filename):
        """saves data to yaml file"""
        toolkit.saveYaml(filename, self)

    def saveCurvilinearTrajectoriesToSqlite(self, db, seed, analysisId):
        connection = sqlite3.connect(db)
        saveTrajectoriesToTable(connection, [user for user in self.completed + self.users if user.timeInterval is not None], 'curvilinear', seed, analysisId)

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
                # plt.plot([300,300], [0, al.getTotalDistance()], 'go--', color='black')
                # plt.plot([600,600], [0, al.getTotalDistance()], 'go--', color='black')
                # plt.plot([1201,1201], [0, al.getTotalDistance()], 'go--', color='black')
                # plt.plot([1212,1212], [0, al.getTotalDistance()], 'go--', color='black')
                # plt.plot([1512,1512], [0, al.getTotalDistance()], 'go--', color='black')
                # plt.plot([1813,1813], [0, al.getTotalDistance()], 'go--', color='black')
        else:
            plt.figure()
            for u in self.users + self.completed:
                if u.timeInterval is not None:
                    u.plotCurvilinearPositions()
            plt.xlabel('time ({}s)'.format(timeStep))
            plt.ylabel('longitudinal coordinate (m)')
        plt.show()

    def getGraph(self):
        return self.graph

    def getCenterNode(self):
        for ui in self.userInputs:
            if ui.getIdx() != self.userInputs[0].getIdx():
                centerNode = self.alignments[ui.getAlignmentIdx()].exitNode
        return centerNode

    def getUserByNum(self, userNum):
        """returns an user given its num"""
        for user in self.users + self.completed:
            if user.num == userNum:
                return user
        print("userNum does not match any existing user")
        return None

    def initUsers(self, instant, userNum, safetyDistance):
        """Initializes new users """
        for ui in self.userInputs:
            #futureCumulatedHeadways = []
            #for h in ui.cumulatedHeadways:
            if instant <= ui.getTimeArrival():
                    self.newUsers.append(ui.initUser(userNum, ui.getTimeArrival(), safetyDistance))
                    ui.generateTimeArrival()
                    userNum += 1
            #else:
            #        futureCumulatedHeadways.append(h)
            #ui.cumulatedHeadways = futureCumulatedHeadways
        return userNum

    def setInserted(self, user):
        self.inserted.append(user)

    def setNewlyCompleted(self, user):
        self.newlyCompleted.append(user)

    def updateUsers(self, instant, analysisZone=None):
        self.newlyCompleted = []
        self.inserted = []
        for u in self.newUsers + self.users:
            u.updateCurvilinearPositions(instant, self)
            if analysisZone is not None:
                if u.timeInterval is not None:# and u.curvilinearPositions is not None:
                    if analysisZone.positionInAnalysisZone(u.getCurvilinearPositionAt(-1)):
                        if u.timeIntervalInAnalysisZone.first == 0:
                            u.timeIntervalInAnalysisZone.first = instant
                    else:
                        if u.timeIntervalInAnalysisZone.first != 0:
                            if u.timeIntervalInAnalysisZone.last == -1:
                                u.timeIntervalInAnalysisZone.last = instant - 1
        for u in self.inserted:
            for u2 in self.users:
                if u2 == u.getLeader():
                    categoryNum = 1  # rear end
                elif u.areOnTransversalAlignments(u2):
                    categoryNum = 2
                else:
                    categoryNum = None
                newInteraction = events.Interaction(num=len(self.interactions)+len(self.completedInteractions), roadUser1=u, roadUser2=u2, timeInterval=u.commonTimeInterval(u2), useCurvilinear=True, categoryNum=categoryNum)
                newInteraction.roadUser1Positions = {}
                newInteraction.roadUser2Positions = {}
                self.addInteractions(newInteraction)
            self.newUsers.remove(u)
            self.users.append(u)
        for u in self.newlyCompleted:
            self.users.remove(u)
            u.getCurvilinearVelocities().duplicateLastPosition()
            self.completed.append(u)

        # to determine the duration of simulation :
        # self.exitUsersCumulative.append(len(self.completed))
        # self.completedInteractionsCumulative.append(len(self.completedInteractions))

    def addInteractions(self, newInter):
        if newInter.roadUserNumbers not in [i.roadUserNumbers for i in self.interactions]:
            # newInter.num = len(self.interactions)
            self.interactions.append(newInter)

    def updateInteractions(self, instant, computeInteractions):
        newlyCompleted = []
        for inter in self.interactions:
            if (inter.roadUser1.getLastInstant() < instant) or (inter.roadUser2.getLastInstant() < instant):
                newlyCompleted.append(inter)
            else:
                inter.setLastInstant(instant)
                if computeInteractions:


                    distanceIndicator = inter.getIndicator(events.Interaction.indicatorNames[2])

                    if distanceIndicator is None:  # create distance indicator
                        distanceIndicator = indicators.SeverityIndicator(events.Interaction.indicatorNames[2], {instant: None}, mostSevereIsMax=False)
                        inter.addIndicator(distanceIndicator)                        
                    distance = self.distanceAtInstant(inter.roadUser1, inter.roadUser2, instant, 'euclidean')
                    distanceIndicator.values[instant] = distance
                    distanceIndicator.getTimeInterval().last = instant

                    distanceIndicator.getTimeInterval().last = instant

                    if inter.categoryNum == 1:  # rearend
                        distanceIndicator.values[instant] = distance - inter.roadUser2.geometry
                        # compute TTC as distance-length/dv
                        if len(inter.roadUser1.getCurvilinearVelocities()) > 0 and len(inter.roadUser2.getCurvilinearVelocities()) > 0:
                            v1 = inter.roadUser1.getCurvilinearVelocityAt(-1)[0]  # compute distance with distanceAtInstant and euclidean distance -> should be kept for rear end TTC computation
                            v2 = inter.roadUser2.getCurvilinearVelocityAt(-1)[0]  # leader
                            if v2 < v1: # in general, one should check which is first
                                ttc = distanceIndicator[instant] / (v1-v2)
                                ttcIndicator = inter.getIndicator(events.Interaction.indicatorNames[7])
                                if ttcIndicator is None:
                                    ttcIndicator = indicators.SeverityIndicator(events.Interaction.indicatorNames[7], {}, mostSevereIsMax=False)
                                    inter.addIndicator(ttcIndicator)
                                ttcIndicator.values[instant] = ttc
                                ttcIndicator.getTimeInterval().last = instant


                                speedDiffernetialIndicator = inter.getIndicator(events.Interaction.indicatorNames[5])
                                if speedDiffernetialIndicator is None:
                                    speedDifferentialIndicator = indicators.SeverityIndicator(events.Interaction.indicatorNames[5], {}, mostSevereIsMax=False)
                                    inter.addIndicator(speedDifferentialIndicator)
                                v1 = inter.roadUser1.getCurvilinearVelocityAt(-1)[0]  # compute distance with distanceAtInstant and euclidean distance -> should be kept for rear end TTC computation
                                v2 = inter.roadUser2.getCurvilinearVelocityAt(-1)[0]
                                if (v1, v2) != (0, 0):
                                    speedDifferentialIndicator.values[instant] = v2-v1
                                    speedDifferentialIndicator.getTimeInterval().last = instant



                    elif inter.categoryNum == 2 and inter.roadUser1.areOnTransversalAlignments(inter.roadUser2):  # side
                        # compute time to end of each alignment and check if there is a TTC
                        p1 = inter.roadUser1.getCurvilinearPositionAtInstant(instant)
                        p2 = inter.roadUser2.getCurvilinearPositionAtInstant(instant)
                        d1 = inter.roadUser1.getCurrentAlignment().getTotalDistance() - p1[0]
                        d2 = inter.roadUser2.getCurrentAlignment().getTotalDistance() - p2[0]
                        if len(inter.roadUser1.getCurvilinearVelocities()) > 0 and len(inter.roadUser2.getCurvilinearVelocities()) > 0:
                            v1 = inter.roadUser1.getCurvilinearVelocityAt(-1)[0]
                            v2 = inter.roadUser2.getCurvilinearVelocityAt(-1)[0]
                            if v1 > 0 and v2 > 0:
                                timeToEndOfAlignmnent1 = d1 / v1
                                timeToEndOfAlignmnent2 = d2 / v2
                                if timeToEndOfAlignmnent1 < timeToEndOfAlignmnent2:
                                    first = inter.roadUser1
                                    second = inter.roadUser2
                                    t1 = timeToEndOfAlignmnent1
                                    t2 = timeToEndOfAlignmnent2
                                else:
                                    first = inter.roadUser2
                                    second = inter.roadUser1
                                    t1 = timeToEndOfAlignmnent2
                                    t2 = timeToEndOfAlignmnent1
                                    v1, v2 = v2, v1
                                if t2 < t1+first.geometry/v1:
                                    ttc = t2
                                    ttcIndicator = inter.getIndicator(events.Interaction.indicatorNames[7])
                                    if ttcIndicator is None:
                                        ttcIndicator = indicators.SeverityIndicator(events.Interaction.indicatorNames[7], {instant: None}, mostSevereIsMax=False)
                                        inter.addIndicator(ttcIndicator)
                                    ttcIndicator.values[instant] = ttc
                                    ttcIndicator.getTimeInterval().last = instant

        for inter in newlyCompleted:
            self.interactions.remove(inter)
            self.completedInteractions.append(inter)

    def computePET(self, sim):
        if sim.computeInteractions:
            users = sorted([u for u in self.completed+self.users if u.getIntersectionExitInstant() is not None], key = lambda u: u.getIntersectionEntryInstant())
            interactions = [inter for inter in self.completedInteractions+self.interactions if inter.categoryNum == 2]
            for i in range(1,len(users)):
                t1 = users[i-1].getIntersectionExitInstant()
                t2 = users[i].getIntersectionEntryInstant()
                if t1 > t2:
                    pet = 0
                else:
                    pet = t2-t1
                userNumbers = set([users[i-1].getNum(), users[i].getNum()])
                j = 0
                while j<len(interactions) and userNumbers != interactions[j].roadUserNumbers:
                    j += 1
                if j<len(interactions):
                    interactions[j].addIndicator(indicators.SeverityIndicator(events.Interaction.indicatorNames[10], {t1: pet}, mostSevereIsMax=False))
                    interactions.remove(interactions[j])

    def initNodesToAlignments(self):
        """sets an entry and an exit node to each alignment"""
        if self.intersections == []:
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
        else:
            nodeIdx = 0
            for intersection in self.intersections:
                for al in intersection.entryAlignments:
                    al.exitNode = 'intersection' + str(nodeIdx)
                    if al.entryNode is None:
                        al.entryNode = al.idx
                for al in intersection.exitAlignments:
                    al.entryNode = 'intersection' + str(nodeIdx)
                    if al.exitNode is None:
                        al.exitNode = al.idx
                nodeIdx += 1

    def initGraph(self):
        """sets graph attribute to self"""
        G = nx.DiGraph()
        self.initNodesToAlignments()
        edgesProperties = []
        for al in self.alignments:
            edgesProperties.append((al.getEntryNode(), al.getExitNode(), al.getTotalDistance()))
        G.add_weighted_edges_from(edgesProperties)
        self.graph = G

    def distanceAtInstant(self, user1, user2, instant, method):
        """"computes the distance between 2 users"""
        if user1.getFirstInstant() <= instant and user2.getFirstInstant() <= instant:
            if method == 'curvilinear':
                if moving.Interval.intersection(user1.timeInterval, user2.timeInterval) is not None:
                    s1, _, user1AlignmentIdx = user1.getCurvilinearPositionAtInstant(instant)
                    s2, _, user2AlignmentIdx = user2.getCurvilinearPositionAtInstant(instant)
                    if user1AlignmentIdx == user2AlignmentIdx:
                        return abs(s1 - s2) - user1.orderUsersByPositionAtInstant(user2, instant)[0].geometry
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
                        G.add_path([user1Target, 'user1'], weight=user1DownstreamDistance)

                        G.add_weighted_edges_from([(user2Origin, 'user2', user2UpstreamDistance)])
                        G.add_weighted_edges_from([('user2', user2Target, user2DownstreamDistance)])
                        G.add_path([user2Target, 'user2'], weight=user2DownstreamDistance)

                        distance = nx.shortest_path_length(G, source='user1', target='user2', weight='weight')
                        # if situation == 'CF':
                        #     leader = user1.orderUsersByPositionAtInstant(user2, instant)[0]
                        #     distance -= leader.geometry

                        G.remove_node('user1')
                        G.remove_node('user2')
                        return distance

            elif method == 'euclidean':
                #user1, user2 = user1.orderUsersByPositionAtInstant(user2, instant)
                s1 = user1.getCurvilinearPositionAtInstant(instant)
                s2 = user2.getCurvilinearPositionAtInstant(instant)
                p1 = moving.getXYfromSY(s1[0], s1[1], s1[2], [al.points for al in self.alignments])
                p2 = moving.getXYfromSY(s2[0], s2[1], s2[2], [al.points for al in self.alignments])
                distance = (p1 - p2).norm2()
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
        for user in self.users:
            # if user.curvilinearVelocities is not None:
            if len(user.curvilinearVelocities) > 0:
                user.getCurvilinearVelocities().duplicateLastPosition()

    def prepare(self, timeStep, duration):
        '''Prepares the world before simulation
        - verify alignments and controlDevices are stored in order
        - init user inputs, links to alignments
        - links the alignments using connectedAlignments
        - resets and links controlDevices to their alignments
        - initializes lists of users
        - creates intersections objects and links them to the corresponding alignments
        - sets probabilities of travel for connected alignments
        - initializes the graph

        note: duration and timeStep are in usual time units (eg seconds)'''

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
            ui.initDistributions(timeStep)
            ui.generateTimeArrival()

        # compute cumulative distances for each alignment :
        for al in self.alignments:
            al.points.computeCumulativeDistances()

        # resetting all control devices to default values
        if self.controlDevices is not None:
            for cd in self.controlDevices:
                cd.reset(timeStep)

        self.intersections = []
        # connecting alignments
        for al in self.alignments:
            al.entryNode = None
            al.exitNode = None
            al.entryIntersection = None
            al.exitIntersection = None
            al.connectedAlignments = None
            al.transversalAlignments = None
            al.currentUsers = {}
            al.firstUser = None
            al.controlDevice = None

            if al.getConnectedAlignmentIndices() is not None:
                al.connectedAlignments = [self.alignments[connectedAlignmentIdx] for connectedAlignmentIdx in al.getConnectedAlignmentIndices()]

                # create list of transversal alignments
                connectedAlignmentsIndices = set(al.getConnectedAlignmentIndices())
                for al2 in self.alignments:
                    if al2 != al and al2.getConnectedAlignmentIndices() is not None and len(set(al2.getConnectedAlignmentIndices()).intersection(connectedAlignmentsIndices)) > 0:
                        if al.transversalAlignments is None:
                            al.transversalAlignments = [al2]
                        else:
                            al.transversalAlignments.append(al2)

                # start creation of intersection
                if len(connectedAlignmentsIndices) > 1:
                    entryAlignments = [al]
                    exitAlignments = al.getConnectedAlignments()
                    if al.transversalAlignments is not None:
                        entryAlignments += al.transversalAlignments
                    intersection = Intersection(entryAlignments, exitAlignments)

                    entryAlignmentsAlreadyInIntersections = False
                    i = 0
                    while not entryAlignmentsAlreadyInIntersections and i < len(self.intersections):
                        entryAlignmentsAlreadyInIntersections = set(entryAlignments) <= set(self.intersections[i].entryAlignments)
                        i += 1
                    if not entryAlignmentsAlreadyInIntersections:
                        intersection.idx = len(self.intersections)
                        self.intersections.append(intersection)

                al.initConnectedAlignmentDistribution()

        if self.controlDevices is not None:
            for cd in self.controlDevices:
                self.alignments[cd.alignmentIdx].controlDevice = cd
                # for al in self.alignments:
            # connecting control devices to their alignments
            # if self.controlDevices is None:
            #     al.controlDevice = None
            # else:
            #     for cd in self.controlDevices:
            #         if al.idx == cd.alignmentIdx:
            #             al.controlDevice = cd
            #         else:
            #             print(al.idx)
            #             al.controlDevice = None
        # else:
        #     for al in self.alignments:
        #         al.controlDevice = None

        for intersection in self.intersections:
            for entryAl in intersection.entryAlignments:
                entryAl.exitIntersection = intersection
            for exitAl in intersection.exitAlignments:
                exitAl.entryIntersection = intersection

        # linking self to its graph
        self.initGraph()

        # initializing the lists of users
        self.newUsers = []
        self.users = []
        self.completed = []

        # initializing interactions list
        self.interactions = []
        self.completedInteractions = []

        self.exitUsersCumulative = []
        self.completedInteractionsCumulative = []

    def getIntersectionXYcoords(self):
        """returns intersection XY coordinates"""
        for al in self.alignments:
            if al.getConnectedAlignmentIndices() is not None and len(al.getConnectedAlignmentIndices()) > 1:
                return al.points[-1]

    def getIntersectionCPAtInstant(self, user, instant):
        """returns intersection curvilinear position relatively to user position"""
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

    def getControlDevicePositionOnAlignment(self, alIdx):
        al = self.alignments[alIdx]
        if al.transversalAlignments is None:
            return [0, 0, al.idx]
        else:
            return [al.getTotalDistance(), 0, al.idx]

    def distanceToCrossingAtInstant(self, user, incomingUser, instant):
        """"returns distance to intersection"""
        G = self.graph

        G.add_node('incomingUser')
        cp = incomingUser.getCurvilinearPositionAtInstant(instant)

        origin = self.alignments[cp[2]].getEntryNode()
        target = self.alignments[cp[2]].getExitNode()

        upstreamDistance = incomingUser.getCurvilinearPositionAtInstant(instant)[0]
        downstreamDistance = self.alignments[cp[2]].getTotalDistance() - upstreamDistance

        G.add_weighted_edges_from([(origin, 'incomingUser', upstreamDistance)])
        G.add_weighted_edges_from([('incomingUser', target, downstreamDistance)])
        center = self.getNodesFromCrossingPoints(user, incomingUser, instant)[0]  # a modifier selon les un classement sur les probabilités
        distance = nx.shortest_path_length(G, source='incomingUser', target=center, weight='weight')
        G.remove_node('incomingUser')

        return distance

    def estimateGap(self, user):
        """returns an estimate of the gap at X intersection, based on the speed of the incoming vehicle,
        and the distance remaining to the crossing point of trajectories """
        crossingUsers = self.getCrossingUsers(user.getCurrentAlignment())
        gap = float('inf')
        if crossingUsers is not None:
            # timeToCrossing = (user.getCurrentAlignment().getTotalDistance() - user.getCurvilinearPositionAt(-1)[0])
            for al, crossingUser in crossingUsers.items():
                if crossingUser is not None:
                    p = crossingUser.getCurvilinearPositionAt(-1)
                    if crossingUser.length() >= 2:
                        velocity = crossingUser.getCurvilinearVelocityAt(-1)
                        v = velocity[0]
                    else:
                        v = crossingUser.desiredSpeed
                    if v != 0:
                        d = crossingUser.getCurrentAlignment().getTotalDistance() - p[0]
                        gap = min(gap, d / v)
        return gap

    def travelledAlignmentsDistanceAtInstant(self, user, instant):
        """returns travelled distance of user at instant
        0 if the user did not change alignment
        length of travelled alignments otherwise """
        s = 0
        for al in self.travelledAlignments(user, instant):
            s += al.getTotalDistance()
        return s

    def isClearingTimeAcceptable(self, user, timeStep):
        """determines if intersection clearing time for user is acceptable"""
        # todo : a verifier
        v = user.curvilinearVelocities[-1][0] / timeStep
        d = self.alignments[user.curvilinearPositions[-1][2]].connectedAlignments[2].width + user.geometry
        clearingTime = d / v
        if clearingTime < user.supposedAmberTime:
            return True
        else:
            return False

    def assignValue(self, args):
        self.userInputs[0].distributions['headway'].scale = args.headway - 1
        self.userInputs[0].distributions['speed'].loc = args.speed
        self.userInputs[0].distributions['dn'].loc = args.dn
        self.userInputs[0].distributions['tau'].loc = args.tau
        self.userInputs[0].distributions['length'].loc = args.l
    #
    # def finalize(self, lastInstant):
    #     """replaces users in the correct list according to their status"""
    #     for u in self.users:
    #         if u.timeInterval is not None:
    #             if u.getLastInstant() != lastInstant:
    #                 self.completed.append(u)
    #                 self.users.remove(u)


    def updateControlDevices(self, timeStep):
        '''updates state for control devices'''
        if self.controlDevices is not None:
            for cd in self.controlDevices:
                cd.update(timeStep)

    def userOnTransversalAlignmentsAtInstant(self, user, other, instant):
        """determines if other is on transversal alignment of user at instant"""
        cp = user.getCurvilinearPositionAtInstant(instant)
        if self.alignments[cp[2]].transversalAlignments is not None:
            if other.getCurvilinearPositionAtInstant(instant)[2] in [al.idx for al in self.alignments[cp[2]].transversalAlignments]:
                return True
        else:
            return False

    def getCrossingUsers(self, currentUserAlignment):
        '''returns None if no user is about to cross the intersection, else returns the transversal user'''
        if currentUserAlignment.transversalAlignments is None:
            return None
        else:
            return {al: al.firstUser for al in currentUserAlignment.transversalAlignments}

    def scan(self, transversalAlignments, instant, withCompleted=False):
        """ returns users on transversal alignment ordered by ascending curvilinear position at instant on alignment"""
        potentialTransversalUsers = []
        if transversalAlignments is not None:
            if withCompleted:
                for u in self.users + self.completed:
                    if u.timeInterval is not None:
                        if instant in u.timeInterval:
                            if u.getCurvilinearPositionAtInstant(instant)[2] in [al.idx for al in transversalAlignments]:
                                potentialTransversalUsers.append(u)
            else:
                for u in self.users:
                    if u.timeInterval is not None:
                        if instant in u.timeInterval:
                            if u.getCurvilinearPositionAtInstant(instant)[2] in [al.idx for al in transversalAlignments]:
                                potentialTransversalUsers.append(u)
            if potentialTransversalUsers != []:
                potentialTransversalUsers = sorted(potentialTransversalUsers, key=lambda x: x.getCurvilinearPositionAtInstant(instant)[0], reverse=True)
                return potentialTransversalUsers[0]
            else:
                return None
        else:
            return None

    def getPredictedCrossingPoints(self, user, other, instant):
        """returns predicted crossing points for a pair of users"""
        cp1 = user.getCurvilinearPositionAtInstant(instant)
        cp2 = other.getCurvilinearPositionAtInstant(instant)

        userPredictedTrajectories = self.alignments[cp1[2]].getAllPossibleAlignmentIntersectionSequences()
        otherPredictedTrajectories = self.alignments[cp2[2]].getAllPossibleAlignmentIntersectionSequences()

        crossingPoints = []
        for userTrajectory in userPredictedTrajectories:
            for otherTrajectory in otherPredictedTrajectories:
                _temp = [item for item in userTrajectory if item in otherTrajectory and item is not None]
                crossingPoints.extend(_temp)

        return crossingPoints

    def getNodesFromCrossingPoints(self, user, other, instant):
        """returns nodes of corresponding crossing points"""
        crossingPoints = self.getPredictedCrossingPoints(user, other, instant)
        nodes = []
        if crossingPoints != set():
            for intersection in crossingPoints:
                _temp = [entryAlignment.exitNode for entryAlignment in intersection.entryAlignments]
                nodes.extend(_temp)
            return nodes
        else:
            return None

    def getCrossingPointCurvilinearPosition(self, user, other, instant):
        crossingPoints = self.getPredictedCrossingPoints(user, other, instant)
        if crossingPoints != set():
            curvilinearPositions = []
            for intersection in crossingPoints:
                curvilinearPositions.extend([[entryAlignment.getTotalDistance(), 0, entryAlignment.idx] for entryAlignment in intersection.entryAlignments])

            return curvilinearPositions
        else:
            return None

    def getCrossingPairAtInstant(self, instant):
        '''detection of users for post simulation computation of indicators'''
        al1 = self.intersections[0].entryAlignments[0]
        al2 = self.intersections[0].entryAlignments[1]
        # for al in self.alignments:
        #     connectedAlignmentIndices = al.getConnectedAlignmentIndices()
        #     if connectedAlignmentIndices is not None:
        #         if len(connectedAlignmentIndices) > 1:
        #             break
        #     else:
        #         return None, None
        # al1 = al
        #
        # for alignment in self.alignments:
        #     if alignment.idx != al1.idx:
        #         connectedAlignmentIndices = alignment.getConnectedAlignmentIndices()
        #         if connectedAlignmentIndices is not None:
        #             if len(connectedAlignmentIndices) > 1:
        #                 break
        # al2 = alignment

        userSet1 = al1.getUsersOnAlignmentAtInstant(instant)
        userSet2 = al2.getUsersOnAlignmentAtInstant(instant)
        if len(userSet1) > 0 and len(userSet2) > 0:
            return sorted(userSet1, key=lambda x: x.getCurvilinearPositionAtInstant(instant)[0], reverse=True)[0], sorted(userSet2, key=lambda y: y.getCurvilinearPositionAtInstant(instant)[0], reverse=True)[0]
        elif len(userSet1) == 0 or len(userSet2) == 0:
            return None, None

    def saveTrajectoriesToDB(self, dbName, seed, analysisId):
        self.saveCurvilinearTrajectoriesToSqlite(dbName, seed, analysisId)

    def saveObjects(self, dbName, seed, analysisId):
        with sqlite3.connect(dbName) as connection:
            cursor = connection.cursor()
            objectQuery = "INSERT INTO objects VALUES (?,?,?,?,?,?,?,?,?,?)"
            for obj in self.users + self.completed:
                if obj.timeInterval is not None:
                    cursor.execute(objectQuery, (obj.getNum(), seed, analysisId, obj.getUserType(), obj.tau, obj.d, obj.desiredSpeed, obj.geometry, obj.getFirstInstant(), obj.getLastInstant()))
                    connection.commit()

    def updateFirstUsers(self):
        for al in self.alignments:
            if al.firstUser is None or al.firstUser.getCurvilinearPositionAt(-1)[2] != al.getIdx():
                s = -1
                for u in self.users:
                    p = u.getCurvilinearPositionAt(-1)
                    if p[2] == al.getIdx():
                        if p[0] > s:
                            s = p[0]
                            al.firstUser = u

    def computeMeanVelocities(self, timeStep):
        self.v1 = {0: np.mean([np.mean(u.curvilinearVelocities.positions[0]) / timeStep for u in self.completed if u.getInitialAlignment().idx == 0]), 2: np.mean([np.mean(u.curvilinearVelocities.positions[0]) / timeStep for u in self.completed if u.getInitialAlignment().idx == 2])}
        self.v2 = {0: np.mean([np.mean(u.getTotalDistance() / (len(u.curvilinearPositions) * timeStep)) for u in self.completed if u.getInitialAlignment().idx == 0]), 2: np.mean([np.mean(u.getTotalDistance() / (len(u.curvilinearPositions) * timeStep)) for u in self.completed if u.getInitialAlignment().idx == 2])}

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

    def initDistributions(self, timeStep):
        self.headwayDistribution = self.distributions['headway'].getDistribution(1. / timeStep)
        self.timeArrival = 0.
        self.lengthDistribution = self.distributions['length'].getDistribution()
        self.speedDistribution = self.distributions['speed'].getDistribution(timeStep)
        self.tauDistribution = self.distributions['tau'].getDistribution(1. / timeStep)
        self.dDistribution = self.distributions['dn'].getDistribution()
        self.gapDistribution = self.distributions['criticalGap'].getDistribution(1. / timeStep)
        # self.amberProbabilityDistribution = self.distributions['amberProbability'].getDistribution()

    # def generateHeadways(self, duration):
    #     """ generates a set a headways"""
    #     self.headways = utils.maxSumSample(self.headwayDistribution, duration)
    #     self.cumulatedHeadways = list(itertools.accumulate(self.headways))
    
    def generateTimeArrival(self):
        self.timeArrival += self.headwayDistribution.rvs()

    def getTimeArrival(self):
        return self.timeArrival
        
    def getUserInputDistribution(self, item):
        """returns the distribution parameters for an item : type, name, parameters"""
        return self.distributions[item].getDistribution()

    def initUser(self, userNum, initialCumulatedHeadway, safetyDistance):
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
                                        initialAlignment=self.alignment)
                                        # amberProbability=self.amberProbabilityDistribution.rvs())
        obj.interactions = None
        obj.intersectionEntryInstant = None
        obj.intersectionExitInstant = None
        obj.timeIntervalInAnalysisZone = moving.TimeInterval()
        # obj.timeIntervalInAnalysisZone.first, obj.timeIntervalInAnalysisZone.last = None, None
        if self.lastGeneratedUser is not None:
            obj.leader = self.lastGeneratedUser
            obj.updateD(safetyDistance)
            # print(obj.timeInterval)
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

    def getDistribution(self, f=1.):
        """returns the scipy.stats objects that corresponds to the parameters in Distribution object

        f is a multiplication factor for the distribution"""

        if self.distributionType == 'theoretic':
            if self.distributionName == 'norm':
                return stats.norm(loc=self.loc * f, scale=self.scale * f)
            if self.distributionName == 'truncnorm':
                return stats.truncnorm(loc=self.loc * f, scale=self.scale * f, a=self.a, b=self.b)
            elif self.distributionName == 'expon':
                return stats.expon(loc=self.loc * f, scale=self.scale * f)
            else:
                raise NameError('error in distribution name')
        elif self.distributionType == 'empirical':
            return utils.EmpiricalContinuousDistribution([x * f for x in self.cdf[0]], self.cdf[1])
        elif self.distributionType == 'degenerated':
            return utils.ConstantDistribution(self.degeneratedConstant * f)
        else:
            raise NameError('error in distribution type')

    def getType(self):
        return self.distributionType

    def getName(self):
        if hasattr(self, 'distributionName'):
            return self.distributionName
        else:
            return None

    def getScale(self):
        if hasattr(self, 'scale'):
            return self.scale
        else:
            return None

    def getLoc(self):
        if hasattr(self, 'loc'):
            return self.loc
        else:
            return None

    def getCdf(self):
        if hasattr(self, 'cdf'):
            return self.cdf
        else:
            return None

    def getConstant(self):
        if hasattr(self, 'degeneratedConstant'):
            return self.degeneratedConstant
        else:
            return None

    def getMinThreshold(self):
        if hasattr(self, 'a'):
            return self.a
        else:
            return None

    def getMaxThreshold(self):
        if hasattr(self, 'b'):
            return self.b
        else:
            return None


class Intersection:
    def __init__(self, entryAlignments=None, exitAlignments=None):
        self.entryAlignments = entryAlignments
        self.exitAlignments = exitAlignments

    def setEntryAlignments(self, entryAlignments):
        self.entryAlignments = entryAlignments

    def setExitAlignments(self, exitAlignments):
        self.entryAlignments = exitAlignments

    def getEntryAlignments(self):
        return self.entryAlignments

    def getExitAlignments(self):
        return self.exitAlignments


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


def createNewellMovingObjectsTable(db):
    def createCurvilinearTrajectoryTable(cursor):
        cursor.execute("CREATE TABLE IF NOT EXISTS curvilinear_positions (trajectory_id INTEGER, seed INTEGER, analysis_id INTEGER, frame_number INTEGER, s_coordinate REAL, y_coordinate REAL, lane TEXT, PRIMARY KEY(trajectory_id, seed, analysis_id, frame_number))")

    connection = sqlite3.connect(db)
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS objects (object_id INTEGER, seed INTEGER, analysis_id INTEGER, road_user_type INTEGER, tau REAL, d REAL, desired_speed REAL, geometry REAL, first_instant, last_instant, PRIMARY KEY(object_id, seed, analysis_id))")
    createCurvilinearTrajectoryTable(cursor)
    connection.commit()


def saveTrajectoriesToTable(connection, objects, trajectoryType, seed, analysisId):
    'Saves trajectories in table tableName'
    cursor = connection.cursor()
    if (trajectoryType == 'curvilinear'):
        curvilinearQuery = "INSERT INTO curvilinear_positions VALUES (?,?,?,?,?,?,?)"
        for obj in objects:
            num = obj.getNum()
            frameNum = obj.getFirstInstant()
            for p in obj.getCurvilinearPositions():
                cursor.execute(curvilinearQuery, (num, seed, analysisId, frameNum, p[0], p[1], p[2]))
                frameNum += 1
    else:
        print('Unknown trajectory type {}'.format(trajectoryType))
    connection.commit()


if __name__ == "__main__":
    import doctest

    doctest.testmod()
