import itertools
import math

from trafficintelligence import moving, utils

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

    def build(self, entryPoint, exitPoint, others=None):
        """builds an alignments from points,
         entryPoint and exitPoint : moving.Point
         others : list of intermediate moving.points"""

        if others is None:
            self.points = moving.Trajectory.fromPointList([entryPoint, exitPoint])
        else:
            self.points = moving.Trajectory.fromPointList([entryPoint] + others + [exitPoint])

    @staticmethod
    def load(filename):
        return toolkit.loadYaml(filename)

    def save(self, filename):
        toolkit.saveYaml(filename, self)

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

    # def insertCrossingPoint(self):
    #     """inserts a crossing point : moving.Point in the alignment sequence"""
    #     if self.crossingPoint == self.points[0]:
    #         self.distanceToCrossingPoint = 0
    #
    #     elif self.points[-1] == self.crossingPoint:
    #         self.distanceToCrossingPoint = self.points.getCumulativeDistance(len(self.points))
    #
    #     else:
    #         for k in range(len(self.points) - 1):
    #             if Alignment.isBetween(self.points[k], self.points[k + 1], self.crossingPoint):
    #                 Alignment.insertPointAt(self, self.crossingPoint, k + 1)
    #                 self.points.computeCumulativeDistances()
    #                 self.distanceToCrossingPoint = self.points.getCumulativeDistance(k + 1)
    #                 break

    def isConnectedTo(self, other):
        """boolean, detemines if two alignments are connected"""
        if other.idx in self.connectedAlignmentIndices or self.idx in other.connectedAlignmentIndices:
            return True
        else:
            return False

    def angleAtCrossingPoint(self, other):
        """determines the angle between two alignments at the crossing point
        it is assumed that the method connectAlignments has already been applied to the alignments
        which means that both of the alignments in input have a crossingPoint attribute
        inputs : alignments
        output : angle (degrees) at the crossing point of the alignments """

        firstPoint = self.getFirstPoint()
        secondPoint = other.getFirstPoint()

        p1 = self.crossingPoint - firstPoint
        p2 = self.crossingPoint - secondPoint

        p = p1 - p2
        angle = moving.Point.angle(p) * 180 / math.pi

        self.angleAtCrossingPoint = angle
        other.angleAtCrossingPoint = angle

    def getAngleAtCrossing(self):
        """ method returns the angle formed by the the crossing alignments"""
        if hasattr(self, 'angleAtCrossing'):
            return self.angleAtCrossingPoint

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
        if self.points[0].x == point.x and self.points[0].y == point.y:
            return True
        else:
            return False

    def isEndOf(self, point):
        "boolean : True if a moving.Point is the last point of an alignment"

        if self.points[-1].x == point.x and self.points[-1].y == point.y:
            return True
        else:
            return False

    def addUserToAlignment(self, user):
        """adds an user to self.vehicles or self.user """
        if self.vehicles:
            self.vehicles.append(user)
        else:
            self.vehicles = [user]

    def getUserByNum(self, num):
        """returns a specific user by its id=num"""
        for v in self.vehicles:
            if v.num == num:
                return v

    def isReachableFrom(self, other):
        """returns boolean, True if an alignment is reachable from another one"""
        if other.connectedAlignmentIndices is not None:
            return self.idx in other.connectedAlignmentIndices
        else:
            return False

    def getUsersNum(self):
        usersNum = []
        for user in self.alignments:
            usersNum.append(user.num)
        return usersNum


