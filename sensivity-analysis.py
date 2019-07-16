# import argparse
#
# import pandas as pd
import analysis as an
import interface as iface
import network
import simulation
# import toolkit

world = network.World.load('cross-net.yml')

sim = simulation.Simulation.load('config.yml')
interface = iface.Interface(world)
interface.setSensitivityAnalysisParameters()

seeds = [sim.seed+i*sim.increment for i in range(sim.rep)]

anIdx = 0

for distribution in world.userInputs[1].distributions:
    world = network.World.load('cross-net.yml')
    analysis = an.Analysis(anIdx, world=world, seed=sim.seed)
    analysis.createAnalysisTable(sim.dbName)

    if world.userInputs[1].distributions[distribution].loc is not None:
        world.userInputs[1].distributions[distribution].loc *= (1+interface.variationRate)
    else:
        world.userInputs[1].distributions[distribution].degeneratedConstant *= (1 + interface.variationRate)

    analysis.saveParametersToTable('world.db')

    for seed in seeds:
        analysis.seed = seed
        sim.seed = seed
        sim.run(world)
        analysis.evaluate(sim.timeStep, sim.duration)
        world.saveObjects(sim.dbName, seed, anIdx)
        world.saveTrajectoriesToDB(sim.dbName, seed, anIdx)
        analysis.saveIndicators('world.db')

    anIdx += 1
    analysis.saveParametersToTable(sim.dbName)