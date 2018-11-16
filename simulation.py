
class Simulation(object):
    '''Stores all simulation and world parameters'''
    def __init__(self, world, duration, timeStep, interactionDistance, minimumDistanceHeadway, averageVehicleLength, averageVehicleWidth, vehicleLengthSD, vehicleWidthSD, ):
        self.world = world
        self.duration = duration
        self.timeStep = timeStep
        self.interactionDistance = interactionDistance
        self.minimumDistanceHeadway = minimumDistanceHeadway
        self.averageVehicleLength = averageVehicleLength
        self.averageVehicleWidth = averageVehicleWidth
        self.vehicleLengthSD = vehicleLengthSD
        self.vehicleWidthSD =vehicleWidthSD

    def save(self, filename):
        toolkit.save_yaml(filename, self)

    @staticmethod
    def load(filename):
        toolkit.load_yaml(filename)
