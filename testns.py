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

for i in range(int(np.floor(sim.duration/sim.timeStep))):
    world.initUsers(i, sim.timeStep)

    # pass
    for al in world.alignments:
        for idx, v in enumerate(al.vehicles):

            # sinon on met a jour les positions selon la valeur de t par rapport a celle du temps de reaction du conducteur
            #NS: pourquoi ferait-on comme ça?? on devrait soit le faire dynamiquement à chaque pas de temps, soit le faire une fois à l'initalisation des véhicules
            if idx == 0:
                leaderVehicle = None
            else:
                leaderVehicle = al.vehicles[idx - 1]

            v.updateCurvilinearPositions(method="newell",
                                         timeStep=sim.timeStep,
                                         #leaderVehicle=leaderVehicle,
                                         nextAlignment_idx=0,
                                         changeOfAlignment=False,
                                         instant=i)
