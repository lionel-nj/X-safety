import copy
import itertools

import matplotlib.pyplot as plt
import networkx as nx
from scipy import stats
from trafficintelligence import utils, moving

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

    def build(self, entryPoint, exitPoint, others=None):
        """builds an alignments from points,
         entryPoint and exitPoint : moving.Point
         others : list of intermediate moving.points"""

        if others is None:
            self.points = moving.Trajectory.fromPointList([entryPoint, exitPoint])
        else:
            self.points = moving.Trajectory.fromPointList([entryPoint] + others + [exitPoint])

    def addPoint(self, x, y):
        self.points.addPositionXY(x, y)

    def setPoint(self, i, x, y):
        self.points.setPositionXY(i, x, y)

    def insertPointAt(self, p, i):
        """inserts a moving.Point p at index i """
        previousPart = moving.Trajectory()

        for k in range(0, i):
            previousPart.addPosition(self.points[k])

        previousPart.addPosition(p)

        for k in range(i, len(self.points)):
            previousPart.addPosition(self.points[k])

        self.points = previousPart

    @staticmethod
    def isBetween(a, b, c):
        return moving.Point.distanceNorm2(a, c) + moving.Point.distanceNorm2(c, b) == moving.Point.distanceNorm2(a, b)

    def isConnectedTo(self, other):
        """boolean, detemines if two alignments are connected"""
        if other.idx in self.connectedAlignmentIndices or self.idx in other.connectedAlignmentIndices:
            return True
        else:
            return False

    def getPoint(self, i):
        """returns i-th point of an alignment"""
        return self.points[i]

    def getFirstPoint(self):
        "returns the first point of an alignment"
        return self.points[0]

    def getLastPoint(self):
        "returns the last point of an alignment"
        return self.points[-1]

    def isStartOf(self, point):
        "boolean : True if a moving.Point is the first point of an alignment"
        if self.getFirstPoint().x == point.x and self.getFirstPoint().y == point.y:
            return True
        else:
            return False

    def isEndOf(self, point):
        "boolean : True if a moving.Point is the last point of an alignment"

        if self.getLastPoint().x == point.x and self.getLastPoint().y == point.y:
            return True
        else:
            return False

    def addUserToAlignment(self, user):
        """adds an user to self.vehicles or self.user """
        if self.vehicles:
            self.vehicles.append(user)
        else:
            self.vehicles = [user]

    def isReachableFrom(self, other):
        """returns boolean, True if an alignment is reachable from another one"""
        if other.connectedAlignmentIndices is not None:
            return self.idx in other.connectedAlignmentIndices
        else:
            return False

    def getNextAlignment(self, nextS, user, instant):
        '''Returns the list of alignments to the next alignment and longitudinal coordinate S on that alignment for objects finding their path'''
        # warning, recursive function
        alignmentDistance = self.getTotalDistance()
        if nextS <= alignmentDistance:
            return [self], nextS
        elif self.connectedAlignments is not None:
            # TODO use proportions at connection
            # TODO check control devices
            cd = self.getControlDevice()
            if cd is not None:
                cd.user = user
                if cd.permissionToGo(instant):
                    alignments, s = self.connectedAlignments[0].getNextAlignment(nextS - alignmentDistance, user, instant)
                else:
                    alignments, s = [self], self.getTotalDistance()
            else:
                alignments, s = self.connectedAlignments[0].getNextAlignment(nextS - alignmentDistance, user, instant)
            return [self] + alignments, s
        else:  # simulation finished, exited network
            return None, None

    def getControlDevice(self):
        return self.controlDevice

    def getCumulativeDistance(self, i):
        return self.points.cumulativeDistances[i]

    def getTotalDistance(self):
        return self.points.getTotalDistance()

    def getId(self):
        return self.idx

    def getEntryNode(self):
        return self.entryNode

    def getExitNode(self):
        return self.exitNode

    def getConnectedAlignmentIndices(self):
        return self.connectedAlignmentIndices


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


