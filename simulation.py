
class Simulation(object):
    '''Stores all simulation and world parameters'''
    def __init__(self, world, duration, timeStep, interactionDistance, minimumDistanceHeadway):
        self.world = world
        self.duration = duration
        self.timeStep = timeStep
        self.interactionDistance =interactionDistance
        self.minimumDistanceHeadway = minimumDistanceHeadway
