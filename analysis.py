import matplotlib.pyplot as plt
from trafficintelligence import events, prediction

import toolkit

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
    for idx in range(len(listOfVeh[al.idx]) - 1):
        TTCs[idx, idx + 1] = listOfVeh[al.idx][idx + 1].computeTTC(sim.timeStep)

    # getting ttc values
    ttcValues = [[] for _ in range(len(TTCs))]
    times = [[] for _ in range(len(TTCs))]

    for idx, ttc in enumerate(TTCs):
        for item in TTCs[ttc]:
            if item is not None:
                ttcValues[idx].append(item[0])
                times[idx].append(item[1])
        plt.plot(times[idx], ttcValues[idx])

    # getting minimum values of ttc
    listOfTTCMinValues = []
    for ttcList in ttcValues :
        if ttcList:
            listOfTTCMinValues.append(min(ttcList))

    #display
    plt.xlabel('time(s/10)')
    plt.ylabel('TTC (Time To Collision)')
    plt.show()
    plt.close()

    # histogram of min TTC values
    plt.hist(listOfTTCMinValues, bins='auto')

    # {(26,27):[1,1,1,0,0,0,1,1,1]
    #  (27,28):[1,1,1,0,0,0,1,1,1]}

    # collect for each pair of vehicle the list of times when the inter-vehicle distance is less than the threshold
    interactionTime = world.count('inLine', sim.interactionDistance, al.idx)

    # get the duration of each interaction between two vehicles
    interactionDuration = {}
    for el in interactionTime:
        if el:
            interactionDuration[el] = toolkit.makeSubListFromList(interactionTime[el])

    # count for each pair of vehicle the number of interactions and link it to their duration
    interactionsNumberDuration = {}
    for item in interactionDuration:
        interactionsNumberDuration[item] = (len(interactionDuration[item]), interactionDuration[item])


