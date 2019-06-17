import itertools

from trafficintelligence import utils, moving

import agents
# import moving
import toolkit


class Alignment:
    """Description of road lanes (centre line of a lane)
    point represents the lane geometry (type is moving.Trajectory) """

    def __init__(self, idx=None, points=None, width=None, controlDevice=None, name=None):
        self.idx = idx
        self.name = name
        self.width = width
        self.points = points
        self.controlDevice = controlDevice

    def save(self, filename):
        toolkit.saveYaml(filename, self)

    @staticmethod
    def load(filename):
        return toolkit.loadYaml(filename)

    def plot(self, options='', **kwargs):
        import matplotlib.pyplot as plt
        self.points.plot(options, kwargs)
        plt.plot()

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

    def plotTrajectories(self):
        import matplotlib.pyplot as plt
        x = []
        t = []
        for idx, user in enumerate(self.vehicles):
            t.append([])
            x.append(user.curvilinearPositions.positions[0])
            for time in range(user.getFirstInstant(), len(user.curvilinearPositions) + user.getFirstInstant()):
                t[idx].append(time * self.timeStep)

            plt.plot(t[idx], x[idx])
        plt.show()

    def getNextAlignment(self, user, nextPosition):
        # visitedAlignmentsLength = user.visitedAlignmentsLength
        deltap = user.visitedAlignmentsLength - nextPosition
        if deltap < 0:  # si on est sorti de l'alignement
            if self.connectedAlignments is not None:
                return self.connectedAlignments[0] # todo : modifier selon les proportions de mouvements avec une variable aleatoire uniforme
            else:
                user.inSimulation = False
                return self
        else:  # si on reste sur l'alignement
            return self


class ControlDevice:
    """class for control deveices :stop signs, traffic light etc ...
    adapted from traffic_light_simulator package in pip3"""

    def __init__(self, idx, category, alignmentIdx):
        self.idx = idx
        self.category = category
        self.alignmentIdx = alignmentIdx

    categories = {1: 'stop',
                  2: 'traffic light',
                  3: 'yield',
                  4: 'etc'}

    def getCharCategory(self):
        """returns a chain of character describing the category of self"""
        return self.categories[self.category]


class TrafficLight(ControlDevice):
    def __init__(self, idx, alignmentIdx, redTime, greenTime, amberTime, state):
        import copy
        category = 2
        super().__init__(idx, category, alignmentIdx)
        self.redTime = redTime
        self.greenTime = greenTime
        self.amberTime = amberTime
        self.state = state
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


class StopSign(ControlDevice):
    def __init__(self, idx, alignmentIdx):
        category = 1
        super().__init__(idx, category, alignmentIdx)
        self.user = None

    def cycle(self, timeStep):
        pass

    def getStateAtInstant(self, t=None):
        pass

    def permissionToGo(self, user):
        if self.userTimeAtStop < self.timeAtStop:
            self.userTimeAtStop += self.timeStep
            user.go = False
        else:
            user.go = True
            self.user = None
            self.userTimeAtStop = 0