class ControlDevice:
    """class for control deveices :stop signs, traffic light etc ...
    adapted from traffic_light_simulator package in pip3"""
    def __init__(self, idx, initialState, category, alignmentIdx, redTime=None, greenTime=None):
        import copy
        self.idx = idx
        self.initialState = initialState
        self.category = category
        self.alignmentIdx = alignmentIdx
        if self.category == 1:
            self.greenTime = 0
            self.redTime = float('inf')
        else:
            self.greenTime = greenTime
            self.redTime = redTime
        self.remainingRed = copy.deepcopy(redTime)
        self.remainingGreen = copy.deepcopy(greenTime)
        self.states = [self.initialState]

    categories = {1:'stop',
                2: 'traffic light',
                3: 'yield'}

    def getCharCategory(self):
        """returns a chain of character describing the category of self"""
        return self.categories[self.category]

    def switch(self):
        """ swith state to next state in the sequence """
        if self.states[-1] == 'stop':
            self.states.append('forward')
        else:
            self.states.append('stop')

    def getStateAt(self, t):
        """ returns art for the current color """
        return self.states[t]

    def cycle(self):
        """ displays the current state for a TrafficLight object for the duration of state"""
        if self.states[-1] == 'forward':
            if self.remainingGreen > 1:
                self.remainingGreen -= 1
                self.states.append('forward')
            else:
                self.switch()
                self.remainingGreen = self.greenTime
        else:
            if self.remainingRed > 1:
                self.remainingRed -= 1
                self.states.append('stop')
            else:
                self.switch()
                self.remainingRed = self.redTime


