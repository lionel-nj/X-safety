import copy
import itertools

import matplotlib.pyplot as plt
import networkx as nx
from scipy import stats
from trafficintelligence import utils, moving

import agents
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

    def getUsersNum(self):
        """returns a user by its num"""
        usersNum = []
        for user in self.vehicles:
            usersNum.append(user.num)
        return usersNum

    def getNextAlignment(self, user, nextPosition):
        # visitedAlignmentsLength = user.visitedAlignmentsLength
        deltap = user.currentAlignment.getCumulativeDistances(-1) - nextPosition
        if deltap < 0:  # si on est sorti de l'alignement
            if self.connectedAlignments is not None:
                user.currentAlignment = self.connectedAlignments[0]
                return self.connectedAlignments[0], nextPosition%self.getCumulativeDistances(-1)  # todo : modifier selon les proportions de mouvements avec une variable aleatoire uniforme
            else:
                return None, None
        else:  # si on reste sur l'alignement
            return self, nextPosition

    def getCumulativeDistances(self, idx):
        return self.points.cumulativeDistances[idx]


class ControlDevice:
    """class for control devices :stop signs, traffic light etc ...
    adapted from traffic_light_simulator package in pip3"""

    def __init__(self, idx, alignmentIdx): # , category
        self.idx = idx
        #self.category = category
        self.alignmentIdx = alignmentIdx

    # categories = {1: 'stop',
    #               2: 'traffic light',
    #               3: 'yield',
    #                  4: 'etc'}

    # def getCharCategory(self):
    #     """returns a chain of character describing the category of self"""
    #     return self.categories[self.category]


class TrafficLight(ControlDevice):
    def __init__(self, idx, alignmentIdx, redTime, greenTime, amberTime, initialState):
        #category = 2
        super(TrafficLight,self).__init__(idx, alignmentIdx)
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
            if self.remainingGreen > 1:
                self.remainingGreen -= timeStep
            else:
                self.switch()
                self.remainingGreen = self.greenTime
        elif self.state == 'red':
            if self.remainingRed > 1:
                self.remainingRed -= timeStep
            else:
                self.switch()
                self.remainingRed = self.redTime
        else:
            if self.remainingAmber > 1:
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


class StopSign(ControlDevice):
    def __init__(self, idx, alignmentIdx, timeAtStop):
        #category = 1
        super(StopSign, self).__init__(idx, alignmentIdx)
        self.user = None
        self.timeAtStop = timeAtStop

    def cycle(self, timeStep):
        pass

    def getStateAtInstant(self, t=None):
        pass

    def reset(self):
        self.userTimeAtStop = 0
        self.user = None


