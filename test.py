from trafficintelligence import moving
import objectsofworld
import toolkit
import math
import random
import numpy as np

world = objectsofworld.World.load('default.yml')
sim = toolkit.load_yaml('config.yml')


def run(worldFile, configFile):
    """
    execution of a single simulation with a particular set of parameters for a world representation.
    Includes : car following model + gap accetance + lane change model.

    Parameters :

    worldFile : world object including the geometric characteristics of the intersection being studied, yaml file previously loaded via toolkit method


    configFile : yaml configuration file previously loaded via toolkit method
#     """
    alignments = world.getAlignments()

    vehiclesInitialization = []
    increment = 0

    for alignment in alignments:
        seed = configFile.seed + increment
        increment += 1
        v0 = random.normalvariate(15, 3)

        intervalsOfVehicleExistenceOnVehicleInput = toolkit.saveHeadwaysAsIntervals(
            worldFile.vehicleInputs[0].generateHeadways(
                sample_size=math.ceil(worldFile.vehicleInputs[0].volume * configFile.duration / 3600) - 1,
                seed=seed,
                distribution='exponential'),
            configFile.duration)
        firstVehicleOnAlignment = moving.MovingObject()

        firstVehicleOnAlignment.velocities = [v0] * round(configFile.duration / configFile.timeStep)
        firstVehicleOnAlignment.velocities = moving.CurvilinearTrajectory.generate(0,
                                                                                   0,
                                                                                   1,
                                                                                   None)
        for k in range(1, math.ceil(configFile.duration / configFile.timeStep)):
            firstVehicleOnAlignment.velocities.addPositionSYL(v0, 0, None)

        firstVehicleOnAlignment.vehicleLength = 7
        firstVehicleOnAlignment.desiredSpeed = v0
        firstVehicleOnAlignment.timeInterval = intervalsOfVehicleExistenceOnVehicleInput[0]
        firstVehicleOnAlignment.curvilinearPositions = moving.CurvilinearTrajectory.generate(0,
                                                                                             0,
                                                                                             math.ceil(
                                                                                                 firstVehicleOnAlignment.timeInterval[
                                                                                                     0] / configFile.timeStep) - 1,
                                                                                             alignment.idx)

        firstVehicleOnAlignment.curvilinearPositions.concatenate(moving.CurvilinearTrajectory.generate(0,
                                                                                                       v0 * configFile.timeStep,
                                                                                                       math.ceil((
                                                                                                                         configFile.duration / configFile.timeStep) - (
                                                                                                                         firstVehicleOnAlignment.timeInterval[
                                                                                                                             0] / configFile.timeStep)),
                                                                                                       alignment.idx))

        firstVehicleOnAlignment.reactionTime = random.normalvariate(2.5, 1)

        vehiclesGeneratedByVehicleInput = [firstVehicleOnAlignment] + worldFile.initVehiclesOnAligment(
            int(alignment.idx),
            math.ceil(worldFile.vehicleInputs[int(alignment.idx)].volume * configFile.duration / 3600) - 1,
            intervalsOfVehicleExistenceOnVehicleInput)
        vehiclesInitialization.append(vehiclesGeneratedByVehicleInput)

        # modification de la premiere coordonnee des vehicules
        #
        for k in range(1, len(vehiclesInitialization[int(alignment.idx)])):
            vehiclesInitialization[int(alignment.idx)][k].curvilinearPositions.setPosition(i=0, s=
            vehiclesInitialization[int(alignment.idx)][k - 1].curvilinearPositions[0][0] -
            vehiclesInitialization[int(alignment.idx)][k].dn, y=0, lane=int(alignment.idx))  #

    for initializedVehicles in vehiclesInitialization:
        for k in range(1, len(initializedVehicles)):
            # pour tous les movingObjects sauf le premier qui est initialise manuellement

            reactionTime = initializedVehicles[k].reactionTime / configFile.timeStep
            creationTimeOfCurrentVehicle = initializedVehicles[k].timeInterval[0] / configFile.timeStep
            t = 1

            while 0 < t < math.ceil(configFile.duration / configFile.timeStep):
                # print('entre dans boucle')
                # print(t)
                # for t in range(1, math.ceil(configFile.duration / configFile.timeStep)):
                # boucle allant de 1 (premiere coordonnee deja initialisee) à la durée de la simulation

                #####  1ere boucle
                while (not (alignments[int(initializedVehicles[k].curvilinearPositions.lanes[t-1])].alignmentHasROW())
                       and alignments[
                           initializedVehicles[k].curvilinearPositions.lanes[t-1]].controlDevice.isVehicleAtControlDevice(
                            initializedVehicles[k], t - 1, 0.5)):
                    # marque le stop durant 1s
                    if initializedVehicles[k].velocities[t-1][0] == 0:
                        for h in range(0, int(1 / configFile.timeStep)):
                            initializedVehicles[k].updateCurvilinearPositions(method="newell",
                                                                              timeStep=configFile.timeStep,
                                                                              leaderVehicleCurvilinearPositionAtPrecedentTime=
                                                                              initializedVehicles[k].curvilinearPositions[
                                                                                  t - 1][0] + initializedVehicles[k].dn,
                                                                              nextAlignment_idx=initializedVehicles[
                                                                                  k].curvilinearPositions.lanes[0],
                                                                              changeOfAlignment=False)

                            # determination du temps d'arrivee a l'intersection = temps d'arrivee + temps de stop (1sec)
                            arrivalTimeAtCrossing = int(initializedVehicles[k].curvilinearPositions.positions[0].index(
                                toolkit.find_nearest(np.array(initializedVehicles[k].curvilinearPositions.positions[0]), 600)) + 1/configFile.timeStep)
                            time = arrivalTimeAtCrossing

                    else:
                        arrivalTimeAtCrossing = int(initializedVehicles[k].curvilinearPositions.positions[0].index(
                            toolkit.find_nearest(np.array(initializedVehicles[k].curvilinearPositions.positions[0]), 600)))

                        time = arrivalTimeAtCrossing
                     
                    # determination du prochain vehicule prioritaire a l'instant  d'arrivee a l'intersection
                    rowVehicle = worldFile.findApprocachingVehicleOnMainAlignment(time, 0,
                                                                                  vehiclesInitialization[0])
                    rowVehicleAlignment = int(vehiclesInitialization[0][rowVehicle].curvilinearPositions.lanes[time])
                    # deuxieme boucle
                    # observation du creneau
                    observedGap = toolkit.timeGap(worldFile, vehiclesInitialization[0][rowVehicle], rowVehicleAlignment, arrivalTimeAtCrossing)
                    criticalGap = initializedVehicles[k].criticalGap
                    while (observedGap < criticalGap):# and t < math.ceil(configFile.duration / configFile.timeStep)):
                        #si le creneau observé est plus petit que le creneau critique : on ne passe pas
                        for index in range(math.ceil(observedGap)):
                            initializedVehicles[k].updateCurvilinearPositions(method="newell",
                                                                              timeStep=configFile.timeStep,
                                                                              leaderVehicleCurvilinearPositionAtPrecedentTime=
                                                                              initializedVehicles[
                                                                                  k].curvilinearPositions[t - 1][0] +
                                                                              initializedVehicles[k].dn,
                                                                              nextAlignment_idx=initializedVehicles[
                                                                                  k].curvilinearPositions.lanes[0],
                                                                              changeOfAlignment=False)
                        t = arrivalTimeAtCrossing + math.ceil(observedGap)
                        rowVehicle = rowVehicle + 1  # worldFile.findApproachingVehicleOnMainAlignment(time, mainAlignment, listOfVehiclesOnMainAlignment)
                        observedGap = toolkit.timeGap(worldFile, rowVehicle, rowVehicleAlignment, t)

                    else:
                        # sinon on passe
                        initializedVehicles[k].updateCurvilinearPositions(method="newell",
                                                                          timeStep=configFile.timeStep,
                                                                          leaderVehicleCurvilinearPositionAtPrecedentTime=
                                                                          initializedVehicles[k].curvilinearPositions[
                                                                              int(t-reactionTime)][0],  #t-1 ? 
                                                                          nextAlignment_idx=initializedVehicles[
                                                                              k].curvilinearPositions.lanes[0],
                                                                          changeOfAlignment=False)
                        t = t + 1
                else:
                    # mise a jour selon Newell

                    if t < creationTimeOfCurrentVehicle:  # and initializedVehicles[k].curvilinearPositions[t-1][0]>=0 :
                        # tant que t < instant de creation du vehicule courant (k), la position vaut l'espacement dn entre les 2 vehicules

                        initializedVehicles[k].curvilinearPositions.addPositionSYL(
                            initializedVehicles[k].curvilinearPositions[0][0], 0,
                            initializedVehicles[k].curvilinearPositions.lanes[0])
                        initializedVehicles[k].velocities.addPositionSYL(initializedVehicles[k].desiredSpeed, 0, None)
                        t = t + 1

                    else:
                        # une fois que t=>  instant de creation du vehicule on procede a la mise a jour des positions selon newell
                        if t > reactionTime:
                            previousVehicleCurvilinearPositionAtPrecedentTime = \
                                initializedVehicles[k - 1].curvilinearPositions[t - math.ceil(reactionTime)][0]
                            # t = t + 1
                        else:
                            previousVehicleCurvilinearPositionAtPrecedentTime = \
                                initializedVehicles[k].curvilinearPositions[t - 1][0] + initializedVehicles[k].dn
                            # t = t + 1

                        initializedVehicles[k].updateCurvilinearPositions(method="newell",
                                                                          timeStep=configFile.timeStep,
                                                                          leaderVehicleCurvilinearPositionAtPrecedentTime=previousVehicleCurvilinearPositionAtPrecedentTime,
                                                                          nextAlignment_idx=
                                                                          initializedVehicles[
                                                                              k].curvilinearPositions.lanes[0],
                                                                          changeOfAlignment=False)
                        t = t + 1
    return vehiclesInitialization


