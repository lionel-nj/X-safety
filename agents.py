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

    def updateCurvilinearPositions(self, method, instant, timeStep, maxSpeed=None,
                                   acceleration=None):
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
                        # self.currentAlignment.isGapAcceptable(self, instant)
                        if self.inSimulation:
                            if self.go:# and self.acceptGap:
                                self.curvilinearPositions.addPositionSYL(freeFlowCoord, 0., nextAlignmentIdx)
                            else:
                                s2 = self.currentAlignment.points.cumulativeDistances[-1]
                                self.curvilinearPositions.addPositionSYL(s2, 0., nextAlignmentIdx)

                else:
                    if instant in list(self.leader.timeInterval):
                        constrainedCoord = self.leader.interpolateCurvilinearPositions(instant - self.tau / timeStep)[
                                           0] - self.d
                    else:
                        constrainedCoord = freeFlowCoord
                    if self.go :#and self.acceptGap:
                        s2 = min(freeFlowCoord, constrainedCoord)
                    else:
                        s2 = self.currentAlignment.points.cumulativeDistances[-1]
                    nextAlignmentIdx = self.currentAlignment.getNextAlignment(self, s2).idx

                    if self.inSimulation:
                        if self.go :#and self.acceptGap:
                            s2 = min(freeFlowCoord, constrainedCoord)
                            self.curvilinearPositions.addPositionSYL(s2, 0., nextAlignmentIdx)
                        else:
                            s2 = self.currentAlignment.points.cumulativeDistances[-1]
                            self.curvilinearPositions.addPositionSYL(s2, 0., nextAlignmentIdx)

                if self.inSimulation:
                    # if nextAlignment is not None:
                    #     laneChange = (self.curvilinearPositions.getLaneAt(-1), nextAlignmentIdx)
                    # else:
                    if self.curvilinearPositions.getLaneAt(-1) == nextAlignmentIdx:
                        laneChange = None
                    else:
                        laneChange = (self.curvilinearPositions.getLaneAt(-1), nextAlignmentIdx)
                    self.setLastInstant(instant)
                    self.curvilinearVelocities.addPositionSYL(s2 - s1, 0., laneChange)
