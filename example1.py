#! /usr/bin/env python3

import network
import simulation

world = network.World.load('cross-net.yml')
sim = simulation.Simulation.load('config.yml')
sim.run(world)
world.plotUserTrajectories(sim.timeStep)

# analysis = an.Analysis(world=world, seed=sim.seed)
# analysis.evaluate(sim.timeStep, sim.duration)
# if sim.dbName is not None :
#     network.createNewellMovingObjectsTable(sim.dbName)
#     world.saveObjects(sim.dbName, sim.seed, analysis.idx)
#     world.saveTrajectoriesToDB(sim.dbName, sim.seed, analysis.idx)
#     an.createAnalysisTable(sim.dbName)
#     analysis.saveParametersToTable(sim.dbName)
#     analysis.saveIndicators(sim.dbName)

import events

minTTCs = {1:[], 2:[]}
minDistances ={1:[], 2:[]}
interactions = []
for inter in world.completedInteractions:
    if inter.categoryNum is not None:
        distance = inter.getIndicator(events.Interaction.indicatorNames[2])
        if distance is not None:
            minDistances[inter.categoryNum].append(distance.getMostSevereValue(1))
        ttc = inter.getIndicator(events.Interaction.indicatorNames[7])
        if ttc is not None:
            minTTC = ttc.getMostSevereValue(1)*sim.timeStep  # seconds
            if minTTC < 0:
                print(inter.num, inter.categoryNum, ttc.values)
            if minTTC < 20:
                minTTCs[inter.categoryNum].append(minTTC)
            values = ttc.getValues(False)
            if len(values) > 5:
                interactions.append(inter)

