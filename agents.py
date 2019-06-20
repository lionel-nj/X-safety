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

    def updateCurvilinearPositions(self, instant, timeStep, world, maxSpeed=None, acceleration=None):#, amberProbability = 0):
        # if timeGap< criticalGap : rester sur place, sinon avancer : a mettre en place dans le code
        '''Update curvilinear position of user at new instant'''
        # TODO reflechir pour des control devices
        if self.curvilinearPositions is None:  # vehicle without positions
            if self.timeAtS0 is None:
                if self.leader is None:
                    self.timeAtS0 = self.initialCumulatedHeadway
                elif self.leader.curvilinearPositions is not None and self.leader.curvilinearPositions.getSCoordAt(
                        -1) > self.d and len(self.leader.curvilinearPositions) >= 2:
                    firstInstantAfterD = self.leader.getLastInstant()
                    while self.leader.existsAtInstant(firstInstantAfterD) and self.leader.getCurvilinearPositionAtInstant(firstInstantAfterD - 1)[0] > self.d:  # find first instant after d
                        firstInstantAfterD -= 1  # if not recorded position before self.d, we extrapolate linearly from first known position
                    leaderSpeed = self.leader.getCurvilinearVelocityAtInstant(firstInstantAfterD - 1)[0]
                    self.timeAtS0 = self.tau + firstInstantAfterD * timeStep - (
                                self.leader.getCurvilinearPositionAtInstant(firstInstantAfterD)[
                                    0] - self.d) * timeStep / leaderSpeed  # second part is the time at which leader is at self.d
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
                    constrainedCoord = self.leader.interpolateCurvilinearPositions(leaderInstant)[0] - self.d
                    self.curvilinearPositions = moving.CurvilinearTrajectory([min(freeFlowCoord, constrainedCoord)], [0.],
                                                                      [self.initialAlignmentIdx])
                    self.curvilinearVelocities = moving.CurvilinearTrajectory()

        else:
            s1 = self.curvilinearPositions.getSCoordAt(-1)
            freeFlowCoord = s1 + self.desiredSpeed * timeStep

            if self.leader is None:
                if self.getLastInstant() < instant:
                    s2 = freeFlowCoord
                    nextAlignment, s2 = self.currentAlignment.getNextAlignment(self, s2)
                    if nextAlignment is not None:
                        nextAlignmentIdx = nextAlignment.idx
                        # if s2 > self.currentAlignment.getCumulativeDistances(-1):
                        #     s2 -= self.currentAlignment.getCumulativeDistances(-1)
                        #     s1 -= self.currentAlignment.getCumulativeDistances(-1)
                        # if self.currentAlignment.controlDevice is not None:
                        #     cd = self.currentAlignment.controlDevice
                        #     if cd.category == 1:
                        #         if s2 >= self.visitedAlignmentsLength:
                        #             if cd.userTimeAtStop < cd.timeAtStop:
                        #                 s2 = self.currentAlignment.points.cumulativeDistances[-1]
                        #                 cd.user = self
                        #                 cd.userTimeAtStop += timeStep
                        #                 nextAlignmentIdx = self.curvilinearPositions.getLaneAt(-1)
                        #             else:
                        #                 if world.isGapAcceptable(self, instant):
                        #                     s2 = freeFlowCoord
                        #                     cd.user = None
                        #                     cd.userTimeAtStop = 0
                        #                 else:
                        #                     s2 = self.currentAlignment.points.cumulativeDistances[-1]
                        #                     nextAlignmentIdx = self.curvilinearPositions.getLaneAt(-1)
                        #     elif cd.category == 2:
                        #         if cd.state == 'red':
                        #             if s2 >= self.visitedAlignmentsLength:
                        #                 s2 = self.currentAlignment.points.cumulativeDistances[-1]
                        #                 nextAlignmentIdx = self.curvilinearPositions.getLaneAt(-1)
                        #         elif cd.state == 'amber':
                        #             if s2 >= self.visitedAlignmentsLength:
                        #                 if self.amberProbability >= .5:  # if p > .5 user stops else if goes forward
                        #                     s2 = self.currentAlignment.points.cumulativeDistances[-1]
                        #                     nextAlignmentIdx = self.curvilinearPositions.getLaneAt(-1)
                        self.curvilinearPositions.addPositionSYL(s2, 0., nextAlignmentIdx)

            else:
                if instant in list(self.leader.timeInterval):
                    constrainedCoord = self.leader.interpolateCurvilinearPositions(instant - self.tau / timeStep, self.currentAlignment)[
                                       0] - self.d + self.currentAlignment.getCumulativeDistances(-1)
                    # if self.leader.curvilinearPositions.lanes[-1] != self.curvilinearPositions.lanes[-1]:
                    #     constrainedCoord += self.currentAlignment.getCumulativeDistances(-1)
                else:
                    constrainedCoord = freeFlowCoord
                    # if self.leader.curvilinearPositions.lanes[-1] != self.curvilinearPositions.lanes[-1]:
                    #     constrainedCoord += self.currentAlignment.getCumulativeDistances(-1)

                if freeFlowCoord > self.currentAlignment.getCumulativeDistances(-1):
                    freeFlowCoord -= self.currentAlignment.getCumulativeDistances(-1)
                # if self.num ==1:
                #     print(constrainedCoord)
                s2 = min(freeFlowCoord, constrainedCoord)
                nextAlignment, _ = self.currentAlignment.getNextAlignment(self, s2)
                if nextAlignment is not None:
                    # if self.leader.currentAlignment.idx != self.currentAlignment.idx:
                    #     s2 += nextAlignment.getCumulativeDistances(-1)
                    nextAlignmentIdx = nextAlignment.idx
                    # if s2 > self.currentAlignment.getCumulativeDistances(-1):
                    #     s2 += self.currentAlignment.getCumulativeDistances(-1)
                        # s1 -= self.currentAlignment.getCumulativeDistances(-1)
                        # if self.currentAlignment.controlDevice is not None:
                        # cd = self.currentAlignment.controlDevice
                        # if cd.category == 1:
                        #     if s2 >= self.visitedAlignmentsLength:
                        #         cd.user = self
                        #         if cd.userTimeAtStop < cd.timeAtStop:
                        #             s2 = self.currentAlignment.points.cumulativeDistances[-1]
                        #             cd.userTimeAtStop += timeStep
                        #             nextAlignmentIdx = self.curvilinearPositions.getLaneAt(-1)
                        #         else:
                        #             if world.isGapAcceptable(self, instant):
                        #                 s2 = freeFlowCoord
                        #                 cd.userTimeAtStop = 0
                        #                 cd.user = None
                        #             else:
                        #                 nextAlignmentIdx = self.curvilinearPositions.getLaneAt(-1)
                        #                 s2 = self.currentAlignment.points.cumulativeDistances[-1]
                        # elif cd.category == 2:
                        #     if cd.state == 'red':
                        #         if s2 >= self.visitedAlignmentsLength:
                        #             s2 = self.currentAlignment.points.cumulativeDistances[-1]
                        #             nextAlignmentIdx = self.curvilinearPositions.getLaneAt(-1)
                        #     elif cd.state == 'amber':
                        #         if s2 >= self.visitedAlignmentsLength:
                        #             if self.amberProbability >= .5:  # if p > .5 user stops else if goes forward
                        #                 s2 = self.currentAlignment.points.cumulativeDistances[-1]
                        #                 nextAlignmentIdx = self.curvilinearPositions.getLaneAt(-1)

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

