import matplotlib.pyplot as plt
from trafficintelligence import moving

import toolkit


def getHeadwayValues(world):
    headways = []
    for ui in world.userInputs:
        headways.append(ui.headways[0:len(ui.alignment.vehicles)])
    return headways


def getDistanceValuesBetweenUsers(world, user0, user1, minCoexistenceDurationValue, plot=False, withTrajectories=False):
    """script to get distance between a pair of vehicles in a car following situation """
    # todo : docstrings
    if user0.timeInterval is not None and user1.timeInterval is not None:
        inter = moving.TimeInterval.intersection(user0.timeInterval, user1.timeInterval)
        if len(list(inter)) >= minCoexistenceDurationValue:
            d = []
            for t in range(inter.first, inter.last+1):
                d.append(world.distanceAtInstant(user0, user1, t))
            if plot:
                plt.plot(list(moving.TimeInterval(inter.first, inter.last+1)), d)
                if withTrajectories:
                    user0.plotCurvilinearPositions()
                    user1.plotCurvilinearPositions()
            return d


def getMinDistanceBetweenEachPairCF(world, minCoexistenceDurationValue):
    """script to get min of distances between each pair of vehicles crossing in an intersection  """
    minDistances = []
    for ui in world.userInputs:
        for k in range(len(ui.alignment.vehicles) - 1):
            if getDistanceValuesBetweenUsers(world, ui.alignment.vehicles[k], ui.alignment.vehicles[k+1], minCoexistenceDurationValue):
                minDistances.append(min(getDistanceValuesBetweenUsers(world, ui.alignment.vehicles[k], ui.alignment.vehicles[k+1], minCoexistenceDurationValue)))
    return minDistances


def minDistanceChecked(world, user0, user1, t, dmin):
    """ checks if the minimum distance headway between two vehicles is verified
    in a car following situation : i is the leader vehicle and j is the following vehicle"""
    d = world.distanceAtInstant(user0, user1, t)
    if d:
        if d >= dmin:
            return True
        else:
            return False


def isAnEncounter(world, user0, user1, t, dmin):
    """ checks if there is an encounter between two vehicules
    leaderAlignmentIdx and followerAlignmentIdx are integers
    i,j : integers
    t : time, integer
    dmin : float  """
    if world.minDistanceChecked(user0, user1, t, dmin) is not None:
        if world.minDistanceChecked(user0, user1, t, dmin):
            return False
        else:
            return True


def getInteractionsDuration(world, dmin, inLine=False):
    """ counts according to the selected method (cross or inLine)
     the number of interactions taking place at a distance smaller than dmin.
    """
    if inLine:
        result = {}
        # pour chaque userInput
        for uiIdx, ui in enumerate(world.userInputs):
            # pour chaque vehicule présent : sauf le dernier
            for h in range(0, len(ui.alignment.vehicles) - 1):
                # si les deux vehicules sont générés
                if ui.alignment.vehicles[h].timeInterval is not None and ui.alignment.vehicles[h+1].timeInterval is not None:
                    # recuperer l'intervalle de coexistence des vehicules
                    inter = moving.TimeInterval.intersection(ui.alignment.vehicles[h].timeInterval, ui.alignment.vehicles[h+1].timeInterval)
                    # initialiser resultat(paire de vehicules concernées : leader.num, follower.num)
                    result[(ui.alignment.vehicles[h].num, ui.alignment.vehicles[h + 1].num)] = []
                    # pour chaque instant de l'intervalle de coexistence
                    for t in list(inter):
                        # si il y a une rencontre entre les 2 vehicules à l'instant t : ajouter 1 à la liste des rencontres :resultat(paire)
                        if world.isAnEncounter(ui.alignment.vehicles[h], ui.alignment.vehicles[h + 1], t, dmin):
                            result[(ui.alignment.vehicles[h].num, ui.alignment.vehicles[h + 1].num)].append(1)
                        # sinon : ajouter 0 à cette même liste
                        else:
                            result[(ui.alignment.vehicles[h].num, ui.alignment.vehicles[h + 1].num)].append(0)
        # une fois les listes complétées
        # pour chaque liste dans resultat(paire) : transformer la liste en [décompte des 1 = nombre d'interactions, longueur des interactions]
        for pair in result:
            result[pair] = [toolkit.countElementInList(result[pair], 1)] + toolkit.makeSubListFromList(result[pair], 1)
        return result

    elif not inLine:
        pass
    else:
        print('error in method name, method name should be "inline" or "crossing"')






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
