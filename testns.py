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
        # while t <= vi.cumulatedHeadways[0] < t + sim.timeStep and len(vi.cumulatedHeadways)>0:
        for elt in vi.cumulatedHeadways:
            if t <= vi.cumulatedHeadways[0] < t + sim.timeStep:
                world.alignments[vi.alignmentIdx].vehicles.append(world.initVehicleOnAligment(vi.alignmentIdx,
                                                                                              [vi.cumulatedHeadways[0],
                                                                                               sim.duration]))
                vi.cumulatedHeadways.pop(0)
        # pass

        # todo: trouver les nouveaux vehicules apparaissant dans [t, t+timeStep[ et creer un MovingObject correspondant

    # pass
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
                    v.curvilinearPositions.addPositionSYL(-v.dn + v.desiredSpeed * t,
                                                          0,
                                                          al.idx)
            else:
                # sinon on met a jour les positions selon la valeur de t par rapport a celle du temps de reaction du conducteur
                if idx - 1 >= 0:

                    if t > v.reactionTime:
                        previousVehicleCurvilinearPositionAtPrecedentTime = \
                            al.vehicles[idx - 1].curvilinearPositions[-int(round(v.reactionTime))][0]  # t-v.reactionTime
                    else:
                        previousVehicleCurvilinearPositionAtPrecedentTime = \
                            al.vehicles[idx - 1].curvilinearPositions[0][0]

                else:
                    previousVehicleCurvilinearPositionAtPrecedentTime = -v.dn + v.desiredSpeed * t

                v.updateCurvilinearPositions(method="newell",
                                             timeStep=sim.timeStep,
                                             leaderVehicleCurvilinearPositionAtPrecedentTime=previousVehicleCurvilinearPositionAtPrecedentTime,
                                             nextAlignment_idx=v.curvilinearPositions.lanes[0],
                                             changeOfAlignment=False)