class YieldSign(ControlDevice):
    def __init__(self, idx, alignmentIdx):
        #category = 3
        super(YieldSign, self).__init__(idx, alignmentIdx)

    def cycle(self):
        pass

    def getStateAtInstant(self, t=None):
        pass

    def reset(self):
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

    def plotUserTrajectories(self, timeStep):
        plt.figure()
        for u in self.users:
            if u.timeInterval is not None:
                u.plotCurvilinearPositions()
        for u in self.completed:
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

    def getAlignmentById(self, idx):
        """get an alignment given its id"""
        try:
            idList = [el.idx for el in self.alignments]
            if idx not in idList:
                print('wrong alignment index({})'.format(idx))
                print(idx)
            else:
                for al in self.alignments:
                    if al.idx == idx:
                        return al
        except:
            print('alignment idx does not match any existing alignment')
            return None

    def getControlDeviceById(self, idx):
        """get an control device given its id"""
        try:
            idList = [el.idx for el in self.controlDevices]
            if idx not in idList:
                print('wrong controlDevice index({})'.format(idx))
            else:
                for cd in self.controlDevices:
                    if cd.idx == idx:
                        return cd
        except:
            print('controlDeviceIdx does not match any existing control device')
            return None

    def getUserInputById(self, idx):
        """get an user input given its id"""
        try:
            idList = [el.idx for el in self.userInputs]
            if idx not in idList:
                print('wrong userInput index({})'.format(idx))
            else:
                for ui in self.userInputs:
                    if ui.idx == idx:
                        return ui
        except:
            print('userInputsIdx does not match any existing alignment')
            return None

    def getUserByNum(self, userNum):
        """returns an user given its num"""
        userNums = []
        for user in self.users:
            userNums.append(user.num)
        idx = userNums.index(userNum)
        return self.users[idx]

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

    def getNotNoneVehiclesInWorld(self):
        """returns all vehicles that have been launched on their initial alignment : user.initialAlignment"""
        users = [[] for _ in range(len(self.userInputs))]
        for ui in self.userInputs:
            for user in ui.users:
                if user.timeInterval is not None and len(user.curvilinearVelocities) > 0:
                    users[ui.idx].append(user)
        return users

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
                    s += self.getAlignmentById(indices).getCumulativeDistances(-1)
            else:
                s = 0
        return s

    def isFirstGeneratedUser(self, user):
        """determines if an user is the first one that has been computed"""
        for userInput in self.userInputs:
            if not userInput.isFirstGeneratedUser(user):
                pass
            else:
                return True
        return False

    def initNodesToAlignments(self):
        """sets an entry and an exit node to each alignment"""
        al = self.getAlignmentById(self.userInputs[0].alignmentIdx)
        al.entryNode = al.idx
        al.exitNode = al.idx + 1
        if al.connectedAlignmentIndices is not None:
            for connectedAlignmentIdx in al.connectedAlignmentIndices:
                self.getAlignmentById(connectedAlignmentIdx).entryNode = al.exitNode
                self.getAlignmentById(connectedAlignmentIdx).exitNode = connectedAlignmentIdx + 1
            centerNode = al.exitNode
        for ui in self.userInputs:
            if ui.idx != self.userInputs[0].idx:
                self.getAlignmentById(ui.alignmentIdx).entryNode = self.getAlignmentById(ui.alignmentIdx).idx + 1
                self.getAlignmentById(ui.alignmentIdx).exitNode = centerNode

    def initGraph(self):
        """sets graph attribute to self"""
        G = nx.Graph()
        self.initNodesToAlignments()
        edgesProperties = []
        for al in self.alignments:
            edgesProperties.append(
                (al.entryNode, al.exitNode, al.getCumulativeDistances(-1)))
        G.add_weighted_edges_from(edgesProperties)
        if self.controlDevices is not None:
            for cdIdx, cd in enumerate(self.controlDevices):
                controlDevice = "cd{}".format(cdIdx)
                G.add_node(controlDevice)
                origin = self.getAlignmentById(cd.alignmentIdx).entryNode
                target = self.getAlignmentById(cd.alignmentIdx).exitNode
                weight = self.getAlignmentById(cd.alignmentIdx).getCumulativeDistances(-1)
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
                    user1DownstreamDistance = self.getAlignmentById(user1.getCurvilinearPositionAtInstant(instant)[2]).getCumulativeDistances(-1) - user1UpstreamDistance
                    user2UpstreamDistance = user2.getCurvilinearPositionAtInstant(instant)[0]
                    user2DownstreamDistance = self.getAlignmentById(user2.getCurvilinearPositionAtInstant(instant)[2]).getCumulativeDistances(-1) - user2UpstreamDistance

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

    def prepare(self):
        """"links the alignments, creating a connectedAlignments member to each alignments of self
        creates am empty user list for each user input,

        links a controlDevice to its alignment, if an alignment has no control Device assigns None"""

        # compute cumulative distances for each alignment :
        for al in self.alignments:
            al.points.computeCumulativeDistances()

        # resetting all control devices to default values
        self.resetControlDevices()

        # connecting alignments
        for al in self.alignments:
            al.connectedAlignments = []
            if al.connectedAlignmentIndices is not None:
                for connectedAlignments in al.connectedAlignmentIndices:
                    al.connectedAlignments.append(self.getAlignmentById(connectedAlignments))
            else:
                al.connectedAlignments = None

            # connecting control devices to their alignments
            if self.controlDevices is not None:
                for cd in self.controlDevices:
                    if al.idx == cd.alignmentIdx:
                        al.controlDevice = cd
                    else:
                        al.controlDevice = None
            else:
                al.controlDevice = None

        # initializing the last generated user to None for each userInput
        for ui in self.userInputs:
            ui.lastGeneratedUser = None

        # linking self to its graph
        self.initGraph()

        # initializing a lisf of users that are no longer computed to empty
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
            return al.getCumulativeDistances(-1)

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
                userIntersectionCP = self.getAlignmentById(user.getCurvilinearPositionAtInstant(instant)[2]).getCumulativeDistances(-1)
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
            s += al.getCumulativeDistances(-1)
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
            return al.getCumulativeDistances(-1)

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

    def exit(self, lastInstant):
        for u in self.users:
            if u.timeInterval is not None:
                if u.getLastInstant() != lastInstant:
                    self.completed.append(u)
                    self.users.remove(u)


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
                                        initialAlignmentIdx=self.alignmentIdx,
                                        amberProbability=self.amberProbabilityDistribution.rvs())
        if self.lastGeneratedUser is not None:
            # obj.leader = self.generatedNum[-1]
            obj.leader = self.lastGeneratedUser
        self.lastGeneratedUser = obj
        return obj

    def getUserByNum(self, num):
        """gets an user by its id"""
        for user in self.alignment.vehicles:
            if user.num == num:
                return user

    def isFirstGeneratedUser(self, user):
        """determines if an user is the first that has been computed"""
        if self.alignment.vehicles:
            return True
        else:
            return self.alignment.vehicles[0].num == user.num


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


if __name__ == "__main__":
    import doctest

    doctest.testmod()
