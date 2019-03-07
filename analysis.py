import matplotlib.pyplot as plt
from trafficintelligence import events, moving, prediction

import makesimulation

world = makesimulation.world
sim = makesimulation.sim

# converting curvilinear trajectories/velocities to cartesian trajectories/velocities
world.convertSYtoXY()
listOfVeh = world.getNotNoneVehiclesInWorld()

for al in world.alignments:
    # defining interactions
    interactions = []
    for u in range(len(listOfVeh[al.idx]) - 1):
        interactions.append(events.Interaction(roadUser1=listOfVeh[al.idx][u], roadUser2=listOfVeh[al.idx][u + 1]))

    # computing interactions
    for inter in interactions:
        inter.computeIndicators()
        predictionParams = prediction.ConstantPredictionParameters(10.)
        inter.computeCrossingsCollisions(
            predictionParameters=predictionParams,
            collisionDistanceThreshold=25.,
            timeHorizon=300)

    TTCs = {}

    # computing ttc values
    for idx in range(len(listOfVeh[al.idx])-1):
        TTCs[idx, idx + 1] = moving.computeTTC(listOfVeh[al.idx][idx+1], sim.timeStep)

    # plotting ttc values
    ttcValues = [[]*len(TTCs)]
    times = [[]*len(TTCs)]

    for idx, ttc in enumerate(TTCs):
        for item in TTCs[ttc]:
            ttcValues[idx].append(item[0])
            times[idx].append(item[0])

    for idx, ttc in enumerate(TTCs):
        for k in range(len(TTCs[ttc])):
            ttcValues.append([item[0] for item in TTCs[ttc]])
            times.append([item[1] for item in TTCs[ttc]])
            plt.plot(ttcValues[idx], times[idx])

    plt.xlabel('time(s)')
    plt.ylabel('TTC (Time To Collision)')
    plt.show()
    plt.close()
    # getting minimum values of ttc
    listOfTTCMinValues = []
    for ttc in TTCs:
        if TTCs[ttc]:
            listOfTTCMinValues.append(min(TTCs[ttc]))
    #
    # # histogram of min TTC values
    # plt.hist(listOfTTCMinValues, bins='auto')
    #

