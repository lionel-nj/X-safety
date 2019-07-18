import itertools
import sqlite3

import matplotlib.pyplot as plt
import networkx as nx
from scipy import stats
from trafficintelligence import utils, moving

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
            self.connectedAlignmentDistribution = stats.rv_discrete(name='custm', values = (list(range(len(connectedAlignmentIndices))), self.getConnectedAlignmentMovementProportions()))
    
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

    def update(self):
        pass

    def permissionToGo(self, instant, user, world):
        return None


class TrafficLight(ControlDevice):
    states = ['green', 'amber', 'red']

    def __init__(self, idx, alignmentIdx, redTime, greenTime, amberTime):
        super(TrafficLight, self).__init__(idx, alignmentIdx)
        self.redTime = redTime
        self.greenTime = greenTime
        self.amberTime = amberTime
        #self.reset()

    def drawInitialState(self):
        i = stats.randint(0, 3).rvs()
        self.state = TrafficLight.states[i]

    def getState(self):
        """ returns the current color """
        return self.state

    def switch(self):
        """ switches state to next state in the sequence """
        if self.state == 'red':
            self.state = 'green'
        elif self.state == 'amber':
            self.state = 'red'
        else:
            self.state = 'amber'

    def update(self):
        """Updates the current state for a TrafficLight object for the duration of state"""
        if self.state == 'green':
            if self.remainingGreen > 0:
                self.remainingGreen -= 1
            else:
                self.switch()
                self.remainingGreen = self.greenTime
        elif self.state == 'red':
            if self.remainingRed > 0:
                self.remainingRed -= 1
            else:
                self.switch()
                self.remainingRed = self.redTime
        else:
            if self.remainingAmber > 0:
                self.remainingAmber -= 1
            else:
                self.switch()
                self.remainingAmber = self.amberTime

    def reset(self, timeStep):
        """ resets the defaut parameters of a traffic light"""
        self.remainingRed = self.redTime/timeStep
        self.remainingAmber = self.amberTime/timeStep
        self.remainingGreen = self.greenTime/timeStep
        self.drawInitialState()

    def permissionToGo(self, instant, user, world):
        if self.state in ['green', 'amber']:
            return True
        else:
            return False

class StopSign(ControlDevice):
    def __init__(self, idx, alignmentIdx, stopDuration):
        super(StopSign, self).__init__(idx, alignmentIdx)
        self.user = None
        self.stopDuration = stopDuration
        #self.reset()

    def permissionToGo(self, instant, user, world):
        if user.getWaitingTimeAtControlDevice(instant) < self.convertedStopDuration:
            return False
        else:
            if world.estimateGap(user) > user.getCriticalGap(): # todo estimate time of arrival of vehicle
                return True
            else:
                return False

    def reset(self, timeStep):
        '''converts stop duration in simulation time'''
        self.convertedStopDuration = self.stopDuration/timeStep

class YieldSign(ControlDevice):
    def __init__(self, idx, alignmentIdx):
        super(YieldSign, self).__init__(idx, alignmentIdx)
        self.user = None

    def permissionToGo(self, instant, user, world):
        return world.estimateGap(user) > user.getCriticalGap()

