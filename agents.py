import numpy as np
from trafficintelligence import moving


class NewellMovingObject(moving.MovingObject):
    def __init__(self, num=None, timeInterval=None, positions=None, velocities=None, geometry=None,
                 userType=moving.userType2Num['unknown'], nObjects=None, initCurvilinear=False, desiredSpeed=None,
                 tau=None, d=None, criticalGap=None, initialCumulatedHeadway=None,
                 initialAlignment=None, amberProbability=None):
        super().__init__(num, timeInterval, positions, velocities, geometry, userType, nObjects, initCurvilinear)
        self.desiredSpeed = desiredSpeed
        self.tau = tau
        self.d = d
        self.leader = None
        # other attributes necessary for computation
        self.initialCumulatedHeadway = initialCumulatedHeadway
        self.alignments = [initialAlignment]
        self.instantAtS0 = None  # time at which the vehicle's position is s=0 on the alignment
        self.arrivalInstantAtControlDevice = None
        self.criticalGap = criticalGap
        self.comingUser = None
        self.amberProbability = amberProbability
        self.freeFlow = [] # bool list, 0 if agent is in a congested state, else (free flow) 1

    def getLeader(self):
        '''returns leader of agent'''
        return self.leader

    def updateD(self, safetyDistance):
        '''updates d parameter'''
        self.d = max(self.d, self.getLeader().geometry) + safetyDistance

    def getTimePercentageFreeFlow(self):
        return 100 * len([k for k in self.freeFlow if k == 1])/len(self.freeFlow)

    def getTimePercentageCongestion(self):
        return 100 * len([k for k in self.freeFlow if k == 0])/len(self.freeFlow)

    def getInstantAtCurvilinearPosition(self, cp, first=True):
        """"returns instant at curvilinear position, if first is true, returns the first instant
        else returns the last instant at curvilinear position"""
        if len(set(self.curvilinearPositions.lanes)) > 1:
            if first:
                lane = cp[2]
                return self.curvilinearPositions.positions[0].index([x for x in self.curvilinearPositions if x[0] <= cp[0] and x[2] == lane][-1][0]) + self.getFirstInstant()
            else:
                lane = cp[2]
                return max(loc for loc, val in enumerate(self.curvilinearPositions.lanes) if val == lane) + self.getFirstInstant() + 1
                # return min(loc for loc, val in enumerate(self.curvilinearPositions) if (cp[0] - 1.5 <= val[0] <= cp[0]) and val[2] == lane) + self.getFirstInstant() + 1
        else:
            return None

    def orderUsersByDistanceToPointAtInstant(self, world, other, instant):
        '''orders users by distance  to crossing point at instant'''
        d1 = world.distanceToCrossingAtInstant(self, other, instant)
        d2 = world.distanceToCrossingAtInstant(other, self, instant)
        if d1 > d2:
            return self, other
        else:
            return other, self

    def orderUsersByPositionAtInstant(self, other, instant):
        """order users by ascending distance at instant"""
        d1 = self.getDistanceFromOriginAtInstant(instant)[0]
        d2 = other.getDistanceFromOriginAtInstant(instant)[0]
        if d1 > d2:
            return self, other
        else:
            return other, self

    def getCriticalGap(self):
        return self.criticalGap

    def getInitialAlignment(self):
        '''Returns the user initial alignment '''
        return self.alignments[0]

    def getCurrentAlignment(self):
        '''Returns the user current alignment '''
        return self.alignments[-1]

    def addVisitedAlignment(self, al):
        """adds alignment to list of visited alignment by user"""
        if al != self.getCurrentAlignment():  # allow to visit alignment again
            self.alignments.append(al)

    def setArrivalInstantAtControlDevice(self, instant):
        """sets arrival instant at control device"""
        # it could be interesting to store the cd at which the user stops
        if self.arrivalInstantAtControlDevice is None:
            self.arrivalInstantAtControlDevice = instant

    def resetArrivalInstantAtControlDevice(self):
        self.arrivalInstantAtControlDevice = None

    def getWaitingTimeAtControlDevice(self, instant):
        return instant - self.arrivalInstantAtControlDevice

    def getDistanceFromOriginAt(self, t):
        """return distance from starting point of agent"""
        path = []
        distance = 0
        k = 0
        s = self.getCurvilinearPositionAt(t)
        while self.alignments[k].idx != s[2]:
            path.append(self.alignments[k])
            k += 1
        for al in path:
            distance += al.getTotalDistance()

        distance += s[0]

        return [distance, s[1], s[2]]

    def getDistanceFromOriginAtInstant(self, instant):
        return self.getDistanceFromOriginAt(instant - self.getFirstInstant())

    def getIntersectionEntryInstant(self):
        return self.intersectionEntryInstant

    def getIntersectionExitInstant(self):
        return self.intersectionExitInstant

    def getTotalDistance(self):
        distance = 0
        for al in self.alignments:
            distance += al.getTotalDistance()
        return distance

    def interpolateCurvilinearPositions(self, t):
        '''Linear interpolation of curvilinear positions, t being a float

        relies on list of visited alignments'''
        i = int(np.floor(t))
        p1 = self.getCurvilinearPositionAtInstant(i)
        p2 = self.getCurvilinearPositionAtInstant(i + 1)
        alpha = t - float(i)
        if p1[2] == p2[2]:
            return [(1 - alpha) * p1[0] + alpha * p2[0], (1 - alpha) * p1[1] + alpha * p2[1], p1[2]]
        else:
            # compute coord of p2 wrt alignment of p1
            i = 0
            while self.alignments[i].idx != p1[2]:
                i += 1
            i1 = i
            s2 = self.alignments[i1].getTotalDistance()
            i += 1
            while self.alignments[i].idx != p2[2]:
                s2 += self.alignments[i].getTotalDistance()
                i += 1
            s2 += p2[0]
            interS = (1 - alpha) * p1[0] + alpha * s2
            # find alignment of interpolated position
            i = i1
            while interS > self.alignments[i].getTotalDistance():
                interS -= self.alignments[i].getTotalDistance()
                i += 1
            return [interS, (1 - alpha) * p1[1] + alpha * p2[1], self.alignments[i].idx]
        # if hasattr(self, 'curvilinearPositions') and if self.existsAtInstant(t):
        #     i = int(floor(t))
        #     p1 = self.getCurvilinearPositionAtInstant(i)
        #     p2 = self.getCurvilinearPositionAtInstant(i+1)
        #     if p1[2] != p2[2] and alignments is not None:
        #         al, s = alignments[p1[2]].getNextAlignment((1-alpha)*p1[0]+alpha*p2[0]) # it works if no possible bifurcation at end of alignment
        #         return [s, (1-alpha)*p1[1]+alpha*p2[1], al[-1].idx]
        # return super().interpolateCurvilinearPositions(t, alignments)

    def getTravelledDistance(self, alignmentIdx1, alignmentIdx2):
        '''Returns travelled distance from alignmentIdx1 to beginning of alignmentIdx2 '''
        if alignmentIdx1 == alignmentIdx2:
            return 0.
        else:
            i = 0
            while self.alignments[i].idx != alignmentIdx1:
                i += 1
            s = self.alignments[i].getTotalDistance()
            while self.alignments[i].idx == alignmentIdx2:
                s += self.alignments[i].getTotalDistance()
                i += 1
            return s

    def isFirstOnAlignment(self):
        '''return True if agent is the first one on alignment'''
        return self.getCurrentAlignment().getFirstUser().num == self.num

    def areOnTransversalAlignments(self, other):
        '''returns True if agents are on transversal alignment, else False'''
        return self.getCurrentAlignment().transversalAlignments is not None and other.getCurrentAlignment() in self.getCurrentAlignment().transversalAlignments

    def updateCurvilinearPositions(self, instant, world, maxSpeed=None, acceleration=None):
        '''Update curvilinear position of user at new instant'''
        # TODO reflechir pour des control devices
        if self.curvilinearPositions is None:  # vehicle without positions
            if self.instantAtS0 is None:
                if self.leader is None:
                    self.instantAtS0 = self.initialCumulatedHeadway
                elif self.leader.curvilinearPositions is not None and self.leader.curvilinearPositions.getSCoordAt(-1) > self.d and len(self.leader.curvilinearPositions) >= 2:
                    firstInstantAfterD = self.leader.getLastInstant()
                    while self.leader.existsAtInstant(firstInstantAfterD) and self.leader.getCurvilinearPositionAtInstant(firstInstantAfterD - 1)[0] > self.d:  # find first instant after d
                        firstInstantAfterD -= 1  # if not recorded position before self.d, we extrapolate linearly from first known position
                    leaderSpeed = self.leader.getCurvilinearVelocityAtInstant(firstInstantAfterD - 1)[0]
                    self.instantAtS0 = self.tau + firstInstantAfterD - (self.leader.getCurvilinearPositionAtInstant(firstInstantAfterD)[0] - self.d) / leaderSpeed  # second part is the time at which leader is at self.d
                    if self.instantAtS0 < self.initialCumulatedHeadway:  # obj appears at instant initialCumulatedHeadway at x=0 with desiredSpeed
                        self.instantAtS0 = self.initialCumulatedHeadway
            elif instant > self.instantAtS0:
                # firstInstant = int(ceil(self.instantAtS0))# this first instant is instant by definition
                leaderInstant = instant - self.tau
                if self.leader is None:
                    s = (instant - self.instantAtS0) * self.desiredSpeed
                    self.curvilinearPositions = moving.CurvilinearTrajectory([s], [0.], [self.getInitialAlignment().idx])
                    self.following = False
                elif self.leader.existsAtInstant(leaderInstant):
                    freeFlowCoord = (instant - self.instantAtS0) * self.desiredSpeed
                    # constrainedCoord at instant = xn-1(t = instant-self.tau)-self.d
                    constrainedCoord = self.leader.interpolateCurvilinearPositions(leaderInstant)[0] - self.d
                    self.curvilinearPositions = moving.CurvilinearTrajectory([min(freeFlowCoord, constrainedCoord)], [0.], [self.getInitialAlignment().idx])
                    self.following = freeFlowCoord <= constrainedCoord
                self.timeInterval = moving.TimeInterval(instant, instant)
                self.curvilinearVelocities = moving.CurvilinearTrajectory()
                world.setInserted(self)
                if self.following:
                    self.freeFlow.append(0)
                else:
                    self.freeFlow.append(1)
                #self.getInitialAlignment().assignUserAtInstant(self, instant)
        else:
            s1 = self.curvilinearPositions.getSCoordAt(-1)
            freeFlowCoord = s1 + self.desiredSpeed
            if self.leader is None:
                s2 = freeFlowCoord
                self.following = False
            else:
                if self.leader.existsAtInstant(instant):
                    # compute leader coordinate with respect to current alignment
                    p = self.leader.interpolateCurvilinearPositions(instant - self.tau)
                    constrainedCoord = p[0] + self.leader.getTravelledDistance(self.curvilinearPositions.getLaneAt(-1), p[2]) - self.d
                    # self.following = True
                else:  # simplest is to continue at constant speed
                    ds = self.curvilinearVelocities.getSCoordAt(-1)
                    constrainedCoord = s1 + ds
                    # self.following = False
                s2 = min(freeFlowCoord, constrainedCoord)
                self.following = freeFlowCoord <= constrainedCoord
            nextAlignments, s2onNextAlignment = self.getCurrentAlignment().getNextAlignment(s2, self, instant, world)
            # if nextAlignments is not None:
            #     if nextAlignments[-1].getExitIntersection() is not None:
            #         if len(self.curvilinearVelocities) >0:
            #             if self.intersectionEntryInstant is None:
            #                 if nextAlignments[-1].getTotalDistance() - (s2-s1) <= s2onNextAlignment <= nextAlignments[-1].getTotalDistance():
            #                     self.intersectionEntryInstant = instant + 1
            if nextAlignments is not None:
                self.curvilinearPositions.addPositionSYL(s2onNextAlignment, 0., nextAlignments[-1].idx)
                if self.following:
                    self.freeFlow.append(0)
                else:
                    self.freeFlow.append(1)
                ds = s2-s1
                for al in nextAlignments[1:]:
                    self.addVisitedAlignment(al)
                if self.curvilinearPositions.getLaneAt(-2) == self.curvilinearPositions.getLaneAt(-1):
                    laneChange = None
                else:
                    laneChange = (self.curvilinearPositions.getLaneAt(-2), self.curvilinearPositions.getLaneAt(-1))
                    if nextAlignments[-1].getEntryIntersection() is not None:
                        self.intersectionEntryInstant = instant - s2onNextAlignment/ds
                        self.intersectionExitInstant = self.intersectionEntryInstant + self.geometry/ds
                    #self.intersectionExitInstant = instant
                self.curvilinearVelocities.addPositionSYL(ds, 0., laneChange)
                self.setLastInstant(instant)
                #nextAlignments[-1].assignUserAtInstant(self, instant)

                # TODO test if the new alignment is different from leader, update leader, updateD du suiveur

            else:
                world.setNewlyCompleted(self)
