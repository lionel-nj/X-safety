import numpy as np

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

    def run(self, world):
        np.random.seed(self.seed)

        # preparing simulation
        world.prepare(self.timeStep, self.duration)
        
        # main loop
        userNum = 0
        instant = 0
        condition = True

        while condition:
        # for i in range(int(np.floor(self.duration / self.timeStep))):
            if self.verbose:
                print('simulation step {}: {} users ({} completed), {} interactions ({} completed)'.format(instant, len(world.users), len(world.completed), len(world.interactions), len(world.completedInteractions)))
            world.updateControlDevices()
            userNum = world.initUsers(instant, userNum, self.safetyDistance)
            world.updateUsers(instant)
            world.updateFirstUsers()
            world.updateInteractions(instant, self.computeInteractions)
            instant += 1
            condition = len(world.completed) <= self.minNCompletedUsers and instant*self.timeStep < self.duration
            if instant*self.timeStep >= self.duration and len(world.completed) < self.minNCompletedUsers:
                condition = True
            
            

        world.duplicateLastVelocities()
        #world.finalize(instant)
        world.computePET()

if __name__ == "__main__":
    import doctest

    doctest.testmod()
