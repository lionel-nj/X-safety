from trafficintelligence import moving


class NewellMovingObject(moving.MovingObject):

    def __init__(self, num=None, timeInterval=None, positions=None, velocities=None, geometry=None,
                 userType=moving.userType2Num['unknown'], nObjects=None, initCurvilinear=False, desiredSpeed=None,
                 tau=None, d=None, criticalGap=None, initialCumulatedHeadway=None,
                 initialAlignmentIdx=None):
        super().__init__(num, timeInterval, positions, velocities, geometry, userType, nObjects, initCurvilinear)
        self.desiredSpeed = desiredSpeed
        self.tau = tau
        self.d = d
        self.leader = None
        # other attributes necessary for computation
        self.initialCumulatedHeadway = initialCumulatedHeadway
        self.initialAlignmentIdx = initialAlignmentIdx
        self.timeAtS0 = None  # time at which the vehicle's position is s=0 on the alignment,
        self.criticalGap = criticalGap
        self.inSimulation = True
        self.go = True
        self.comingUser = None

    def orderUsersByFirstInstant(self, other):
        if self.getFirstInstant() > other.getFirstInstant():
            return other, self
        else:
            return self, other

    def updateCurvilinearPositions(self, method, instant, timeStep, world, amberProbability, maxSpeed=None, acceleration=None):
        # if timeGap< criticalGap : rester sur place, sinon avancer : a mettre en place dans le code
        '''Update curvilinear position of user at new instant'''
        # TODO reflechir pour des control devices
        if method == 'newell':
            if self.curvilinearPositions is None:  # vehicle without positions
                if self.timeAtS0 is None:
                    if self.leader is None:
                        self.timeAtS0 = self.initialCumulatedHeadway
                    elif self.leader.curvilinearPositions is not None and self.leader.curvilinearPositions.getSCoordAt(
                            -1) > self.d and len(self.leader.curvilinearPositions) >= 2:
                        firstInstantAfterD = self.leader.getLastInstant()
                        while self.leader.existsAtInstant(firstInstantAfterD) and \
                                self.leader.getCurvilinearPositionAtInstant(firstInstantAfterD - 1)[
                                    0] > self.d:  # find first instant after d
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
                        nextAlignmentIdx = self.currentAlignment.getNextAlignment(self, s2).idx
                        if self.inSimulation:
                            if self.currentAlignment.controlDevice is not None:
                                cd = self.currentAlignment.controlDevice
                                if cd.category == 1:
                                    if s2 >= self.visitedAlignmentsLength:
                                        if cd.userTimeAtStop < cd.timeAtStop:
                                            s2 = self.currentAlignment.points.cumulativeDistances[-1]
                                            cd.user = self
                                            cd.userTimeAtStop += timeStep
                                            nextAlignmentIdx = self.curvilinearPositions.getLaneAt(-1)
                                        else:
                                            if world.isGapAcceptable(self, instant):
                                                s2 = freeFlowCoord
                                                cd.user = None
                                                cd.userTimeAtStop = 0
                                            else:
                                                s2 = self.currentAlignment.points.cumulativeDistances[-1]
                                                nextAlignmentIdx = self.curvilinearPositions.getLaneAt(-1)
                                elif cd.category == 2:
                                    if cd.state == 'red':
                                        if s2 >= self.visitedAlignmentsLength:
                                            s2 = self.currentAlignment.points.cumulativeDistances[-1]
                                            nextAlignmentIdx = self.curvilinearPositions.getLaneAt(-1)
                                    elif cd.state == 'amber':
                                        if s2 >= self.visitedAlignmentsLength:
                                            if amberProbability >= .5: # if p > .5 user stops else if goes forward
                                                s2 = self.currentAlignment.points.cumulativeDistances[-1]
                                                nextAlignmentIdx = self.curvilinearPositions.getLaneAt(-1)
                                # else:
                                #     pass

                            self.curvilinearPositions.addPositionSYL(s2, 0., nextAlignmentIdx)

                else:
                    if instant in list(self.leader.timeInterval):
                        constrainedCoord = self.leader.interpolateCurvilinearPositions(instant - self.tau / timeStep)[
                                           0] - self.d
                    else:
                        constrainedCoord = freeFlowCoord
                    s2 = min(freeFlowCoord, constrainedCoord)
                    nextAlignmentIdx = self.currentAlignment.getNextAlignment(self, s2).idx

                    if self.inSimulation:
                        if self.currentAlignment.controlDevice is not None:
                            cd = self.currentAlignment.controlDevice
                            if cd.category == 1:
                                if s2 >= self.visitedAlignmentsLength:
                                    cd.user = self
                                    if cd.userTimeAtStop < cd.timeAtStop:
                                        s2 = self.currentAlignment.points.cumulativeDistances[-1]
                                        cd.userTimeAtStop += timeStep
                                        nextAlignmentIdx = self.curvilinearPositions.getLaneAt(-1)
                                    else:
                                        if world.isGapAcceptable(self, instant):
                                            s2 = freeFlowCoord
                                            cd.userTimeAtStop = 0
                                            cd.user = None
                                        else:
                                            nextAlignmentIdx = self.curvilinearPositions.getLaneAt(-1)
                                            s2 = self.currentAlignment.points.cumulativeDistances[-1]
                            elif cd.category == 2:
                                if cd.state == 'red':
                                    if s2 >= self.visitedAlignmentsLength:
                                        s2 = self.currentAlignment.points.cumulativeDistances[-1]
                                        nextAlignmentIdx = self.curvilinearPositions.getLaneAt(-1)
                                elif cd.state == 'amber':
                                    if s2 >= self.visitedAlignmentsLength:
                                        if amberProbability >= .5: # si p > .5 on s'arrete sinon on continue
                                            s2 = self.currentAlignment.points.cumulativeDistances[-1]
                                            nextAlignmentIdx = self.curvilinearPositions.getLaneAt(-1)

                            # else:
                            #     pass
                        self.curvilinearPositions.addPositionSYL(s2, 0., nextAlignmentIdx)

                if self.inSimulation:
                    if self.curvilinearPositions.getLaneAt(-1) == nextAlignmentIdx:
                        laneChange = None
                    else:
                        laneChange = (self.curvilinearPositions.getLaneAt(-1), nextAlignmentIdx)
                    self.setLastInstant(instant)
                    self.curvilinearVelocities.addPositionSYL(s2 - s1, 0., laneChange)
