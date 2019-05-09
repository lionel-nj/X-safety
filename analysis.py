import matplotlib.pyplot as plt
from trafficintelligence import moving, events

import toolkit


def getHeadwayValues(world):
    """ script to return headway values of generated vehicules in world"""
    headways = []
    for ui in world.userInputs:
        headways.append(ui.headways[0:len(ui.alignment.users)])
    return headways


def getDistanceValuesBetweenUsers(world, roadUser1, roadUser2, plot=False):
    """script to get distance between a pair of vehicles"""
    if roadUser1.timeInterval is not None and roadUser2.timeInterval is not None:
        i = events.Interaction(useCurvilinear=True, roadUser1=roadUser1, roadUser2=roadUser2)
        i.computeIndicators(world=world, alignment1=world.travelledAlignments(roadUser1), alignment2=world.travelledAlignments(roadUser2))
        if plot:
            plt.plot(i.indicators['Distance'].values.keys(), list(i.indicators['Distance'].values.values()))
        return list(i.indicators['Distance'].values.values())


def getMinDistanceBetweenEachPairCF(world):
    """script to get min of distances between each pair of vehicles"""
    minDistances = []
    for ui in world.userInputs:
        for k in range(len(ui.alignment.users) - 1):
            if getDistanceValuesBetweenUsers(world, ui.alignment.users[k], ui.alignment.users[k+1]):
                minDistances.append(min(getDistanceValuesBetweenUsers(world, ui.alignment.users[k], ui.alignment.users[k+1])))
    return minDistances


def minDistanceChecked(world, user0, user1, t, dmin):
    """ checks if the minimum distance headway between two vehicles is verified
    in a car following situation : i is the leader vehicle and j is the following vehicle"""
    d = world.distanceAtInstant(user0, user1, t)
    if d is not None:
        if d >= dmin:
            return True
        else:
            return False
    else:
        return None


def isAnEncounter(world, user0, user1, t, dmin):
    """ checks if there is an encounter between two vehicules
    leaderAlignmentIdx and followerAlignmentIdx are integers
    i,j : integers
    t : time, integer
    dmin : float  """
    if minDistanceChecked(world, user0, user1, t, dmin) is not None:
        if minDistanceChecked(world, user0, user1, t, dmin):
            return False
        else:
            return True
    else:
        return None


def getInteractionsDuration(world, dmin, inLine=False):
    """ counts according to the selected method (cross or inLine)
     the number of interactions taking place at a distance smaller than dmin.
    """
    if inLine:
        result = {}
        # pour chaque userInput
        for uiIdx, ui in enumerate(world.userInputs):
            # pour chaque vehicule présent : sauf le dernier
            for h in range(0, len(ui.alignment.users) - 1):
                # si les deux vehicules sont générés
                if ui.alignment.users[h].timeInterval is not None and ui.alignment.users[h+1].timeInterval is not None:
                    # recuperer l'intervalle de coexistence des vehicules
                    inter = moving.TimeInterval.intersection(ui.alignment.users[h].timeInterval, ui.alignment.users[h+1].timeInterval)
                    # initialiser resultat(paire de vehicules concernées : leader.num, follower.num)
                    result[(ui.alignment.users[h].num, ui.alignment.users[h + 1].num)] = []
                    # pour chaque instant de l'intervalle de coexistence
                    for t in list(inter):
                        # si il y a une rencontre entre les 2 vehicules à l'instant t : ajouter 1 à la liste des rencontres :resultat(paire)
                        if isAnEncounter(world, ui.alignment.users[h], ui.alignment.users[h + 1], t, dmin):
                            result[(ui.alignment.users[h].num, ui.alignment.users[h + 1].num)].append(1)
                        # sinon : ajouter 0 à cette même liste
                        else:
                            result[(ui.alignment.users[h].num, ui.alignment.users[h + 1].num)].append(0)
        # une fois les listes complétées
        # pour chaque liste dans resultat(paire) : transformer la liste en [décompte des 1 = nombre d'interactions, longueur des interactions]
        for pair in result:
            result[pair] = [toolkit.countElementInList(result[pair], 1)] + toolkit.makeSubListFromList(result[pair], 1)
        return result

    elif not inLine:
        pass
    else:
        print('error in method name, method name should be "inline" or "crossing"')