class TrafficLight(ControlDevice):
    def __init__(self, idx, alignmentIdx, redTime, greenTime, amberTime, initialState):
        super(TrafficLight, self).__init__(idx, alignmentIdx)
        self.redTime = redTime
        self.greenTime = greenTime
        self.amberTime = amberTime
        self.initialState = initialState
        self.state = initialState
        self.remainingRed = copy.deepcopy(redTime)
        self.remainingAmber = copy.deepcopy(amberTime)
        self.remainingGreen = copy.deepcopy(greenTime)

    def getStateAtInstant(self, t):
        """ returns art for the current color """
        return self.states[t]

    def switch(self):
        """ swith state to next state in the sequence """
        if self.state == 'red':
            self.state = 'green'
        elif self.state == 'amber':
            self.state = 'red'
        else:
            self.state = 'amber'

    def cycle(self, timeStep):
        """ displays the current state for a TrafficLight object for the duration of state"""
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
        self.remainingRed = copy.deepcopy(self.redTime)
        self.remainingAmber = copy.deepcopy(self.amberTime)
        self.remainingGreen = copy.deepcopy(self.greenTime)

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

    def cycle(self, timeStep):
        pass

    def getStateAtInstant(self, t=None):
        pass

    def reset(self):
        self.user = None

    def permissionToGo(self, instant):
        if not hasattr(self.user, 'arrivalInstant'):
            self.user.arrivalInstant = instant
        if instant < self.user.arrivalInstant + self.stopDuration:
            return False
        else:
            self.user = None
            return True


class YieldSign(ControlDevice):
    def __init__(self, idx, alignmentIdx):
        super(YieldSign, self).__init__(idx, alignmentIdx)

    def cycle(self):
        pass

    def getStateAtInstant(self, t=None):
        pass

    def reset(self):
        pass

    def permissionToGo(self, instant):
        pass

# class ETC(ControlDevice):
#     def __init__(self, idx, alignmentIdx, category=1, initialState='green'):
#         super().__init__(idx, category, alignmentIdx)
#         self.initialState = initialState
#         self.states = [self.initialState]
#
#     def cycle(self):
#         pass
#     def getStateAtInstant(self, t):
# pass


