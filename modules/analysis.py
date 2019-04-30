import matplotlib.pyplot as plt

from trafficintelligence import moving

# world = network.World.load('world.yml')
# sim = simulation.Simulation.load('inputData/config.yml')
# analysisParameters = toolkit.loadYaml('inputData/analysis-parameters.yml')


def getDistanceValuesBetweenUsers(world, user0num, user1num, minCoexistenceDurationValue):
    """script to get distance between a pair of vehicles in a car following situation """
    # todo : dostrings
    user0 = world.getUserByNum(user0num)
    user1 = world.getUserByNum(user1num)
    inter = moving.TimeInterval.intersection(user0.timeInterval, user1.timeInterval)
    if len(list(inter)) >= minCoexistenceDurationValue:
        d = []
        for t in range(inter.first, inter.last):
            d.append(world.distanceAtInstant(user0, user1, t))
        return d
    else:
        print("vehicles do not meet the coexistence duration condition therefore program will not compute distance list")


def getMinDistanceBetweenEachPairCF(world, minCoexistenceDurationValue):
    """script to get min of distances between each pair of veehicles crossing in an intersection  """
    minDistances = []
    for al in world.alignments:
        for k in range(len(al.vehicles) - 1):
            if getDistanceValuesBetweenUsers(world, al.vehicles[k].num, al.vehicles[k+1].num, minCoexistenceDurationValue):
                minDistances.append((min(getDistanceValuesBetweenUsers(world, al.vehicles[k].num, al.vehicles[k+1].num, minCoexistenceDurationValue)), al.vehicles[k].num, al.vehicles[k-1].num), al.vehicles[k].curvilinearPositions[-1][2])
            # il manque deux éléments minDistance à rajouter à la liste : dernier de 2 et premier de 1 // dernier de 1 et premier de 0
    return minDistances


def getMinDistanceValueIndex(world, minCoexistenceDurationValue, user0num, user1num):
    pass


def speedDifferentialAtMinDistanceValueIndex(world, minCoexistenceDurationValue, user0num, user1num,):
    pass


def getHeadway(world, user0num, user1num):
    h = abs(world.getUserByNum(user0num).timeAtS0 - world.getUserByNum(user1num).timeAtS0)
    return h


def getHeadwayValues(world):
    headways = []
    for al in world.alignments:
        for k in range(1, len(al.vehicles) - 1):
            headways.append(getHeadway(world, al.vehicles[k].num, al.vehicles[k+1].num))
    return headways


def ttcValueAt(world, user0, user1, t):
    # si vitesse suiveur > vitesse leader à instant t: alors ttc = (xleader-xfollo-leaderLength)/(Vfollower - Vleader) ,
    # plutot que les xi on utilisera la fonction de distance implmentée dans la classe World
    if t >= min(user0.getFirstInstant(), user1.getFirstInstant()):
        v0 = user0.getCurvilinearVelocityAtInstant(t)[0]
        v1 = user1.getCurvilinearVelocityAtInstant(t)[0]
        if v1 > v1:
            ttc = world.distanceAtInstant(user0, user1, t)/(v1-v0)
            return ttc


def getTTCValues(world, user0, user1):
    inter = moving.TimeInterval.intersection(user0.timeInterval, user1.timeInterval)
    ttc = []
    inter = list(inter)
    inter.pop()
    for t in inter:
        ttc.append(ttcValueAt(world, user0, user1, t))
    ttc = list(filter(None, ttc))
    return ttc


def getTTCValuesForEachPairOfVehicles(world):
    ttc = []
    minTTCValues = []
    for al in world.alignments:
        for k in range(0, len(al.vehicles)):
            ttc.append(getTTCValues(world, al.vehicles[k], al.vehicles[k - 1]))
    for el in ttc:
        if el:
            minTTCValues.append(min(el))
    return ttc, minTTCValues


def getHist(values, xlabel, ylabel):
    """script to get min distance value histogram"""
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.hist(values)
    plt.show()


def countInteractions(world, user0, user1):
    pass

#
#
#
#
# # def run(worldFile, simulationParameters, analysisParameters):

