import numpy as np
from SALib.analyze import sobol
from SALib.sample import saltelli
from progress.bar import Bar
import analysis
import network
import simulation
import toolkit


problem = {
    'num_vars': 5,
    'names': ['d', 'headway', 'length', 'speed', 'tau'],
    'bounds': [[7.33, 9.33],
           [2.0001633772214027, 6.936204757259126],
           [6, 8],
           [11, 17],
           [1.5, 3]
          ]}

paramValues = saltelli.sample(problem, 20)
Y = np.zeros([paramValues.shape[0]])
bar = Bar('Processing', max=paramValues.shape[0])

for i, X in enumerate(paramValues):
    bar.next()
    world = network.World.load('simple-net.yml')
    sim = simulation.Simulation.load('config.yml')
    Y[i] = analysis.evaluateModel(X, world, sim)

Si = sobol.analyze(problem, Y, print_to_console=True)
toolkit.saveYaml('outputData/sensitivity-analysis/modelOutputs.yml', Y)
toolkit.callWhenDone()
bar.finish()
