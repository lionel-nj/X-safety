import networkx as nx
import numpy as np
from trafficintelligence import moving


class NewellMovingObject(moving.MovingObject):
    def __init__(self, num=None, timeInterval=None, positions=None, velocities=None, geometry=None,
                 userType=moving.userType2Num['unknown'], nObjects=None, initCurvilinear=False, desiredSpeed=None,
                 tau=None, d=None, criticalGap=None, initialCumulatedHeadway=None,
                 initialAlignmentIdx=None, amberProbability=None):
        super(NewellMovingObject, self).__init__(num, timeInterval, positions, velocities, geometry, userType, nObjects, initCurvilinear)
        self.desiredSpeed = desiredSpeed
        self.tau = tau
        self.d = d
        self.leader = None
        # other attributes necessary for computation
        self.initialCumulatedHeadway = initialCumulatedHeadway
        self.initialAlignmentIdx = initialAlignmentIdx
        self.timeAtS0 = None  # time at which the vehicle's position is s=0 on the alignment,
        self.criticalGap = criticalGap
        self.comingUser = None
        self.amberProbability = amberProbability

    def orderUsersByFirstInstant(self, other):
        if self.getFirstInstant() > other.getFirstInstant():
            return other, self
        else:
            return self, other

    def getUserCurrentAlignment(self, world):
        """"assigns to an user its the current alignment"""
        if self.curvilinearPositions is None:
            self.currentAlignment = world.getAlignmentById(self.initialAlignmentIdx)
        else:
            self.currentAlignment = world.getAlignmentById(self.curvilinearPositions.lanes[-1])

    def getDistanceFromOriginAtInstant(self, instant, world):
        """returns the total distance for an user at instant"""
        G = world.graph
        G.add_node(self)
        s = self.getCurvilinearPositionAtInstant(instant)
        upstreamDistance = s[0]
        downstreamDistance = self.currentAlignment.getCumulativeDistances(-1) - upstreamDistance

        entryNode = world.getAlignmentById(s[2]).entryNode
        exitNode = world.getAlignmentById(s[2]).exitNode

        G.add_weighted_edges_from([(entryNode, self, upstreamDistance)])
        G.add_weighted_edges_from([(self, exitNode, downstreamDistance)])
        distance = nx.shortest_path_length(G, source=world.getAlignmentById(self.initialAlignmentIdx).entryNode, target=self, weight='weight')
        G.remove_node(self)
        return [distance, s[1], s[2]]

    def interpolateCurvilinearPositions(self, t, world):
        '''Linear interpolation of curvilinear positions, t being a float'''
        if hasattr(self, 'curvilinearPositions'):
            if self.existsAtInstant(t):
                i = int(np.floor(t))
                p1 = self.getDistanceFromOriginAtInstant(i, world)
                p2 = self.getDistanceFromOriginAtInstant(i + 1, world)
                alpha = t - float(i)
                if alpha < 0.5:
                    lane = p1[2]
                else:
                    lane = p2[2]
                return [(1 - alpha) * p1[0] + alpha * p2[0], (1 - alpha) * p1[1] + alpha * p2[1], lane]

            else:
                print('Object {} does not exist at {}'.format(self.getNum(), t))
        else:
            print('Object {} has no curvilinear positions'.format(self.getNum()))

    def updateCurvilinearPositions(self, instant, timeStep, world, maxSpeed=None, acceleration=None):#, amberProbability = 0):
        # if timeGap< criticalGap : rester sur place, sinon avancer : a mettre en place dans le code
        '''Update curvilinear position of user at new instant'''
        # TODO reflechir pour des control devices
        if self.curvilinearPositions is None:  # vehicle without positions
            if self.timeAtS0 is None:
                if self.leader is None:
                    self.timeAtS0 = self.initialCumulatedHeadway
                elif self.leader.curvilinearPositions is not None and self.leader.curvilinearPositions.getSCoordAt(-1) > self.d and len(self.leader.curvilinearPositions) >= 2:
                    firstInstantAfterD = self.leader.getLastInstant()
                    while self.leader.existsAtInstant(firstInstantAfterD) and self.leader.getCurvilinearPositionAtInstant(firstInstantAfterD - 1)[0] > self.d:  # find first instant after d
                        firstInstantAfterD -= 1  # if not recorded position before self.d, we extrapolate linearly from first known position
                    leaderSpeed = self.leader.getCurvilinearVelocityAtInstant(firstInstantAfterD - 1)[0]
                    self.timeAtS0 = self.tau + firstInstantAfterD * timeStep - (self.leader.getCurvilinearPositionAtInstant(firstInstantAfterD)[0] - self.d) * timeStep / leaderSpeed  # second part is the time at which leader is at self.d
                    if self.timeAtS0 < self.initialCumulatedHeadway:  # obj appears at instant initialCumulatedHeadway at x=0 with desiredSpeed
                        self.timeAtS0 = self.initialCumulatedHeadway
            elif instant * timeStep > self.timeAtS0:
                # firstInstant = int(ceil(self.timeAtS0/timeStep))# this first instant is instant by definition
                leaderInstant = instant - self.tau / timeStep
                if self.leader is None:
                    s = (timeStep * instant - self.timeAtS0) * self.desiredSpeed
                    self.timeInterval = moving.TimeInterval(instant, instant)
                    self.curvilinearPositions = moving.CurvilinearTrajectory([s], [0.], [self.initialAlignmentIdx])
                    self.curvilinearVelocities = moving.CurvilinearTrajectory()
                elif self.leader.existsAtInstant(leaderInstant):
                    self.timeInterval = moving.TimeInterval(instant, instant)
                    freeFlowCoord = (instant * timeStep - self.timeAtS0) * self.desiredSpeed
                    # constrainedCoord at instant = xn-1(t = instant*timeStep-self.tau)-self.d
                    constrainedCoord = self.leader.interpolateCurvilinearPositions(leaderInstant, world)[0] - self.d
                    self.curvilinearPositions = moving.CurvilinearTrajectory([min(freeFlowCoord, constrainedCoord)], [0.], [self.initialAlignmentIdx])
                    self.curvilinearVelocities = moving.CurvilinearTrajectory()

        else:
            s = self.getCurvilinearPositionAt(-1)
            s1 = s[0]
            freeFlowCoord = s1 + self.desiredSpeed * timeStep
            if self.leader is None:
                if self.getLastInstant() < instant:
                    s2 = freeFlowCoord
                    nextAlignment, s2 = self.currentAlignment.getNextAlignment(self, s2)
                    if nextAlignment is not None:
                        nextAlignmentIdx = nextAlignment.idx
                        self.curvilinearPositions.addPositionSYL(s2, 0., nextAlignmentIdx)

            else:
                if s[2] == self.leader.currentAlignment.idx:
                    freeFlowCoord = s1 + self.desiredSpeed * timeStep

                if instant in list(self.leader.timeInterval):
                    constrainedCoord = self.leader.interpolateCurvilinearPositions(instant - self.tau / timeStep, world)[0] - self.d
                else:
                    constrainedCoord = freeFlowCoord

                s2 = min(freeFlowCoord, constrainedCoord)

                nextAlignment, s2 = self.currentAlignment.getNextAlignment(self, s2)
                if nextAlignment is not None:
                    nextAlignmentIdx = nextAlignment.idx
                    self.curvilinearPositions.addPositionSYL(s2, 0., nextAlignmentIdx)

            if nextAlignment is not None:
                if self.curvilinearPositions.getLaneAt(-1) == nextAlignmentIdx:
                    laneChange = None
                else:
                    laneChange = (self.curvilinearPositions.getLaneAt(-1), nextAlignmentIdx)
                self.setLastInstant(instant)
                self.curvilinearVelocities.addPositionSYL(s2 - s1, 0., laneChange)
            # else:
            #     if self.leader is not None:
            #         self.setLastInstant(instant-2)