# trajectoryData = run(world, sim)
# temp = world.countAllEncounters(trajectoryData,50)
# toolkit.trace(run(world, sim)[0], 'x')
toolkit.trace(run(world, sim)[1], 'x')

# while not(alignments[initializedVehicles[k].curvilinearPositions.lanes[t]].alignmentHasROW())
#       and alignments[initializedVehicles[k].curvilinearPositions.lanes[t]].controlDevice.isVehicleaTCrossingPoint(initializedVehicles[k], t):
#     for k in range (0,1/configFile.timeStep):
#         initializedVehicles[k].updateCurvilinearPositions(method = 'newell',
#                                                           timeStep = configFile.timeStep,
#                                                           leaderVehicleCurvilinearPositionAtPrecedentTime = initializedVehicles[k].curvilinearPositions[t-1][0] + initializedVehicles[k].dn,
#                                                           nextAlignment_idx = initializedVehicles[k].curvilinearPositions.lanes[0],
#                                                           changeOfAlignment)
#
#     arrivalTimeAtCrossing = lpVehicle.curvilinearPositions.positions[0].index(1000) + 1/configFile.timeStep
#     time = arrivalTimeAtCrossing
#
#     rowVehicle = worldFile.findApprocachingVehicleOnMainAlignment(time, mainAlignment, listOfVehiclesOnMainAlignment)
#     rowVehicleAlignment = rowVehicle.curvilinearPositions.lanes[time]
#
#     observedGap = toolkit.timeGap(worldFile, rowVehicle, rowVehicleAlignment, arrivalTimeAtCrossing)
#
#     enter = True
#     while observedGap < initializedVehicles[k].criticalGap:
#         enter = False
#         initializedVehicles[k].updateCurvilinearPositions(method = 'newell',
#                                                           timeStep = configFile.timeStep,
#                                                           leaderVehicleCurvilinearPositionAtPrecedentTime = initializedVehicles[k].curvilinearPositions[t-1][0] + initializedVehicles[k].dn,
#                                                           nextAlignment_idx = initializedVehicles[k].curvilinearPositions.lanes[0],
#                                                           changeOfAlignment)
#         time = time + math.ceil(observedGap)
#         rowVehicle = rowVehicle + 1 #worldFile.findApproachingVehicleOnMainAlignment(time, mainAlignment, listOfVehiclesOnMainAlignment)
#         observedGap = toolkit.timeGap(worldFile, rowVehicle, rowVehicleAlignment, time)
#
#     else :
#         initializedVehicles[k].updateCurvilinearPositions(method = 'newell',
#                                                           timeStep = configFile.timeStep,
#                                                           leaderVehicleCurvilinearPositionAtPrecedentTime = initializedVehicles[k].curvilinearPositions[t][0] + initializedVehicles[k].dn,
#                                                           nextAlignment_idx = initializedVehicles[k].curvilinearPositions.lanes[0], changeOfAlignment)
# else:
#     mise a jour selon Newell : code effectué plus haut

if __name__ == "__main__":
    import doctest
    doctest.testmod()