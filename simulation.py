import numpy as np

import analysis as an
import toolkit


class Simulation(object):
    """Stores all simulation and world parameters"""
    units = [
        'sec',
        'sec',
        'sec',
        'N/A'
    ]

    def __init__(self, duration, minNCompletedUsers, timeStep, seed, verbose, dbName=None, computeInteractions=False):
        self.duration = duration
        self.minNCompletedUsers = minNCompletedUsers
        self.timeStep = timeStep
        self.seed = seed
        self.verbose = verbose
        self.dbName = dbName
        self.computeInteractions = computeInteractions

    def save(self, filename):
        toolkit.saveYaml(filename, self)

    @staticmethod
    def load(filename):
        return toolkit.loadYaml(filename)

    def run(self, world, surface=None):
        np.random.seed(self.seed)

        # preparing simulation
        world.prepare(self.timeStep, self.duration)
        if surface is not None:
            analysisZone = an.AnalysisZone(world.intersections[0], surface)
        else:
            analysisZone = None
        
        # main loop
        userNum = 0
        instant = 0

        while instant*self.timeStep < self.duration or len(world.completed) < self.minNCompletedUsers:
            if self.verbose:
                print('simulation step {}: {} users ({} completed), {} interactions ({} completed)'.format(instant, len(world.users), len(world.completed), len(world.interactions), len(world.completedInteractions)))
            world.updateControlDevices(self.timeStep)
            # print(world.controlDevices[0].state, world.controlDevices[1].state, instant)
            userNum = world.initUsers(instant, userNum, self.safetyDistance)
            world.updateUsers(instant, analysisZone)
            world.updateFirstUsers()
            world.updateInteractions(instant, self.computeInteractions)
            instant += 1
        world.duplicateLastVelocities()
        world.computePET(self)

if __name__ == "__main__":
    import doctest

    doctest.testmod()