class World:
    """Description of the world, including the road (alignments), control devices (signs, traffic lights) and crossing point """

    def __init__(self, alignments=None, controlDevices=None, userInputs=None):
        self.alignments = alignments  # liste d alignements
        self.userInputs = userInputs  # liste des intersections (objets)
        self.controlDevices = controlDevices  # liste de CD

    def __repr__(self):
        return "alignments: {}, control devices: {}, user inputs: {}".format(self.alignments, self.controlDevices,
                                                                             self.userInputs)

    @staticmethod
    def load(filename):
        """loads a yaml file"""
        return toolkit.loadYaml(filename)

    def save(self, filename):
        """saves data to yaml file"""
        toolkit.saveYaml(filename, self)

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

    def getControlDevices(self):
        return self.controlDevices

    def getAlignmentById(self, idx):  # to remove
        '''Returns an alignment given its id'''
        return getItemByIdx(self.alignments, idx)

    def getControlDeviceById(self, idx):  # to remove
        """get an control device given its id"""
        return getItemByIdx(self.controlDevices, idx)

    def getUserInputById(self, idx):
        """get an user input given its id"""
        for ui in self.userInputs:
            if ui.idx == idx:
                return ui
        print('userInputsIdx does not match any existing alignment')
        return None

    def getUserByNum(self, userNum):
        """returns an user given its num"""
        for user in self.users+self.newlyCompleted+self.completed:
            if user.num == userNum:
                return user
        print("userNum does not match any existing user")
        return None

    def initUsers(self, i, timeStep, userNum):
        """Initializes new users """
        for ui in self.userInputs:
            futureCumulatedHeadways = []
            for h in ui.cumulatedHeadways:
                if i <= h / timeStep < i + 1:
                    self.users.append(ui.initUser(userNum, h))
                    userNum += 1
                else:
                    futureCumulatedHeadways.append(h)
            ui.cumulatedHeadways = futureCumulatedHeadways
        return userNum

    def updateUsers(self, i, timeStep):
        self.newlyCompleted = []
        for u in self.users:
            u.updateCurvilinearPositions(i, timeStep, self)
        for u in self.newlyCompleted:
            self.users.remove(u)
            self.completed.append(u)

    @staticmethod
    def hasBeenOnAlignment(user, alignmentIdx):
        """determines if a vehicles has circulated on an alignment"""
        return alignmentIdx in user.curvilinearPositions.lanes

    def getPreviouslyOccupiedAlignmentsLength(self, user):
        """returns the length of the alignments a vehicle has previously travelled on """
        s = 0
        if user.curvilinearPositions is not None:
            alignmentIndices = list(set(user.curvilinearPositions.lanes))
            alignmentIndices.remove(user.curvilinearPositions.lanes[-1])
            if alignmentIndices != []:
                for indices in alignmentIndices:
                    s += self.getAlignmentById(indices).getTotalDistance()
            else:
                s = 0
        return s

    def initNodesToAlignments(self):
        """sets an entry and an exit node to each alignment"""
        al = self.getAlignmentById(self.userInputs[0].getAlignmentIdx())
        al.entryNode = al.idx
        al.exitNode = al.idx + 1
        if al.connectedAlignmentIndices is not None:
            for connectedAlignmentIdx in al.getConnectedAlignmentIndices():
                self.getAlignmentById(connectedAlignmentIdx).entryNode = al.exitNode
                self.getAlignmentById(connectedAlignmentIdx).exitNode = connectedAlignmentIdx + 1
            centerNode = al.exitNode
        for ui in self.userInputs:
            if ui.getId() != self.userInputs[0].getId():
                self.getAlignmentById(ui.getAlignmentIdx()).entryNode = ui.getAlignmentIdx() + 1
                self.getAlignmentById(ui.getAlignmentIdx()).exitNode = centerNode

    def initGraph(self):
        """sets graph attribute to self"""
        G = nx.Graph()
        self.initNodesToAlignments()
        edgesProperties = []
        for al in self.alignments:
            edgesProperties.append((al.getEntryNode(), al.getExitNode(), al.getTotalDistance()))
        G.add_weighted_edges_from(edgesProperties)
        if self.controlDevices is not None:
            for cdIdx, cd in enumerate(self.getControlDevices()):
                controlDevice = "cd{}".format(cdIdx)
                G.add_node(controlDevice)
                origin = self.getAlignmentById(cd.getAlignmentIdx()).getEntryNode()
                target = self.getAlignmentById(cd.getAlignmentIdx()).getExitNode()
                weight = self.getAlignmentById(cd.getAlignmentIdx()).getTotalDistance()
                G.add_weighted_edges_from([(origin, controlDevice, weight), (controlDevice, target, 0)])
        self.graph = G

    def distanceAtInstant(self, user1, user2, instant):
        """"computes the distance between 2 users"""
        if user1.getFirstInstant() <= instant and user2.getFirstInstant() <= instant:

            if moving.Interval.intersection(user1.timeInterval, user2.timeInterval) is not None:
                user1AlignmentIdx = user1.getCurvilinearPositionAtInstant(instant)[2]
                user2AlignmentIdx = user2.getCurvilinearPositionAtInstant(instant)[2]
                if user1AlignmentIdx == user2AlignmentIdx:
                    return abs(user1.getDistanceFromOriginAtInstant(instant, self)[0] - user2.getDistanceFromOriginAtInstant(instant, self)[0]) - user1.orderUsersByFirstInstant(user2)[0].geometry
                else:
                    user1UpstreamDistance = user1.getCurvilinearPositionAtInstant(instant)[0]
                    user1DownstreamDistance = self.getAlignmentById(user1.getCurvilinearPositionAtInstant(instant)[2]).getTotalDistance() - user1UpstreamDistance
                    user2UpstreamDistance = user2.getCurvilinearPositionAtInstant(instant)[0]
                    user2DownstreamDistance = self.getAlignmentById(user2.getCurvilinearPositionAtInstant(instant)[2]).getTotalDistance() - user2UpstreamDistance

                    G = self.graph

                    G.add_node('user1')
                    G.add_node('user2')

                    user1Origin = self.getAlignmentById(user1AlignmentIdx).entryNode
                    user1Target = self.getAlignmentById(user1AlignmentIdx).exitNode
                    user2Origin = self.getAlignmentById(user2AlignmentIdx).entryNode
                    user2Target = self.getAlignmentById(user2AlignmentIdx).exitNode

                    G.add_weighted_edges_from([(user1Origin, 'user1', user1UpstreamDistance)])
                    G.add_weighted_edges_from([('user1', user1Target, user1DownstreamDistance)])

                    G.add_weighted_edges_from([(user2Origin, 'user2', user2UpstreamDistance)])
                    G.add_weighted_edges_from([('user2', user2Target, user2DownstreamDistance)])
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
        else:
            print('user do not coexist, therefore can not compute distance')

    def getLinkedAlignments(self, alignmentIdx):
        """return the list of all alignments that are un-directly linked to an alignment"""
        al = self.getAlignmentById(alignmentIdx)
        linkedAlignments = []
        if al.connectedAlignmentIndices:
            for el in al.connectedAlignmentIndices:
                linkedAlignments.append(el)
                if self.getAlignmentById(el).connectedAlignmentIndices:
                    linkedAlignments = linkedAlignments + self.getAlignmentById(el).connectedAlignmentIndices
        return linkedAlignments

    def travelledAlignments(self, user, instant):
        """"returns a list of the alignments that user travelled on"""
        if instant is not None:
            alignments = list(set(user.curvilinearPositions.lanes[:instant - user.timeInterval.first]))
            travelledAlignments = []
            for alIndices in alignments:
                travelledAlignments.append(self.getAlignmentById(alIndices).points)
            return travelledAlignments
        else:
            alignments = list(set(user.curvilinearPositions.lanes))
            travelledAlignments = []
            for alIndices in alignments:
                travelledAlignments.append(self.getAlignmentById(alIndices).points)
            return travelledAlignments

    def duplicateLastVelocities(self):
        for user in self.users:
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
            if al.connectedAlignmentIndices is not None:
                al.connectedAlignments = [self.alignments[connectedAlignmentIdx] for connectedAlignmentIdx in al.connectedAlignmentIndices]
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

        # initializing the lisfs of users
        self.users = []
        self.completed = []

    def getIntersectionCPAtInstant(self, user, instant):
        alIdx = user.getCurvilinearPositionAtInstant(instant)[2]
        return self.getIntersectionCP(alIdx)

    def getIntersectionCP(self, alIdx):
        """"returns the curvilinear positions of the crossing point on all its alignments
        alIdx : alignment to project on"""
        # intersectionCP = self.getAlignmentById(alIdx).getCumulativeDistances(-1
        # for al in self.alignments:
        #     if al.connectedAlignmentIndices is not None:
        #         if alIdx in al.connectedAlignmentIndices:
        #             intersectionCP += self.getAlignmentById(al.idx).getCumulativeDistances(-1
        # return intersectionCP
        al = self.getAlignmentById(alIdx)
        if al.connectedAlignmentIndices is None:
            return 0
        else:
            return al.getTotalDistance()

    def getIncomingTrafficAlignmentIdx(self, user):
        """"returns the alignment id of the adjacent alignment where the traffic comes from"""

        # self.getUserCurrentAlignment(user)
        # if instant in list(user.timeInterval):
        _temp = user.currentAlignment.connectedAlignmentIndices
        if _temp is not None:
            for al in self.alignments:  # determiner l'alignement sur lequel le traffic adjacent arrive
                if al.idx != user.currentAlignment.idx:
                    if al.connectedAlignmentIndices is not None:
                        return al.idx

    def checkTraffic(self, user, instant):
        """"returns the closest user to cross the intersection in the adjacent alignments"""
        # todo :A revoir suite a la modification de getIntersectionCP
        if instant in list(user.timeInterval):
            lane = self.getIncomingTrafficAlignmentIdx(user)
            if lane is not None:
                intersectionCP = self.getIntersectionCP(lane)
                userIntersectionCP = self.getAlignmentById(user.getCurvilinearPositionAtInstant(instant)[2]).getTotalDistance()
                if user.leader is not None:
                    if user.leader.getCurvilinearPositionAtInstant(instant)[0] > userIntersectionCP:
                        worldUserList = []
                        for k in range(len(self.userInputs)):
                            worldUserList.append(self.getNotNoneVehiclesInWorld()[k])
                        for ui in self.userInputs:
                            if ui.alignmentIdx == lane:
                                uiIdx = ui.idx
                                break
                        adjacentUsers = worldUserList[uiIdx]
                        incomingUsers = []
                        for adUser in adjacentUsers:
                            if instant in list(adUser.timeInterval):
                                if adUser.getCurvilinearPositionAtInstant(instant)[0] <= intersectionCP:
                                    incomingUsers.append(adUser)
                        sortedUserList = sorted(incomingUsers, key=lambda x: x.getCurvilinearPositionAtInstant(instant)[0], reverse=True)
                        if sortedUserList != []:
                            user.comingUser = sortedUserList[0]
                    else:
                        user.comingUser = None
                else:
                    worldUserList = []
                    for k in range(len(self.userInputs)):
                        worldUserList.append(self.getNotNoneVehiclesInWorld()[k])
                    for ui in self.userInputs:
                        if ui.alignmentIdx == lane:
                            uiIdx = ui.idx
                            break
                    adjacentUsers = worldUserList[uiIdx]
                    incomingUsers = []
                    for adUser in adjacentUsers:
                        if instant in list(adUser.timeInterval):
                            if adUser.getCurvilinearPositionAtInstant(instant)[0] <= intersectionCP:
                                incomingUsers.append(adUser)
                    sortedUserList = sorted(incomingUsers, key=lambda x: x.getCurvilinearPositionAtInstant(instant)[0],
                                            reverse=True)
                    if sortedUserList != []:
                        user.comingUser = sortedUserList[0]

    def estimateGap(self, user, instant):
        """returns an estimate of the gap at X intersection, based on the speed of the incoming vehicle,
        and the distance remaining between the center of the intersection"""
        if user.timeInterval is not None:
            self.checkTraffic(user, instant)
            if user.comingUser is None:
                return float('inf')
            else:
                v = user.comingUser.getCurvilinearVelocityAtInstant(instant)[0] / self.timeStep
                if v != 0:
                    d = self.distanceAtInstant(user.comingUser, self.getAlignmentById(user.getCurvilinearPositionAtInstant(instant)[2]).controlDevice, instant)
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

    def getControlDeviceCategory(self, cdIdx):
        return self.getControlDeviceById(cdIdx).category

    def isGapAcceptable(self, user, instant):
        if user.criticalGap < self.estimateGap(user, instant):
            return True
        else:
            return False

    def isClearingTimeAcceptable(self, user, timeStep):
        # todo : a verifier
        v = user.curvilinearVelocities[-1][0] / timeStep
        d = self.getAlignmentById(user.curvilinearPositions[-1][2]).connectedAlignments[2].width + user.geometry
        clearingTime = d / v
        if clearingTime < user.supposedAmberTime:
            return True
        else:
            return False

    def getIntersectionXYcoords(self):
        for al in self.alignments:
            if al.connectedAlignmentIndices is not None and len(al.connectedAlignmentIndices) > 1:
                break
        try:
            intersection = \
                al.points.getLineIntersections(self.getAlignmentById(al.connectedAlignmentIndices[1]).points[0],
                                               self.getAlignmentById(al.connectedAlignmentIndices[1]).points[1])[1]
            return intersection[0]
        except:
            return None

    def getControlDevicePositionOnAlignment(self, alIdx):
        al = self.getAlignmentById(alIdx)
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

    def resetControlDevices(self):
        """resets original information for traffic lights"""
        if self.controlDevices is not None:
            for cd in self.controlDevices:
                cd.reset()

    def getUsersSituationAtInstant(self, user, other, instant):
        """returns CF if car are in a CF situation
        X1 if both cars are past the intersection
        X2 if both cars are before the intersection
        X3 if one of the cars is before the intersection and the other one is past it
        nb: if cars are in a CF situation but not leading, X1, X2 OR X3 is returned, to be improved ... """

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

    def getControlDevices(self):
        return self.controlDevices


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

    @staticmethod
    def distanceGap(sLeader, sFollowing, lengthLeader):
        """calculates distance gaps between two vehicles"""
        distance = sLeader - sFollowing - lengthLeader
        return distance

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

    def getId(self):
        return self.idx


class CarGeometry:
    def __init__(self, length=None, width=None, polygon=None):
        self.width = width
        self.length = length
        self.polygon = polygon


class Distribution(object):
    def __init__(self, distributionType, distributionName=None, loc=None, scale=None, cdf=None,
                 degeneratedConstant=None):
        self.loc = loc
        self.cdf = cdf
        self.scale = scale
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

        if self.distributionType == 'theoric':
            if self.distributionName == 'norm':
                return stats.norm(loc=self.loc, scale=self.scale)
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

    def getName(self):
        return self.distributionName

    def getType(self):
        return self.distributionType

    def getScale(self):
        return self.scale

    def getLoc(self):
        return self.loc

    def getCdf(self):
        return self.cdf

    def getConstant(self):
        return self.degeneratedConstant


if __name__ == "__main__":
    import doctest

    doctest.testmod()
