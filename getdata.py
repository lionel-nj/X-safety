import network
import simulation
import makesimulation
import analysis

print('Enter seed value to use')
seed = input()

print('Enter the simulation duration')
duration = input()


enterNextValue = True
headwaysToModify = [[], []]
while enterNextValue:
    print('On which userInput would you liek to change the headways ?')
    ui = input()
    print('Enter headway values to try')
    h = input()
    headwaysToModify[int(ui)].append(float(h))
    print('add another headway values to try ? y/n')
    enterNextValue = input()
    if enterNextValue == 'y':
        enterNextValue = True
    else:
        enterNextValue = False

# modify seed value in config file
sim = simulation.load('config.yml')
sim.seed = seed
sim.duration = duration

# loop : for each user input then for every value of headway : modify config files then run simulation and save data
for i in range(len(headwaysToModify)):
    for headway in headwaysToModify[i]:
        world = network.load('simple-net.yml')
        for userInput in world:
            userInput.distributions['headway']['scale'] = headway

            # make simulations and analyses
            makesimulation.run(world, sim)
            analysis.run(world, sim)


