from trafficintelligence import moving


class NewellMovingObject(moving.MovingObject):

    def __init__(self, num=None, timeInterval=None, positions=None, velocities=None, geometry=None,
                 userType=moving.userType2Num['unknown'], nObjects=None, initCurvilinear=False):
        super(moving.MovingObject, self).__init__(num, timeInterval)
        if initCurvilinear:
            self.curvilinearPositions = positions
            self.curvilinearVelocities = velocities  # third component is (previousAlignmentIdx, newAlignmentIdx) or None if no change
        else:
            self.positions = positions
            self.velocities = velocities
        self.geometry = geometry
        self.userType = userType
        self.setNObjects(nObjects)  # a feature has None for nObjects
        self.features = None

    def addNewellAttributes(self, desiredSpeed, tau, d, criticalGap, initialCumulatedHeadway, initialAlignmentIdx):
        '''adds attributes necessary for Newell car following model
        using curvilinear trajectories'''
        # Newell model parameters
        self.desiredSpeed = desiredSpeed
        self.tau = tau
        self.d = d
        self.leader = None
        # other attributes necessary for computation
        self.initialCumulatedHeadway = initialCumulatedHeadway
        self.initialAlignmentIdx = initialAlignmentIdx
        self.timeAtS0 = None  # time at which the vehicle's position is s=0 on the alignment,
        self.criticalGap = criticalGap

    def updateCurvilinearPositions(self, method, instant, timeStep, maxSpeed=None,
                                   acceleration=None):
        # if timeGap< criticalGap : rester sur place, sinon avancer : a mettre en place dans le code
        '''Update curvilinear position of user at new instant'''
        # TODO changer nextAlignmentIdx pour l'alignment en cours, reflechir pour des control devices
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

                if self.leader is not None:
                    if not self.leader.inSimulation:
                        self.leader = None

                if self.leader is None:
                    if self.getLastInstant() < instant:
                        s2 = freeFlowCoord
                        nextAlignment = self.currentAlignment.getNextAlignment(self, s2)
                        if nextAlignment is None:
                            nextAlignmentIdx = self.curvilinearPositions.getLaneAt(-1)
                        else:
                            if nextAlignment:
                                nextAlignmentIdx = nextAlignment.idx
                        if self.inSimulation:
                            self.curvilinearPositions.addPositionSYL(freeFlowCoord, 0., nextAlignmentIdx)


                else:
                    constrainedCoord = self.leader.interpolateCurvilinearPositions(instant - self.tau / timeStep)[
                                           0] - self.d
                    s2 = min(freeFlowCoord, constrainedCoord)
                    nextAlignment = self.currentAlignment.getNextAlignment(self, s2)
                    if nextAlignment is None:
                        nextAlignmentIdx = self.curvilinearPositions.getLaneAt(-1)
                    else:
                        nextAlignmentIdx = nextAlignment.idx
                    self.curvilinearPositions.addPositionSYL(s2, 0., nextAlignmentIdx)
                if self.inSimulation:
                    if nextAlignment is not None:
                        laneChange = (self.curvilinearPositions.getLaneAt(-1), nextAlignmentIdx)
                    else:
                        laneChange = None
                    self.setLastInstant(instant)
                    self.curvilinearVelocities.addPositionSYL(s2 - s1, 0., laneChange)