class World:
    """Description of the world, including the road (alignments), control devices (signs, traffic lights) and crossing point """

    def __init__(self, alignments=None, controlDevices=None, intersections=None):
        self.alignments = alignments  # liste d alignements
        self.intersections = intersections  # lsite des intersections (objets)
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
        self.getAlignmentById(0).connectAlignments(self.getAlignmentById(1))
        self.controlDevices = controlDevices
        self.alignments = alignments
        self.userInputs = userInputs
        self.save("default.yml")

    def plot(self, options='', **kwargs):
        import matplotlib.pyplot as plt
        for a in self.alignments:
            a.points.plot(options, kwargs)
        plt.plot()

    def showAlignments(self):
        """plots alignments in a word representation file"""
        import matplotlib.pyplot as plt
        for alignments in self.alignments:
            moving.Trajectory.plot(alignments.points)
            moving.Trajectory.plot(alignments.points)
        plt.show()
        plt.close()

    def getAlignments(self):
        return self.alignments

    def isVehicleBeforeCrossingPointAt(self, alignmentIdx, vehicleIdx, t, vehiclesData):
        """ determines if a vehicle if located ahead of a crossing point in a world representation """
        d = vehiclesData[alignmentIdx][vehicleIdx].curvilinearPositions[t][0] - self.getAlignmentById(
            alignmentIdx).distanceToCrossingPoint
        if d < 0:
            return True
        else:
            return False

    def minDistanceChecked(self, leaderAlignmentIdx, followerAlignmentIdx, i, j, t, dmin):
        """ checks if the minimum distance headway between two vehicles is verified
        in a car following situation : i is the leader vehicle and j is the following vehicle"""

        tempLeader = self.getAlignmentById(leaderAlignmentIdx).vehicles[i]
        tempFollower = self.getAlignmentById(followerAlignmentIdx).vehicles[j]
        if tempLeader.timeInterval.first > tempFollower.timeInterval.first:
            leader = tempFollower
            follower = tempLeader
        else:
            leader = tempLeader
            follower = tempFollower
        if moving.Interval.intersection(leader.timeInterval,
                                        follower.timeInterval) is not None and leader.timeInterval.contains(t):
            if leaderAlignmentIdx == followerAlignmentIdx:
                d = UserInput.distanceGap(leader.getCurvilinearPositionAtInstant(t)[0],
                                          follower.getCurvilinearPositionAtInstant(t)[0],
                                          leader.geometry)
                if d >= dmin:
                    return True
                return False

            else:
                angle = self.getAlignmentById(leaderAlignmentIdx).angleAtCrossingPoint(
                    self.getAlignmentById(followerAlignmentIdx))
                d1 = leader.curvilinearPositions[t][0] - self.getAlignmentById(
                    leaderAlignmentIdx).distanceToCrossingPoint
                d2 = follower.curvilinearPositions[t][0] - self.getAlignmentById(
                    followerAlignmentIdx).distanceToCrossingPoint
                d = ((d1 ** 2) + (d2 ** 2) - (2 * d1 * d2 * math.cos(angle))) ** 0.5  # loi des cosinus
                if d >= dmin:
                    return True
                else:
                    return False
        else:
            return True

    def isAnEncounter(self, leaderAlignmentIdx, followerAlignmentIdx, i, j, t, dmin):
        """ checks if there is an encounter between two vehicules
        leaderAlignmentIdx and followerAlignmentIdx are integers
        i,j : integers
        t : time, integer
        dmin : float  """
        if self.minDistanceChecked(leaderAlignmentIdx, followerAlignmentIdx, i, j, t, dmin):
            return False
        else:
            return True

    def count(self, method, dmin, alignmentIdx=None):
        """ counts according to the selected method (cross or in line)
         the number of interactions taking place at a distance smaller than dmin.
        """

        # {(26,27):[1,1,1,0,0,0,1,1,1]
        #  (27,28):[1,1,1,0,0,0,1,1,1]}

        if method == "inLine":
            vehList = []
            for user in self.getAlignmentById(alignmentIdx).vehicles:
                if user.timeInterval is not None:
                    vehList.append(user)

            rows = len(vehList)
            result = {}

            for h in range(4, rows - 1):
                commonInterval = self.getAlignmentById(alignmentIdx).vehicles[h].commonTimeInterval(
                    self.getAlignmentById(alignmentIdx).vehicles[h + 1])
                result[(h, h + 1)] = []
                for t in commonInterval:
                    if self.isAnEncounter(alignmentIdx, alignmentIdx, h, h + 1, t, dmin):
                        result[(h, h + 1)].append(1)
                    else:
                        result[(h, h + 1)].append(0)

            return result

        elif method == "crossing":

            vehList = [[], []]

            for el in self.getAlignmentById(0).vehicles:
                if el.timeInterval is not None:
                    vehList[0].append(el)

            for el in self.getAlignmentById(1).vehicles:
                if el.timeInterval is not None:
                    vehList[1].append(el)

            rows = len(vehList[0])
            columns = len(vehList[1])
            interactionTime = []
            totalNumberOfCrossingEncounters = 0

            for h in range(rows):
                interactionTime.append([])
                for v in range(columns):
                    interactionTime[h].append([])
                    follower = self.getAlignmentById(1).vehicles[v].getLeader(self.getAlignmentById(1).vehicles[v])

                    for t in range(follower.timeInterval.first, follower.timeInterval.last + 1):
                        if self.isAnEncounter(0, 1, h, v, t, dmin):
                            interactionTime[h][v].append(1)
                        else:
                            interactionTime[h][v].append(0)

                    numberOfEncounters = toolkit.countElementInList(interactionTime[h][v], 1)  #
                    totalNumberOfCrossingEncounters += numberOfEncounters
            return totalNumberOfCrossingEncounters

        else:
            print('error in method name')

    def countAllEncounters(self, vehiclesData, dmin):
        """counts the encounters in a world
        vehiclesData : list of list of moving objects
        dmin : float"""

        totalNumberOfEncounters = []

        for alignment in self.alignments:
            totalNumberOfEncounters.append(self.count(method="inLine", vehiclesData=vehiclesData,
                                                      alignmentIdx=alignment.idx, dmin=dmin))

        totalNumberOfEncounters.append(self.count(method="crossing", vehiclesData=vehiclesData, dmin=dmin))

        return totalNumberOfEncounters, sum(totalNumberOfEncounters)

    def initUsers(self, i, timeStep, userNum):
        """Initializes new users on their respective alignments """
        for ui in self.userInputs:
            futureCumulatedHeadways = []
            for h in ui.cumulatedHeadways:
                if i <= h / timeStep < i + 1:
                    ui.initUser(userNum, h)
                    userNum += 1
                else:
                    futureCumulatedHeadways.append(h)
            ui.cumulatedHeadways = futureCumulatedHeadways
        return userNum

    def convertSYtoXY(self):
        """converts SY to XY for a set of vehicles in self"""
        for al in self.alignments:
            for user in al.vehicles:
                if user.timeInterval is not None:
                    user.positions = moving.Trajectory()
                    user.velocities = moving.Trajectory()
                    for cp in user.curvilinearPositions:
                        user.positions.addPosition(
                            moving.getXYfromSY(s=cp[0],
                                               y=cp[1],
                                               alignmentNum=cp[2],
                                               alignments=[al.points]))
                    for idx, cv in enumerate(user.curvilinearVelocities):
                        user.velocities.addPosition(
                            moving.getXYfromSY(s=cv[0],
                                               y=cv[1],
                                               alignmentNum=user.curvilinearPositions[idx][2],
                                               alignments=[self.getAlignmentById(0).points]))
                else:
                    pass

    def getNotNoneVehiclesInWorld(self):
        """returns all vehicles that have been launched on their initial alignment : user.initialAlignment"""
        users = [[] * len(self.alignments)]
        for al in self.alignments:
            for user in al.vehicles:
                if user.timeInterval is not None:
                    users[al.idx].append(user)
        return users

    def getSimulatedUsers(self):
        """returns all vehicles that could not be computed, kind of the reciprocate of the method
        getNotNoneVehicleInWorld"""
        # TODO a verifier pour plusieurs alignments comportant des vehicules
        self.simulatedUsers = []
        for idx, al in enumerate(self.alignments):
            self.simulatedUsers.append([])
            for user in al.vehicles:
                if user is not None and user.timeInterval is not None:
                    if user.getCurvilinearPositionAt(-1)[0] > self.getVisitedAlignmentsCumulatedDistance(
                            user):  # sum(self.getAlignmentById(al.idx].points.distances):
                        self.simulatedUsers[idx].append([user.num, None])
                        for instant, cp in enumerate(user.curvilinearPositions):
                            if cp[0] > sum(al.points.distances):
                                self.simulatedUsers[-1][-1][-1] = instant
                                break

    def connectAlignments(self):
        """method to link the alignments: for a given alignment, it associates all the other alignments
         that can be reached from it"""
        import copy
        for idx, al in enumerate(self.alignments):
            _alignments = copy.deepcopy(self.alignments)
            _alignments.pop(idx)
            al.reachableAlignments = []
            if not _alignments:
                print('your world only has 1 alignment')
                break
            for other in _alignments:
                if other.isStartOf(al.getLastPoint()):
                    if other.isReachableFrom(al):
                        al.reachableAlignments.append(other.idx)

    def getNextAlignment(self, user, instant, timeStep):
        """returns the next alignment an user will be assigned to, according to the instant"""
        if user.timeInterval is not None:
            if user.timeInterval.first <= instant + user.getFirstInstant():
                occupiedAlignmentAtBy = user.curvilinearPositions.getLaneAt(-1)
                reachableAlignments = self.getAlignmentById(occupiedAlignmentAtBy).reachableAlignments
                nextPositionIfNoAlignmentChange = user.computeNextCurvilinearPositions('newell',
                                                                                       instant,
                                                                                       # + user.getFirstInstant() + 1,
                                                                                       timeStep)
                # print(nextPositionIfNoAlignmentChange)
                if self.getVisitedAlignmentsCumulatedDistance(user) \
                        < nextPositionIfNoAlignmentChange:
                    if reachableAlignments:
                        nextAlignment = reachableAlignments[0]
                    else:
                        nextAlignment = None
                else:
                    nextAlignment = None

                return nextAlignment
        else:
            return None

    def getVisitedAlignmentsCumulatedDistance(self, user):
        """returns total length of the alignment the user had been assigned to """
        visitedAlignmentsIndices = list(set(user.curvilinearPositions.lanes))
        # tempUser = self.rebuildUserTrajectory(user)
        visitedAlignmentsCumulativeDistance = 0
        for alignmentIdx in visitedAlignmentsIndices:
            visitedAlignmentsCumulativeDistance += self.getAlignmentById(alignmentIdx).points.cumulativeDistances[-1]

        return visitedAlignmentsCumulativeDistance

    def moveUserToAlignment(self, user):
        """ replaces every chunk of user.curvilinearPosition in the right alignment.vehicles
        returns Boolean = True, if the user's trajectory has been chunked"""
        laneChange, laneChangeInstants, changesList = user.changedAlignment()
        if laneChange:
            for alignmentChange, inter in zip(changesList, laneChangeInstants):
                self.getAlignmentById(alignmentChange[-1]).addUserToAlignment(user.getObjectInTimeInterval(
                    moving.TimeInterval(inter.first + user.getFirstInstant(), inter.last + user.getFirstInstant())))
            return True

    def replaceUserOnTravelledAlignments(self, user):
        """removes parts of curvilinearPosition that doesn't belong to the correct alignment """
        laneChange = user.changedAlignment()
        if laneChange[0]:

            # recuperer les alignments qui sont empruntés : alignmentIndices
            alignmentIndices = []
            for el in laneChange[-1]:
                alignmentIndices.extend(el)
                alignmentIndices = list(set(alignmentIndices))
            alignmentIndices.pop(alignmentIndices.index(user.initialAlignmentIdx))

            # pour chaque alignement ou le vehicule passe, ajouter le vehicule

            for inter, alignmentIdx in zip(laneChange[1], alignmentIndices):
                subUser = user.subTrajectoryInInterval(
                    moving.TimeInterval(inter.first + user.getFirstInstant(), inter.last + user.getFirstInstant()))
                subUser.state = user.state
                self.getAlignmentById(alignmentIdx).vehicles.append(subUser)

            #supprimer depuis le premier moment ou le cvehicule d=change d'alignement
            instant = laneChange[1][0].first
            user.removeAttributesFromInstant(instant)

    def replaceUsers(self):
        for userInput in self.userInputs:
            for user in userInput.alignment.vehicles:
                self.replaceUserOnTravelledAlignments(user)

    def getTravelledDistanceOnAlignment(self, user, t):
        """returns the travelled distance of an user on its current alignment"""
        visitedAlignments = list(set(user.curvilinearPositions.lanes[:t]))
        visitedAlignments.remove(user.curvilinearPositions.lanes[t])
        s = 0
        for indices in visitedAlignments:
            s += self.getAlignmentById(indices).points.cumulativeDistances[-1]
        userCurvilinearPositionAt = user.curvilinearPositions[t]
        return userCurvilinearPositionAt - self.getVisitedAlignmentsCumulatedDistance(user)

    def occupiedAlignmentLength(self, user):
        """return the total length of the alignment occupied by an user = its last position"""
        if user.curvilinearPositions is not None:
            alignmentIdx = user.curvilinearPositions.getLaneAt(-1)
            return self.getAlignmentById(alignmentIdx).points.cumulativeDistances[-1]
        else:
            return user.initialAlignmentIdx

    def getAlignmentById(self, idx):
        """get an alignment given its id"""
        try:
            idList = [el.idx for el in self.alignments]
            if idx not in idList:
                print('wrong index number')
            else:
                for al in self.alignments:
                    if al.idx == idx:
                        return al
        except:
            print('alignment idx does not match any existing alignment')
            return None

    def getUserByNum(self, userNum):
        """returns an user given its num"""
        _user = []
        for al in self.alignments:
            _user.append((al.idx, self.getUserByAlignmentIdAndNum(al.idx, userNum).curvilinearPositions[-1][0]))
        user = max(_user, key=lambda x: x[1])
        return self.getUserByAlignmentIdAndNum(user[0], user[1])

    def getUserByAlignmentIdAndNum(self, alignmentIdx, num):
        """returns an user given its num and alignment"""
        for user in self.getAlignmentById(alignmentIdx).vehicles:
            if user.num == num:
                return user

    @staticmethod
    def hasBeenOnAlignment(user, alignmentIdx):
        """determines if a vehicles has circulated on an alignment"""
        return alignmentIdx in user.curvilinearPositions.lanes

    def getPreviouslyOccupiedAlignmentsLength(self, user):
        """returns the length of the alignments a vehicle has previously travelled on """
        s = 0
        if user.curvilinearPositions is not None:
            alignmentIndices = list(set(user.curvilinearPositions.lanes))
            for indices in alignmentIndices:
                s += self.getAlignmentById(indices).points.cumulativeDistances[-1]
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
        for k in range(len(self.alignments)+1):
            G.add_node(k)
        edgesProperties = []
        for al in self.alignments:
            edgesProperties.append((al.graphCorrespondance[0], al.graphCorrespondance[1], al.points.cumulativeDistances[-1]))
        G.add_weighted_edges_from(edgesProperties)

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
        if type(user1) == moving.MovingObject and type(user2) == moving.MovingObject:
            if user1.getFirstInstant() <= instant and user2.getFirstInstant() <= instant:
                if moving.Interval.intersection(user1.timeInterval, user2.timeInterval) is not None:
                    user1CP = user1.getCurvilinearPositionAtInstant(instant)[2]
                    user2CP = user2.getCurvilinearPositionAtInstant(instant)[2]

                    user1DistanceUpstream = user1.distanceOnAlignments[instant - user1.getFirstInstant()]
                    user1DistanceDownstream = \
                        self.getAlignmentById(user1.getCurvilinearPositionAtInstant(instant)[2]).points.cumulativeDistances[
                            -1] - user1DistanceUpstream
                    user2DistanceUpstream = user2.distanceOnAlignments[instant - user2.getFirstInstant()]
                    user2DistanceDownstream = \
                        self.getAlignmentById(user2.getCurvilinearPositionAtInstant(instant)[2]).points.cumulativeDistances[
                            -1] - user2DistanceUpstream

                    G = self.graph

                    G.add_node('user1')
                    G.add_node('user2')

                    user1Origin = self.getAlignmentById(user1CP).graphCorrespondance[0]
                    user1Target = self.getAlignmentById(user1CP).graphCorrespondance[1]
                    user2Origin = self.getAlignmentById(user2CP).graphCorrespondance[0]
                    user2Target = self.getAlignmentById(user2CP).graphCorrespondance[1]

                    G.add_weighted_edges_from([(user1Origin, 'user1', user1DistanceUpstream)])
                    G.add_weighted_edges_from([('user1', user1Target, user1DistanceDownstream)])

                    G.add_weighted_edges_from([(user2Origin, 'user2', user2DistanceUpstream)])
                    G.add_weighted_edges_from([('user2', user2Target, user2DistanceDownstream)])

                    distance = nx.shortest_path_length(G, source='user1', target='user2', weight='weight')
                    G.remove_node('user1')
                    G.remove_node('user2')
                    return distance
                else:
                    print('user do not coexist, therefore can not compute distance')
        elif type(user1) == moving.MovingObject and type(user2) == ControlDevice:
            if user1.getFirstInstant() <= instant:
                user1CP = user1.getCurvilinearPositionAtInstant(instant)[2]
                if user1CP == user2.alignmentIdx:
                    user1DistanceUpstream = user1.distanceOnAlignments[instant - user1.getFirstInstant()]
                    user1DistanceDownstream = \
                        self.getAlignmentById(user1.getCurvilinearPositionAtInstant(instant)[2]).points.cumulativeDistances[
                            -1] - user1DistanceUpstream

                    G = self.graph
                    G.add_node('user1')

                    user1Origin = self.getAlignmentById(user1CP).graphCorrespondance[0]
                    user1Target = self.getAlignmentById(user1CP).graphCorrespondance[1]
                    G.add_weighted_edges_from([(user1Origin, 'user1', user1DistanceUpstream)])
                    G.add_weighted_edges_from([('user1', user1Target, user1DistanceDownstream)])

                    distance = nx.shortest_path_length(G, source='user1', target="cd{}".format(user2.idx), weight='weight')
                    G.remove_node('user1')

                    return distance
                else:
                    return print('Can not compute distance between control Device and user because they are not located on the same alignment')

        elif type(user2) == moving.MovingObject and type(user1) == ControlDevice:
            user1, user2 = user2, user1
            self.distance(user1, user2, instant)

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

    def insertControlDevices(self):
        """inserts controlDevice on the graph of the network"""
        G = self.graph
        for cdIdx, cd in enumerate(self.controlDevices):
            controlDevice = "cd{}".format(cdIdx)
            G.add_node(controlDevice)
            origin = self.getAlignmentById(cd.alignmentIdx).graphCorrespondance[0]
            target = self.getAlignmentById(cd.alignmentIdx).graphCorrespondance[1]
            weight = self.getAlignmentById(cd.alignmentIdx).points.cumulativeDistances[-1]
            G.add_weighted_edges_from([(origin, controlDevice, weight), (controlDevice, target, 0)])

    def startUser(self, userNum):
        user = self.getUserByNum(userNum)
        user.state = 'forward'

    def stopUser(self, userNum):
        user = self.getUserByNum(userNum)
        user.state = 'stop'

    def getControlDeviceById(self, idx):
        """get an control device given its id"""
        try:
            idList = [el.idx for el in self.controlDevices]
            if idx not in idList:
                print('wrong index number')
            else:
                for cd in self.controlDevices:
                    if cd.idx == idx:
                        return cd
        except:
            print('controlDeviceIdx does not match any existing alignment')
            return None

    def checkControlDevicesAtInstant(self, user, t, radius):
        """checks the state of controlDevices within a radius
        if controlDevice.state[t] == forward, user.state = forward, else user.state = stop"""
        if user.timeInterval is not None:
            if t - user.getFirstInstant() >= 0:
                # print(t - user.getFirstInstant())
                # print(user.curvilinearPositions)
                al = self.getAlignmentById(user.curvilinearPositions.lanes[t - user.getFirstInstant() - 1])
                if al.controlDeviceIndices:
                    for controlDeviceIdx in al.controlDeviceIndices:
                        if self.distanceAtInstant(user, self.getControlDeviceById(controlDeviceIdx), t-1) is not None and self.distanceAtInstant(user, self.getControlDeviceById(controlDeviceIdx), t-1) < radius:
                            if self.getControlDeviceById(controlDeviceIdx).getStateAt(t) == 'stop':
                                user.state = 'stop'
                            else:
                                user.state = 'forward'
                        else:
                            user.state = 'forward'

    def comingThroughTraffic(self, user, t, threshold):
        # todo : tester
        # todo : mettre a jour updateCurvilinearPositions avec le comportement aux abords d'un controlDevice
        al = self.getAlignmentById(user.getCurvilinearPositionAtInstant(t)[2])
        if len(al.connectedAlignmentIndices) > 1:
            for connectedAlIdx in al.al.connectedAlignmentIndices:
                # effectuer les calculs uniquement sur les alignements où le traffic arrive
                if al.graphCorrespondance[1] == self.getAlignmentById(connectedAlIdx).graphCorrespondance[1]:
                    # determiner le vehicule le plus proche :
                    distances = []
                    for comingThroughUser in enumerate(self.getAlignmentById(connectedAlIdx).vehicles):
                        distances.append((self.distance(user, comingThroughUser, t), comingThroughUser.num))
                        closestVehicleToUser = self.getUserByNum(min(distances, key=lambda x: x[1])[1])
                        if min(distances, key=lambda x: x[1])[0] < threshold:
                            if closestVehicleToUser.state == 'forward':
                                user.state = 'stop'
                            else:
                                user.state = 'forward'
                        else:
                            user.state = 'forward'


class UserInput:
    def __init__(self, alignmentIdx, distributions):
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

    def generateHeadways(self, duration):
        """ generates a set a headways"""
        self.headways = utils.maxSumSample(self.headwayDistribution, duration)
        self.cumulatedHeadways = list(itertools.accumulate(self.headways))

    def getUserInputDistribution(self, item):
        """returns the distribution parameters for an item : type, name, parameters"""
        return self.distributions[item].getDistribution()

    def initUser(self, userNum, initialCumulatedHeadway):
        """generates a MovingObject on the VehicleInput alignment"""

        obj = moving.MovingObject(userNum, geometry=self.lengthDistribution.rvs(), initCurvilinear=True)
        obj.addNewellAttributes(self.speedDistribution.rvs(),
                                self.tauDistribution.rvs(),
                                self.dDistribution.rvs(),
                                # kj=120 veh/km
                                initialCumulatedHeadway,
                                self.alignmentIdx,
                                'forward')
        # utile?
        # obj.criticalGap = gapNorm.getDistribution().rvs(random_state=10*userNum + 2*self.alignmentIdx)

        if len(self.alignment.vehicles) > 0:
            obj.leader = self.alignment.vehicles[-1]
        self.alignment.vehicles.append(obj)

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