class Yield(ControlDevice):
    def __init__(self, idx, alignmentIdx):
        initialState = 'green'
        category = 3
        super().__init__(idx, category, alignmentIdx)
        self.initialState = initialState

    def cycle(self):
        pass

    def getStateAtInstant(self, t=None):
        return self.initialState


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

    def __init__(self, alignments=None, controlDevices=None, intersections=None):
        self.alignments = alignments  # liste d alignements
        self.intersections = intersections  # liste des intersections (objets)
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
        import matplotlib.pyplot as plt
        for a in self.alignments:
            a.points.plot(options, kwargs)
        plt.plot()

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
                    # if len(self.users) > 1:
                    #     self.users[-1].leader = self.users[-2]
                    # else:
                    #     self.users[-1].leader = None
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

    def getVisitedAlignmentsCumulatedDistance(self, user):
        """returns total length of the alignment the user had been assigned to """
        visitedAlignmentsIndices = list(set(user.curvilinearPositions.lanes))
        visitedAlignmentsCumulativeDistance = 0
        for alignmentIdx in visitedAlignmentsIndices:
            visitedAlignmentsCumulativeDistance += self.getAlignmentById(alignmentIdx).points.cumulativeDistances[-1]

        return visitedAlignmentsCumulativeDistance

    def getUserDistanceOnAlignmentAt(self, user, t):
        """returns the travelled distance of an user on its current alignment"""
        visitedAlignments = list(set(user.curvilinearPositions.lanes[:(t - user.getFirstInstant() + 1)]))
        visitedAlignments.remove(user.curvilinearPositions.lanes[t - user.getFirstInstant()])
        s = 0
        for indices in visitedAlignments:
            s += self.getAlignmentById(indices).points.cumulativeDistances[-1]
        userCurvilinearPositionAt = user.getCurvilinearPositionAtInstant(t)[0]
        return userCurvilinearPositionAt - s

    def occupiedAlignmentLength(self, user):
        """return the total length of the alignment occupied by an user = its last position"""
        if user.curvilinearPositions is not None:
            alignmentIdx = user.curvilinearPositions.getLaneAt(-1)
            return self.getAlignmentById(alignmentIdx).points.cumulativeDistances[-1]
        else:
            return user.initialAlignmentIdx

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
                    s += self.getAlignmentById(indices).points.cumulativeDistances[-1]
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

    def getGraph(self):
        """adds graph attribute to self"""
        import networkx as nx
        G = nx.Graph()
        for k in range(len(self.alignments) + 1):
            G.add_node(k)
        edgesProperties = []
        for al in self.alignments:
            edgesProperties.append(
                (al.graphCorrespondance[0], al.graphCorrespondance[1], al.points.cumulativeDistances[-1]))
        G.add_weighted_edges_from(edgesProperties)
        if self.controlDevices is not None:
            for cdIdx, cd in enumerate(self.controlDevices):
                controlDevice = "cd{}".format(cdIdx)
                G.add_node(controlDevice)
                origin = self.getAlignmentById(cd.alignmentIdx).graphCorrespondance[0]
                target = self.getAlignmentById(cd.alignmentIdx).graphCorrespondance[1]
                weight = self.getAlignmentById(cd.alignmentIdx).points.cumulativeDistances[-1]
                G.add_weighted_edges_from([(origin, controlDevice, weight), (controlDevice, target, 0)])

        self.graph = G

    def distanceAtInstant(self, user1, user2, instant):
        """"computes the distance between 2 users"""
        import networkx as nx
        if type(user1) == agents.NewellMovingObject and type(user2) == agents.NewellMovingObject:
            if user1.getFirstInstant() <= instant and user2.getFirstInstant() <= instant:
                if moving.Interval.intersection(user1.timeInterval, user2.timeInterval) is not None:
                    user1AlignmentIdx = user1.getCurvilinearPositionAtInstant(instant)[2]
                    user2AlignmentIdx = user2.getCurvilinearPositionAtInstant(instant)[2]

                    # if self.getAlignmentById(user2AlignmentIdx).connectedAlignmentIndices[0] is not None:
                    #     pass
                    # else:

                    if user1AlignmentIdx == user2AlignmentIdx:#) or (user2AlignmentIdx == self.getAlignmentById(user1AlignmentIdx).connectedAlignmentIndices[0]):
                        return abs(
                            self.getUserDistanceOnAlignmentAt(user1, instant) - self.getUserDistanceOnAlignmentAt(user2,
                                                                                                                  instant) - user1.geometry)

                    else:
                        user1UpstreamDistance = self.getUserDistanceOnAlignmentAt(user1, instant)
                        user1DownstreamDistance = \
                            self.getAlignmentById(
                                user1.getCurvilinearPositionAtInstant(instant)[2]).points.cumulativeDistances[
                                -1] - user1UpstreamDistance
                        user2UpstreamDistance = self.getUserDistanceOnAlignmentAt(user2, instant)
                        user2DownstreamDistance = \
                            self.getAlignmentById(
                                user2.getCurvilinearPositionAtInstant(instant)[2]).points.cumulativeDistances[
                                -1] - user2UpstreamDistance

                        G = self.graph

                        G.add_node('user1')
                        G.add_node('user2')

                        user1Origin = self.getAlignmentById(user1AlignmentIdx).graphCorrespondance[0]
                        user1Target = self.getAlignmentById(user1AlignmentIdx).graphCorrespondance[1]
                        user2Origin = self.getAlignmentById(user2AlignmentIdx).graphCorrespondance[0]
                        user2Target = self.getAlignmentById(user2AlignmentIdx).graphCorrespondance[1]

                        G.add_weighted_edges_from([(user1Origin, 'user1', user1UpstreamDistance)])
                        G.add_weighted_edges_from([('user1', user1Target, user1DownstreamDistance)])

                        G.add_weighted_edges_from([(user2Origin, 'user2', user2UpstreamDistance)])
                        G.add_weighted_edges_from([('user2', user2Target, user2DownstreamDistance)])

                        distance = nx.shortest_path_length(G, source='user1', target='user2',
                                                           weight='weight') - user1.geometry
                        G.remove_node('user1')
                        G.remove_node('user2')
                        return distance
                else:
                    print('user do not coexist, therefore can not compute distance')

        elif type(user1) == agents.NewellMovingObject and type(user2) != agents.NewellMovingObject:
            if user1.getFirstInstant() <= instant:
                user1AlignmentIdx = user1.getCurvilinearPositionAtInstant(instant)[2]
                user1UpstreamDistance = self.getUserDistanceOnAlignmentAt(user1, instant)
                user1DownstreamDistance = \
                    self.getAlignmentById(
                        user1.getCurvilinearPositionAtInstant(instant)[2]).points.cumulativeDistances[
                        -1] - user1UpstreamDistance

                G = self.graph
                G.add_node('user1')

                user1Origin = self.getAlignmentById(user1AlignmentIdx).graphCorrespondance[0]
                user1Target = self.getAlignmentById(user1AlignmentIdx).graphCorrespondance[1]
                G.add_weighted_edges_from([(user1Origin, 'user1', user1UpstreamDistance)])
                G.add_weighted_edges_from([('user1', user1Target, user1DownstreamDistance)])

                distance = nx.shortest_path_length(G, source='user1', target="cd{}".format(user2.idx),
                                                   weight='weight')
                G.remove_node('user1')

                return distance
            else:
                return print(
                    'Can not compute distance between control Device and user because they are not located on the same alignment')

        elif type(user2) == agents.NewellMovingObject and type(user1) == ControlDevice:
            user1, user2 = user2, user1
            self.distanceAtInstant(user1, user2, instant)

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
        if self.controlDevices is not None:
            for cd in self.controlDevices:
                if cd.category == 1:
                    cd.timeAtStop = self.timeAtStop
                    cd.userTimeAtStop = 0
                    cd.timeStep = self.timeStep
                    cd.user = None

        for al in self.alignments:
            al.connectedAlignments = []
            if al.connectedAlignmentIndices is not None:
                for connectedAlignments in al.connectedAlignmentIndices:
                    al.connectedAlignments.append(self.getAlignmentById(connectedAlignments))
            else:
                al.connectedAlignments = None
            if self.controlDevices is not None:
                for cd in self.controlDevices:
                    if al.idx == cd.alignmentIdx:
                        al.controlDevice = cd
                    else:
                        al.controlDevice = None
            else:
                al.controlDevice = None

        for ui in self.userInputs:
            ui.users = []

    def getVisitedAlignmentLength(self, user):
        # todo: docstrings + test
        user.visitedAlignmentsLength = 0
        if user.curvilinearPositions is not None:
            visitedAlignments = list(set(user.curvilinearPositions.lanes))
            for alIndices in visitedAlignments:
                user.visitedAlignmentsLength += self.getAlignmentById(alIndices).points.cumulativeDistances[-1]
        else:
            user.visitedAlignmentsLength = 0

    def getUserCurrentAlignment(self, user):
        """"returns the current alignment of user"""
        self.getVisitedAlignmentLength(user)
        if user.curvilinearPositions is None:
            user.currentAlignment = self.getAlignmentById(user.initialAlignmentIdx)
        else:
            user.currentAlignment = self.getAlignmentById(user.curvilinearPositions.lanes[-1])

    def getIntersectionCP(self, alIdx):
        """"returns the curvilinear positions of the crossing point on all its alignments
        alIdx : alignment to project on"""
        intersectionCP = self.getAlignmentById(alIdx).points.cumulativeDistances[-1]
        for al in self.alignments:
            if al.connectedAlignmentIndices is not None:
                if alIdx in al.connectedAlignmentIndices:
                    intersectionCP += self.getAlignmentById(al.idx).points.cumulativeDistances[-1]
        return intersectionCP

    def getIncomingTrafficAlignmentIdx(self, user, instant):
        """"returns the alignment id of the adjacent alignment where the traffic comes from"""
        _temp = self.getAlignmentById(user.getCurvilinearPositionAtInstant(instant)[2]).connectedAlignmentIndices
        if _temp is not None:
            for al in self.alignments:  # determiner l'alignement sur lequel le traffic adjacent arrive
                if al.idx != user.getCurvilinearPositionAtInstant(instant)[2]:
                    if al.connectedAlignmentIndices is not None:
                        return al.idx

    def checkTraffic(self, user, instant):
        """"returns the closest user to cross the intersection in the adjacent alignments"""
        if instant in list(user.timeInterval):
            if self.getIncomingTrafficAlignmentIdx(user, instant) is not None:
                lane = self.getIncomingTrafficAlignmentIdx(user, instant)
                intersectionCP = self.getIntersectionCP(lane)
                userIntersectionCP = self.getAlignmentById(user.getCurvilinearPositionAtInstant(instant)[2]).points.cumulativeDistances[-1]
                if user.leader is not None:
                    if user.leader.getCurvilinearPositionAtInstant(instant)[0] > userIntersectionCP:
                        worldUserList = []
                        for k in range(len(self.userInputs)):
                            worldUserList.append(self.getNotNoneVehiclesInWorld()[k])
                        for ui in self.userInputs:
                            if ui.alignmentIdx == self.getIncomingTrafficAlignmentIdx(user, instant):
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
                        if ui.alignmentIdx == self.getIncomingTrafficAlignmentIdx(user, instant):
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
            s += al.cumulativeDistances[-1]
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
            return al.points.cumulativeDistances[-1]

    def assignValue(self, args):
        self.userInputs[0].distributions['headway'].scale = args.headway - 1
        self.userInputs[0].distributions['speed'].loc = args.speed
        self.userInputs[0].distributions['dn'].loc = args.dn
        self.userInputs[0].distributions['tau'].loc = args.tau
        self.userInputs[0].distributions['length'].loc = args.l


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
                                        initialAlignmentIdx=self.alignmentIdx)
        if len(self.users) > 0:
            # obj.leader = self.generatedNum[-1]
            obj.leader = self.users[-1]
        self.users.append(obj)
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
        from scipy import stats
        from trafficintelligence import utils

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
