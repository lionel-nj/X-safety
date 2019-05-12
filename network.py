import itertools

from trafficintelligence import utils, moving

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
                t[idx].append(time * .1)

            plt.plot(t[idx], x[idx])
        plt.show()

    def getNextAlignment(self, user, nextPosition):
        visitedAlignmentsLength = user.visitedAlignmentsLength
        if visitedAlignmentsLength - nextPosition < 0: # si on est sorti de l'alignement
            if self.connectedAlignments is not None:
                return self.connectedAlignments[0] # todo : modifier selon les proportions de mouvements avec une variable aleatoire uniforme
            else:
                user.inSimulation = False
                return False
        else: # si on reste sur l'alignement
            return None


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

    categories = {1: 'stop',
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
            print('controlDeviceIdx does not match any existing alignment')
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

    def getUserByAlignmentIdAndNum(self, alignmentIdx, num):
        """returns an user given its num and alignment"""
        for user in self.getAlignmentById(alignmentIdx).vehicles:
            if user.num == num:
                return user

    def initUsers(self, i, timeStep, userNum):
        """Initializes new users on their respective alignments """
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
        users = [[] * len(self.userInputs)]
        for ui in self.userInputs:
            for user in ui.alignment.users:
                if user.timeInterval is not None:
                    users[ui.idx].append(user)
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

    def moveUserToAlignment(self, user):
        """replaces every chunk of user.curvilinearPosition in the right alignment.vehicles
        returns Boolean = True, if the user's trajectory has been chunked"""
        laneChange, laneChangeInstants, changesList = user.changedAlignment()
        if laneChange:
            for alignmentChange, inter in zip(changesList, laneChangeInstants):
                self.getAlignmentById(alignmentChange[-1]).addUserToAlignment(user.getObjectInTimeInterval(
                    moving.TimeInterval(inter.first + user.getFirstInstant(), inter.last + user.getFirstInstant())))
            return True

    def assignUserToCorrespondingAlignment(self):
        """assigns an user to its corresponding alignment"""
        for user in self.users:
            if user.curvilinearPositions is not None:
                CP = user.curvilinearPositions[-1]
                al = self.getAlignmentById(CP[2])
                if user.num in al.getUsersNum():
                    pass
                else:
                    if user.leader is not None:
                        user.leader = self.getUserByNum(user.leader.num)
                    al.vehicles.append(user)
                    if len(user.curvilinearPositions) > 2:
                        previousAl = self.getAlignmentById(user.curvilinearPositions.lanes[-2])
                    else:
                        previousAl = self.getAlignmentById(user.initialAlignmentIdx)
                    previousAl.vehicles.remove(user)

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
        if type(user1) == moving.MovingObject and type(user2) == moving.MovingObject:
            if user1.getFirstInstant() <= instant and user2.getFirstInstant() <= instant:
                if moving.Interval.intersection(user1.timeInterval, user2.timeInterval) is not None:
                    user1AlignmentIdx = user1.getCurvilinearPositionAtInstant(instant)[2]
                    user2AlignmentIdx = user2.getCurvilinearPositionAtInstant(instant)[2]

                    if user1AlignmentIdx == user2AlignmentIdx:
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

                        distance = nx.shortest_path_length(G, source='user1', target='user2', weight='weight') - user1.geometry
                        G.remove_node('user1')
                        G.remove_node('user2')
                        return distance
                else:
                    print('user do not coexist, therefore can not compute distance')

        elif type(user1) == moving.MovingObject and type(user2) == ControlDevice:
            if user1.getFirstInstant() <= instant:
                user1AlignmentIdx = user1.getCurvilinearPositionAtInstant(instant)[2]
                if user1AlignmentIdx == user2.alignmentIdx:
                    user1UpstreamDistance = user1.distanceOnAlignments[instant - user1.getFirstInstant()]
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

    def checkControlDevicesAtInstant(self, user, t, radius):
        """checks the state of controlDevices within a radius
        if controlDevice.state[t] == forward, user.state = forward, else user.state = stop"""
        if user.timeInterval is not None:
            if t - user.getFirstInstant() >= 0:
                # print(t - user.getFirstInstant())
                # print(user.curvilinearPositions)
                al = self.getAlignmentById(user.curvilinearPositions.lanes[t - self.getFirstInstant() - 1])
                if al.controlDeviceIndices:
                    for controlDeviceIdx in al.controlDeviceIndices:
                        if self.distanceAtInstant(user, self.getControlDeviceById(controlDeviceIdx),
                                                  t - 1) is not None and self.distanceAtInstant(user,
                                                                                                self.getControlDeviceById(
                                                                                                    controlDeviceIdx),
                                                                                                t - 1) < radius:
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

    def travelledAlignments(self, user):
        alignments = list(set(user.curvilinearPositions.lanes))
        travelledAlignments = []
        for alIndices in alignments:
            travelledAlignments.append(self.getAlignmentById(alIndices).points)
        return travelledAlignments

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

    def duplicateLastVelocities(self):
        for user in self.users:
            if user.curvilinearVelocities is not None:
                user.curvilinearVelocities.duplicateLastPosition()

    def prepare(self):
        for al in self.alignments:
            al.connectedAlignments = []
            if al.connectedAlignmentIndices is not None:
                for connectedAlignments in al.connectedAlignmentIndices:
                    al.connectedAlignments.append(self.getAlignmentById(connectedAlignments))
            else:
                al.connectedAlignments = None

    def getVisitedAlignmentLength(self, user):
        # todo: docstrings + test
        user.visitedAlignmentsLength = 0
        if user.curvilinearPositions is not None:
            visitedAlignments = list(set(user.curvilinearPositions.lanes))
            # visitedAlignments.remove(user.curvilinearPositions.lanes[-1])
            for alIndices in visitedAlignments:
                user.visitedAlignmentsLength += self.getAlignmentById(alIndices).points.cumulativeDistances[-1]
        else:
            user.visitedAlignmentsLength = 0

    def getUserCurrentAlignment(self, user):
        self.getVisitedAlignmentLength(user)
        if user.curvilinearPositions is None:
            user.currentAlignment = self.getAlignmentById(user.initialAlignmentIdx)
        else:
            user.currentAlignment = self.getAlignmentById(user.curvilinearPositions.lanes[-1])


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
        obj.inSimulation = True
        obj.addNewellAttributes(self.speedDistribution.rvs(),
                                self.tauDistribution.rvs(),
                                self.dDistribution.rvs(),
                                # kj=120 veh/km
                                initialCumulatedHeadway,
                                self.alignmentIdx)

        # if hasattr(self, 'generatedNum'):
        #     self.generatedNum.append(obj.num)
        # else:
        #     self.generatedNum = [obj.num]
        if len(self.alignment.users) > 0:
            # obj.leader = self.generatedNum[-1]
            obj.leader = self.alignment.users[-1]
        self.alignment.users.append(obj)
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