# class ETC(ControlDevice):
#     def __init__(self, idx, alignmentIdx, category=1, initialState='green'):
#         super().__init__(idx, category, alignmentIdx)
#         self.initialState = initialState
#         self.states = [self.initialState]


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
        saveTrajectoriesToTable(connection, [user for user in self.completed + self.users if user.timeInterval is not None], 'curvilinear',  seed, analysisId)

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

    def initUsers(self, instant, userNum):
        """Initializes new users """
        for ui in self.userInputs:
            futureCumulatedHeadways = []
            for h in ui.cumulatedHeadways:
                if instant <= h < instant + 1:
                    self.newUsers.append(ui.initUser(userNum, h))
                    userNum += 1
                else:
                    futureCumulatedHeadways.append(h)
            ui.cumulatedHeadways = futureCumulatedHeadways
        return userNum

    def setInserted(self, user):
        self.inserted.append(user)
    
    def setNewlyCompleted(self, user):
        self.newlyCompleted.append(user)
    
    def updateUsers(self, instant):
        self.newlyCompleted = []
        self.inserted = []
        for u in self.newUsers+self.users:
            u.updateCurvilinearPositions(instant, self)
        for u in self.inserted:
            self.newUsers.remove(u)
            self.users.append(u)
        for u in self.newlyCompleted:
            self.users.remove(u)
            self.completed.append(u)

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

    def distanceAtInstant(self, user1, user2, instant, situation, method):
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
                        if situation == 'CF':
                            leader = user1.orderUsersByPositionAtInstant(user2, instant)[0]
                            distance -= leader.geometry

                        G.remove_node('user1')
                        G.remove_node('user2')
                        return distance

            elif method == 'euclidian':
                user1, user2 = user1.orderUsersByPositionAtInstant(user2, instant)
                s1 = user1.getCurvilinearPositionAtInstant(instant)
                s2 = user2.getCurvilinearPositionAtInstant(instant)
                p1 = moving.getXYfromSY(s1[0], s1[1], s1[2], [al.points for al in self.alignments])
                p2 = moving.getXYfromSY(s2[0], s2[1], s2[2], [al.points for al in self.alignments])
                distance = (p1 - p2).norm2()
                if situation == 'CF':
                    distance = (p1 - p2).norm2() - user1.geometry
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

    def prepare(self, timeStep, duration, seed):
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
            ui.generateHeadways(duration/timeStep)

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
                        i +=1
                    if not entryAlignmentsAlreadyInIntersections:
                        self.intersections.append(intersection)

                al.initConnectedAlignmentDistribution()

            # connecting control devices to their alignments
            if self.controlDevices is None:
                al.controlDevice = None
            else:
                for cd in self.controlDevices:
                    if al.idx == cd.alignmentIdx:
                        al.controlDevice = cd
                    else:
                        al.controlDevice = None

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
        self.interactions = {}

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
            #timeToCrossing = (user.getCurrentAlignment().getTotalDistance() - user.getCurvilinearPositionAt(-1)[0])
            for al,crossingUser in crossingUsers.items():
                if crossingUser is not None:
                    p = crossingUser.getCurvilinearPositionAt(-1)
                    if crossingUser.length() >= 2:
                        velocity = crossingUser.getCurvilinearVelocityAt(-1)
                        v = velocity[0]
                    else:
                        v = crossingUser.desiredSpeed
                    if v != 0:
                        d = crossingUser.getCurrentAlignment().getTotalDistance() - p[0]
                        gap = min(gap, d/v)
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

    def finalize(self, lastInstant):
        for u in self.users:
            if u.timeInterval is not None:
                if u.getLastInstant() != lastInstant:
                    self.completed.append(u)
                    self.users.remove(u)

    def updateControlDevices(self):
        '''updates state for control devices'''
        if self.controlDevices is not None:
            for cd in self.controlDevices:
                cd.update()

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
            # crossingUsers = {}
            # for al in currentUserAlignment.transversalAlignments:
            #     s = -1
            #     crossingUser = None
            #     for u in self.users:
            #         p = u.getCurvilinearPositionAt(-1)
            #         if p[2] == al.getIdx():
            #             if p[0] > s:
            #                 s = p[0]
            #                 crossingUser = u
            #     crossingUsers[al] = crossingUser
            # return crossingUsers


        # cp = user.getCurvilinearPositionAtInstant(instant - 1)
        # transversalAlignments = self.alignments[cp[2]].transversalAlignments
        # if instant in user.timeInterval:
        #     if transversalAlignments is not None:
        #         if user.leader is not None:
        #             print(user.num, user.timeInterval, instant)
        #             if user.leader.getCurvilinearPositionAtInstant(instant - 1)[2] != user.getCurvilinearPositionAtInstant(instant - 1):
        #                 return self.scan(transversalAlignments, instant - 1, withCompleted)
        #             else:
        #                 return None
        #         else:
        #             self.scan(transversalAlignments, instant, withCompleted)
        #     else:
        #         return None
        # else:
        #     return None

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

    def updateInteractions(self):
        for user in self.users:
            if user.leader is not None:
                inter = events.Interaction(roadUser1=user, roadUser2=user.leader, useCurvilinear=True)
                self.addInteractions(inter)

            currentAlignment = user.getCurrentAlignment()
            if currentAlignment.getFirstUser().num == user.num:
                if currentAlignment.transversalAlignments is not None:
                    for transversalAlignment in currentAlignment.transversalAlignments:
                        other = transversalAlignment.getFirstUser()
                        if other is not None:
                            inter = events.Interaction(roadUser1=user, roadUser2=other, useCurvilinear=True)
                            self.addInteractions(inter)

    def computeDistances(self, instant):
        for inter in self.interactions:
            print(inter, instant)
            self.interactions[inter].computeDistance(self, instant)

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

    def addInteractions(self, newInter):
        if self.interactions == {}:
            newInter.num = len(self.interactions)
            self.interactions[(newInter.roadUser1.num, newInter.roadUser2.num)] = newInter
        else:
            if not(newInter.roadUserNumbers in [self.interactions[i].roadUserNumbers for i in self.interactions]):
                newInter.num = len(self.interactions)
                self.interactions[(newInter.roadUser1.num, newInter.roadUser2.num)] = newInter


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
        self.headwayDistribution = self.distributions['headway'].getDistribution(1./timeStep)
        self.lengthDistribution = self.distributions['length'].getDistribution()
        self.speedDistribution = self.distributions['speed'].getDistribution(timeStep)
        self.tauDistribution = self.distributions['tau'].getDistribution(1./timeStep)
        self.dDistribution = self.distributions['dn'].getDistribution()
        self.gapDistribution = self.distributions['criticalGap'].getDistribution(1./timeStep)
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
        obj.interactions = None
        if self.lastGeneratedUser is not None:
            obj.leader = self.lastGeneratedUser
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

    def getDistribution(self, f = 1.):
        """returns the scipy.stats objects that corresponds to the parameters in Distribution object

        f is a multiplication factor for the distribution"""

        if self.distributionType == 'theoretic':
            if self.distributionName == 'norm':
                return stats.norm(loc=self.loc*f, scale=self.scale*f)
            if self.distributionName == 'truncnorm':
                return stats.truncnorm(loc=self.loc*f, scale=self.scale*f, a=self.a, b=self.b)
            elif self.distributionName == 'expon':
                return stats.expon(loc=self.loc*f, scale=self.scale*f)
            else:
                raise NameError('error in distribution name')
        elif self.distributionType == 'empirical':
            return utils.EmpiricalContinuousDistribution([x*f for x in self.cdf[0]], self.cdf[1])
        elif self.distributionType == 'degenerated':
            return utils.ConstantDistribution(self.degeneratedConstant*f)
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
    if(trajectoryType == 'curvilinear'):
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
