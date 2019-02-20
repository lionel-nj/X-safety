import toolkit
import cars
from trafficintelligence import moving


class Simulation(object):
    '''Stores all simulation and world parameters'''
    units = [
        'sec',
        'sec',
        'm',
        'sec',
        'm',
        'm',
        'm',
        'm'
    ]

    def __init__(self, duration, timeStep, interactionDistance, minimumTimeHeadway, averageVehicleLength,
                 averageVehicleWidth, vehicleLengthSD, vehicleWidthSD):
        self.duration = duration
        self.timeStep = timeStep
        self.interactionDistance = interactionDistance
        self.minimumTimeHeadway = minimumTimeHeadway
        self.averageVehicleLength = averageVehicleLength
        self.averageVehicleWidth = averageVehicleWidth
        self.vehicleLengthSD = vehicleLengthSD
        self.vehicleWidthSD = vehicleWidthSD

    def save(self, filename):
        toolkit.save_yaml(filename, self)

    @staticmethod
    def load(filename):
        toolkit.load_yaml(filename)

    def minDistanceChecked(self, vehiclesData, leader_alignment_idx_i, follower_alignment_idx_j, i, j, t):
        """ checks if the minimum distance headway between two vehicles is verified
        in a car following situation : i is the leader vehicle and j is the following vehicle"""
        import math

        leader = vehiclesData.alignments[leader_alignment_idx_i].vehicles[i]
        follower = vehiclesData.alignments[follower_alignment_idx_j].vehicles[j]

        if leader_alignment_idx_i == follower_alignment_idx_j:
            if leader.timeInterval.contains(t) and follower.timeInterval.contains(t):
                d = cars.VehicleInput.distanceGap(
                    vehiclesData.alignments[leader_alignment_idx_i].vehicles[i].curvilinearPositions[
                        int(t / self.timeStep)][0],
                    vehiclesData.alignments[follower_alignment_idx_j].vehicles[j].curvilinearPositions[
                        int((t - follower.timeInterval.first) / self.timeStep)][0],
                    vehiclesData.alignments[leader_alignment_idx_i].vehicles[i].vehicleLength)
                if d >= self.interactionDistance:
                    return True
                return False
            else:
                print('one of the vehicles does no exist at t')
                return False

        else:
            angle = self.alignments[0].angleAtCrossingPoint(self.alignments[1])
            d1 = vehiclesData[leader_alignment_idx_i][i].curvilinearPositions[t][0] - self.alignments[
                leader_alignment_idx_i].distance_to_crossing_point
            d2 = vehiclesData[follower_alignment_idx_j][j].curvilinearPositions[t][0] - self.alignments[
                follower_alignment_idx_j].distance_to_crossing_point
            d = ((d1 ** 2) + (d2 ** 2) - (2 * d1 * d2 * math.cos(angle))) ** 0.5  # loi des cosinus
            if d >= self.interactionDistance:
                return True, d
            else:
                return False, d

    def isAnEncounter(self, vehiclesData, alignment_idx_i, alignment_idx_j, i, j, t):
        """ checks if there is an encounter between two vehicules
        alignment_idx_i and alignment_idx_j are integers
        i,j : integers
        t : time, integer
        dmin : float  """
        # d = self.minDistanceChecked(vehiclesData, alignment_idx_i, alignment_idx_j, i, j, t)[1]
        leader = vehiclesData.alignments[alignment_idx_i].vehicles[i]
        follower = vehiclesData.alignments[alignment_idx_j].vehicles[j]
        if (leader.timeInterval.contains(t)
                and follower.timeInterval.contains(t)
                and not self.minDistanceChecked(vehiclesData, alignment_idx_i, alignment_idx_j, i, j, t)):
            return True
        else:
            return False  # , d

    def count(self, method, vehiclesData, alignmentIdx=None):
        """ counts according to the selected method (cross or in line)
         the number of interactions taking place at a distance smaller than dmin.
        """
        if method == "inLine":
            rows = len(vehiclesData.alignments[alignmentIdx].vehicles)

            interactionTime = []
            totalNumberOfEncountersSameWay = 0

            for h in range(0, rows - 1):
                inter = moving.TimeInterval.intersection(vehiclesData.alignments[alignmentIdx].vehicles[h].timeInterval,
                                                         vehiclesData.alignments[alignmentIdx].vehicles[h + 1].timeInterval)
                t = round(inter.first, 1)
                interactionTime.append([])

                while t < inter.last - self.timeStep:
                    if self.isAnEncounter(vehiclesData, alignmentIdx, alignmentIdx, h, h + 1, t):
                        interactionTime[h].append(t)
                    t += self.timeStep

                if len(interactionTime[h]) < 2:
                    numberOfEncountersSameWay = len(interactionTime[h])

                else:
                    numberOfEncountersSameWay = 1
                    for k in range(len(interactionTime[h]) - 1):
                        if interactionTime[h][k + 1] != interactionTime[h][k] + 1:
                            numberOfEncountersSameWay += 1

                totalNumberOfEncountersSameWay += numberOfEncountersSameWay

            return totalNumberOfEncountersSameWay

        elif method == "crossing":
            rows = len(vehiclesData[0])
            columns = len(vehiclesData[1])
            interactionTime = []
            totalNumberOfCrossingEncounters = 0

            for h in range(rows):
                interactionTime.append([])
                for v in range(columns):
                    interactionTime[h].append([])

                    t = 0
                    while t < len(vehiclesData[0][0].curvilinearPositions):
                        if ((self.isAnEncounter(vehiclesData, 0, 1, h, v, t)[0]
                             and 0 < vehiclesData[0][h].velocities[t][0]
                             and 0 < vehiclesData[1][v].velocities[t][0])):
                            interactionTime[h][v].append(t)
                        t += self.timeStep

                    if len(interactionTime[h][v]) < 2:
                        numberOfEncounters = len(interactionTime[h][v])

                    else:
                        numberOfEncounters = 1
                        for k in range(len(interactionTime[h][v]) - 1):
                            if interactionTime[h][v][k + 1] != interactionTime[h][v][k] + 1:
                                numberOfEncounters += 1

                    totalNumberOfCrossingEncounters += numberOfEncounters

        else:
            return None

    def countAllEncounters(self, vehiclesData, dmin):
        """counts the encounters in a world
        vehiclesData : list of list of moving objects
        dmin : float"""

        totalNumberOfEncounters = []

        for alignment in self.alignments:
            totalNumberOfEncounters.append(self.count(method="inLine", vehiclesData=vehiclesData,
                                                      alignmentIdx=alignment.idx, dmin=dmin))

        totalNumberOfEncounters.append(self.count(method="crossing", vehiclesData=vehiclesData, dmin=dmin))

        return totalNumberOfEncounters, sum(totalNumberOfEncounters)


if __name__ == "__main__":
    import doctest

    doctest.testmod()
