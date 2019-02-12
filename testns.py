import objectsofworld
import toolkit
import itertools
import random
import numpy as np

world = objectsofworld.World.load('simple-net.yml')
sim = toolkit.load_yaml('config.yml')

random.seed(sim.seed)

for vi in world.vehicleInputs:
    # link to alignment
    for al in world.alignments:
        if al.idx == vi.alignmentIdx:
            vi.alignment = al
    vi.generateHeadways(duration=sim.duration, seed=int(10 * random.random()))
    vi.cumulatedHeadways = list(itertools.accumulate(vi.headways))

# suggestion, a voir si c'est le plus pratique
for al in world.alignments:
    al.vehicles = []

for t in np.arange(0., sim.duration, sim.timeStep):
    for vi in world.vehicleInputs:
        for elt in vi.cumulatedHeadways:
            world.alignments[vi.alignmentIdx].vehicles.append(world.initVehicleOnAligment(vi.alignmentIdx,
                                                                                          [elt, sim.duration]))
            vi.cumulatedHeadways.pop(0)

        # todo: trouver les nouveaux vehicules apparaissant dans [t, t+timeStep[ et creer un MovingObject correspondant

        pass
    for al in world.alignments:
        for idx, v in enumerate(al.vehicles):

            if t < v.timeInterval[0]:
                # #si t < instant de creation du vehicule, la position vaut l'espacement dn entre les deux vehicules
                if idx - 1 >= 0:
                    v.curvilinearPositions.addPositionSYL(
                        al.vehicles[idx - 1].curvilinearPositions[0][0] - v.dn,
                        0,
                        al.idx)
                else:
                    v.curvilinearPositions.addPositionSYL(-v.dn,
                                                          0,
                                                          al.idx)
            else:
                # sinon on met a jour les positions selon la valeur de t par rapport a celle du temps de reaction du conducteur
                if t > v.reactionTime:
                    if idx - 1 >= 0:
                        previousVehicleCurvilinearPositionAtPrecedentTime = \
                            al.vehicles[idx - 1].curvilinearPositions[(t-v.reactionTime)/sim.timeStep][0] #t-v.reactionTime
                    else:
                        previousVehicleCurvilinearPositionAtPrecedentTime = 0
                else:
                    if idx - 1 >= 0:
                        previousVehicleCurvilinearPositionAtPrecedentTime = \
                            al.vehicles[idx - 1].curvilinearPositions[0][0]
                    else:
                        previousVehicleCurvilinearPositionAtPrecedentTime = v.desiredSpeed * sim.timeStep + v.dn

                v.updateCurvilinearPositions(method="newell",
                                             timeStep=sim.timeStep,
                                             leaderVehicleCurvilinearPositionAtPrecedentTime=previousVehicleCurvilinearPositionAtPrecedentTime,
                                             nextAlignment_idx=v.curvilinearPositions.lanes[0],
                                             changeOfAlignment=False)
            pass