#
#     # converting curvilinear trajectories/velocities to cartesian trajectories/velocities
#     # worldFile.convertSYtoXY()
#     # predictionParams = prediction.CVExactPredictionParameters(useCurvilinear=True)
#     df = pd.DataFrame(columns = ['seed', 'duration', 'h0', 'volume', '# of generated vehicle', 'volume (true)', 'headway(true)', 'distance threshold', 'interaction number', '%interactions'])
#
#
#     # worldFile.createCSV('analysisFile.csv')
#
#     for al in worldFile.alignments:
#         i = 0
#         for headwayValue in analysisParameters['headwayValues'][al.idx]:
#             worldFile.userInputs[al.idx].distributions['headway'].scale = headwayValue
#             worldFile = makesimulation.run(worldFile, simulationParameters)
#             listOfVeh = worldFile.getNotNoneVehiclesInWorld()
#
#             for minInteractionDistancesValue in analysisParameters['minInteractionDistancesValues'][al.idx]:
#
#                 # collect for each pair of vehicle the list of times when the inter-vehicle distance is less than the threshold
#                 # number of interactions for each pair of vehicles : 1 if the pair id the distance between the 2 vehicles <= distance threshold, else 0
#                 interactionTime = worldFile.count('inLine', minInteractionDistancesValue, al.idx)
#
#                 # the duration of each interaction between two vehicles : count the number of consecutive 1 in the previously completed list : interactionTime
#                 interactionDuration = {}
#                 for el in interactionTime:
#                     if el:
#                         interactionDuration[el] = toolkit.makeSubListFromList(interactionTime[el], 1)
#
#                 # count for each pair of vehicle the number of interactions and link it to their duration
#                 interactionsCharacteristics = {}
#                 for item in interactionDuration:
#                     interactionsCharacteristics[item] = (len(interactionDuration[item]), interactionDuration[item])
#
#                 # total number of interactions
#                 totalInteractionsNumber = 0
#                 for elt in interactionsCharacteristics:
#                     totalInteractionsNumber += interactionsCharacteristics[elt][0]
#
#                 vehiclesGenerated = len(listOfVeh[al.idx])-4
#                 volume = 3600/headwayValue
#                 volumeTrue = 3600 * len(listOfVeh[al.idx]) / simulationParameters.duration
#                 headwayTrue = 3600/volumeTrue
#
#                 data = [simulationParameters.seed, simulationParameters.duration, headwayValue, volume, vehiclesGenerated, volumeTrue, headwayTrue, minInteractionDistancesValue, totalInteractionsNumber, 100*totalInteractionsNumber/vehiclesGenerated]
#                 df.loc[i] = data
#                 i += 1
#         # displaying interactions # = f(headway)
#         # for each min distance
#         for values in analysisParameters['minInteractionDistancesValues'][al.idx]:
#             filter = df['distance threshold'] == values
#             tempDf = df.where(filter, inplace=False)
#             tempDf.dropna(axis=0, how='all', inplace=True)
#             plt.plot(tempDf['h0'].values, tempDf['%interactions'].values)
#         plt.legend(['d={}'.format(values) for values in analysisParameters['minInteractionDistancesValues'][al.idx]])
#         plt.savefig('graphique-seed={}-duration={}.png'.format(simulationParameters.seed, simulationParameters.duration))
#         df.to_csv('analysisFile-seed={}-duration={}.csv'.format(simulationParameters.seed, simulationParameters.duration), index=False)
#
#
#
#     # return df
#
#                 # worldFile.addElementToAnalysisFile('analysisFile.csv', data)
#
#
#         #
#         # for al in worldFile.alignments:
#         #     # defining interactions
#         #     al.points.computeCumulativeDistances()
#         #     interactions = []
#         #     for userIdx in range(len(listOfVeh[al.idx]) - 1):
#         #         interactions.append(events.Interaction(useCurvilinear=True, roadUser1=listOfVeh[al.idx][userIdx], roadUser2=listOfVeh[al.idx][userIdx + 1]))
#
#         #     # computing interactions
#         #     for inter in interactions:
#         #         inter.computeIndicators(alignment1=al, alignment2=al)
#         #         inter.computeCrossingsCollisions(
#         #             predictionParameters=predictionParams,
#         #             collisionDistanceThreshold=7,
#         #             timeHorizon=300,
#         #             useCurvilinear=True,
#         #             alignment1=al,
#         #             alignment2=al)
#         # #
#         #     # getting the ttc-time list for each interaction if ttc has been computed (2)
#         #     TTCs = {}
#         #     times = []
#         #     for inter in interactions:
#         #         if 'Time to Collision' in inter.indicators.keys():
#         #             TTCs[(inter.roadUser1.num, inter.roadUser2.num)] = []
#         #             times.append([])
#         #             for key, value in enumerate(inter.indicators['Time to Collision']):
#         #                 TTCs[(inter.roadUser1.num, inter.roadUser2.num)].append(value)
#         #                 times[-1].append(key)
#         # return interactions
#         #
#         # #     # computing ttc values (1)
#         #     for idx in range(len(listOfVeh[al.idx]) - 1):
#         #         TTCs[idx, idx + 1] = listOfVeh[al.idx][idx + 1].computeTTC(simulationParameters.timeStep)
#         #
#         #     # getting ttc values (1)
#         #     ttcValues = [[] for _ in range(len(TTCs))]
#         #     times = [[] for _ in range(len(TTCs))]
#         #
#         #     for idx, ttc in enumerate(TTCs):
#         #         for item in TTCs[ttc]:
#         #             if item is not None:
#         #                 ttcValues[idx].append(item[0])
#         #                 times[idx].append(item[1])
#         #         plt.plot(times[idx], ttcValues[idx])
#         #
#         #     # plotting ttc value for each interactions (2)
#         #     for timeValues, ttcValues in zip(times, TTCs):
#         #         plt.plot(timeValues, TTCs[ttcValues])
#         #
#         #     # display
#         #     plt.xlabel('time(s/10)')
#         #     plt.ylabel('TTC (Time To Collision)')
#         #     plt.show()
#         #     plt.close()
#         #
#         #     # getting minimum values of ttc (1)
#         #     minTTCsValues = []
#         #     # for ttcList in ttcValues:
#         #     #     if ttcList:
#         #     #         minTTCsValues.append(min(ttcList))
#         #
#         #     # getting minimum values of ttc (2)
#         #     for ttcList in TTCs:
#         #             minTTCsValues.append(min(TTCs[ttcList]))
#         #
#         #     # histogram of min TTC values
#         #     plt.hist(minTTCsValues, bins='auto')
#         #
#         #     # collect for each pair of vehicle the list of times when the inter-vehicle distance is less than the threshold
#         #     # number of interactions for each pair of vehicles
#         #     d = [15, 17, 20]
#         #     for distance in d:
#         #         interactionTime = worldFile.count('inLine', distance, al.idx)
#         #
#         #         # get the duration of each interaction between two vehicles
#         #         interactionDuration = {}
#         #         for el in interactionTime:
#         #             if el:
#         #                 interactionDuration[el] = toolkit.makeSubListFromList(interactionTime[el], 1)
#         #
#         #         # count for each pair of vehicle the number of interactions and link it to their duration
#         #         interactionsCharacteristics = {}
#         #         for item in interactionDuration:
#         #             interactionsCharacteristics[item] = (len(interactionDuration[item]), interactionDuration[item])
#         #
#         #         # total number of interactions
#         #         totalInteractionsNumber = 0
#         #         interactionLengthList = []
#         #         for elt in interactionsCharacteristics:
#         #             totalInteractionsNumber += interactionsCharacteristics[elt][0]
#         #             for times in interactionsCharacteristics[elt][1]:
#         #                 if interactionsCharacteristics[elt][1]:
#         #                     interactionLengthList.append(times)
#         # #
#         # #         plt.hist(interactionLengthList)
#         # #         print(totalInteractionsNumber, np.mean(interactionLengthList), np.std(interactionLengthList), print(len(listOfVeh[0])))
#         # #         plt.show()
#         #
