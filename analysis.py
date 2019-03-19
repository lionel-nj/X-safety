import matplotlib.pyplot as plt
from trafficintelligence import events, prediction, moving
import numpy as np
import toolkit

world = toolkit.loadYaml('world.yml')
sim = toolkit.loadYaml('config.yml')


def run(worldFile, configFile):

    # converting curvilinear trajectories/velocities to cartesian trajectories/velocities
    # worldFile.convertSYtoXY()
    listOfVeh = worldFile.getNotNoneVehiclesInWorld()
    predictionParams = prediction.CVExactPredictionParameters(useCurvilinear=True)

    for al in worldFile.alignments:
        # defining interactions
        al.points.computeCumulativeDistances()
        interactions = []
        for userIdx in range(len(listOfVeh[al.idx]) - 1):
            interactions.append(events.Interaction(useCurvilinear=True, roadUser1=listOfVeh[al.idx][userIdx], roadUser2=listOfVeh[al.idx][userIdx + 1]))

        # computing interactions
        for inter in interactions:
            inter.computeIndicators(alignment1=al, alignment2=al)
            inter.computeCrossingsCollisions(
                predictionParameters=predictionParams,
                collisionDistanceThreshold=7,
                timeHorizon=300,
                useCurvilinear=True,
                alignment1=al,
                alignment2=al)

        # getting the ttc-time list for each interaction if ttc has been computed (2)
        TTCs = {}
        times = []
        for inter in interactions:
            if 'Time to Collision' in inter.indicators.keys():
                TTCs[(inter.roadUser1.num, inter.roadUser2.num)] = []
                times.append([])
                for key, value in enumerate(inter.indicators['Time to Collision']):
                    TTCs[(inter.roadUser1.num, inter.roadUser2.num)].append(value)
                    times[-1].append(key)
    return interactions

    #     # computing ttc values (1)
    #     for idx in range(len(listOfVeh[al.idx]) - 1):
    #         TTCs[idx, idx + 1] = listOfVeh[al.idx][idx + 1].computeTTC(configFile.timeStep)
    #
    #     # getting ttc values (1)
    #     ttcValues = [[] for _ in range(len(TTCs))]
    #     times = [[] for _ in range(len(TTCs))]
    #
    #     for idx, ttc in enumerate(TTCs):
    #         for item in TTCs[ttc]:
    #             if item is not None:
    #                 ttcValues[idx].append(item[0])
    #                 times[idx].append(item[1])
    #         plt.plot(times[idx], ttcValues[idx])
    #
    #     # plotting ttc value for each interactions (2)
    #     for timeValues, ttcValues in zip(times, TTCs):
    #         plt.plot(timeValues, TTCs[ttcValues])
    #
    #     # display
    #     plt.xlabel('time(s/10)')
    #     plt.ylabel('TTC (Time To Collision)')
    #     plt.show()
    #     plt.close()
    #
    #     # getting minimum values of ttc (1)
    #     minTTCsValues = []
    #     # for ttcList in ttcValues:
    #     #     if ttcList:
    #     #         minTTCsValues.append(min(ttcList))
    #
    #     # getting minimum values of ttc (2)
    #     for ttcList in TTCs:
    #             minTTCsValues.append(min(TTCs[ttcList]))
    #
    #     # histogram of min TTC values
    #     plt.hist(minTTCsValues, bins='auto')
    #
    #     # collect for each pair of vehicle the list of times when the inter-vehicle distance is less than the threshold
    #     # number of interactions for each pair of vehicles
    #     d = [15, 17, 20]
    #     for distance in d:
    #         interactionTime = worldFile.count('inLine', distance, al.idx)
    #
    #         # get the duration of each interaction between two vehicles
    #         interactionDuration = {}
    #         for el in interactionTime:
    #             if el:
    #                 interactionDuration[el] = toolkit.makeSubListFromList(interactionTime[el])
    #
    #         # count for each pair of vehicle the number of interactions and link it to their duration
    #         interactionsCharacteristics = {}
    #         for item in interactionDuration:
    #             interactionsCharacteristics[item] = (len(interactionDuration[item]), interactionDuration[item])
    #
    #         # total number of interactions
    #         totalInteractionsNumber = 0
    #         interactionLengthList = []
    #         for elt in interactionsCharacteristics:
    #             totalInteractionsNumber += interactionsCharacteristics[elt][0]
    #             for times in interactionsCharacteristics[elt][1]:
    #                 if interactionsCharacteristics[elt][1]:
    #                     interactionLengthList.append(times)
    # #
    # #         plt.hist(interactionLengthList)
    # #         print(totalInteractionsNumber, np.mean(interactionLengthList), np.std(interactionLengthList), print(len(listOfVeh[0])))
    # #         plt.show()
    #
