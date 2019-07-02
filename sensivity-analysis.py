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

c = 0

for distribution in world.userInputs[0].distributions:
    print('ah')
    world = network.World.load('simple-net.yml')

    if world.userInputs[0].distributions[distribution].loc is not None:
        world.userInputs[0].distributions[distribution].loc *= (1+interface.variationRate)
    else:
        world.userInputs[0].distributions[distribution].degeneratedConstant *= (1 + interface.variationRate)
    analysis = an.Analysis(c, world=world, seed=sim.seed)
    analysis.saveParametersToTable('world.db', sim.seed)

    for seed in seeds:
        analysis.seed = seed
        sim.seed = seed
        print('ok')
        sim.run(world)
        analysis.evaluate(ttcFilter=20, speedDifferential=1)
        analysis.saveIndicators('world.db')

    c += 1
# toolkit.callWhenDone()
