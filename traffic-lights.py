#! /usr/bin/env python3
import numpy as np

import analysis as an
import events
import network
import simulation
import toolkit

trafficlights_world = network.World.load('trafficlights.yml')
trafficlights_sim = simulation.Simulation.load('trafficlights-config.yml')
# trafficlights_sim.dbName = 'trafficlights-stop-data.db'
trafficlights_analysis = an.Analysis(idx=0, world=trafficlights_world, seed=trafficlights_sim.seed)
trafficlights_analysis.interactions = []

seeds = [trafficlights_sim.seed+i*trafficlights_sim.increment for i in range(trafficlights_sim.rep)]
trafficlights_minTTCs = {1: [], 2: []}
trafficlights_minDistances = {1: {}, 2: {}}
for categoryNum in trafficlights_minDistances:
    for seed in seeds:
        trafficlights_minDistances[categoryNum][seed] = []

trafficlights_PETs = []
trafficlights_interactions = []

trafficlights_rearEndnInter10 = []
trafficlights_rearEndnInter20 = []
trafficlights_rearEndnInter50 = []

trafficlights_sidenInter10 = []
trafficlights_sidenInter20 = []
trafficlights_sidenInter50 = []


#analysis.saveParametersToTable(sim.dbName)
for seed in seeds:
    print(str(seeds.index(seed)+1) + 'out of {}'.format(len(seeds)))
    trafficlights_world = network.World.load('trafficlights.yml')
    trafficlights_sim.seed = seed
    trafficlights_sim.run(trafficlights_world)
    trafficlights_analysis.seed = seed
    trafficlights_analysis.interactions.append(trafficlights_world.completedInteractions)
    for inter in trafficlights_world.completedInteractions:
        if inter.categoryNum is not None:
            trafficlights_distance = inter.getIndicator(events.Interaction.indicatorNames[2])
            if trafficlights_distance is not None:
                trafficlights_minDistances[inter.categoryNum][seed].append(trafficlights_distance.getMostSevereValue(1))
            trafficlights_ttc = inter.getIndicator(events.Interaction.indicatorNames[7])
            if trafficlights_ttc is not None:
                trafficlights_minTTC = trafficlights_ttc.getMostSevereValue(1)*trafficlights_sim.timeStep  # seconds
                if trafficlights_minTTC < 0:
                    print(inter.num, inter.categoryNum, trafficlights_ttc.values)
                if trafficlights_minTTC < 20:
                    trafficlights_minTTCs[inter.categoryNum].append(trafficlights_minTTC)
                values = trafficlights_ttc.getValues(False)
                if len(values) > 5:
                    trafficlights_interactions.append(inter)
            if inter.getIndicator(events.Interaction.indicatorNames[10]) is not None:
                trafficlights_PETs.append(inter.getIndicator(events.Interaction.indicatorNames[10]).getMostSevereValue(1))

    trafficlights_rearEndnInter10.append((np.array(trafficlights_minDistances[1][seed]) <= 10).sum())
    trafficlights_rearEndnInter20.append((np.array(trafficlights_minDistances[1][seed]) <= 20).sum())
    trafficlights_rearEndnInter50.append((np.array(trafficlights_minDistances[1][seed]) <= 50).sum())

    trafficlights_sidenInter10.append((np.array(trafficlights_minDistances[2][seed]) <= 10).sum())
    trafficlights_sidenInter20.append((np.array(trafficlights_minDistances[2][seed]) <= 20).sum())
    trafficlights_sidenInter50.append((np.array(trafficlights_minDistances[2][seed]) <= 50).sum())

trafficlights_nInter10 = {1: np.mean(trafficlights_rearEndnInter10), 2: np.mean(trafficlights_sidenInter10)}
trafficlights_nInter20 = {1: np.mean(trafficlights_rearEndnInter20), 2: np.mean(trafficlights_sidenInter20)}
trafficlights_nInter50 = {1: np.mean(trafficlights_rearEndnInter50), 2: np.mean(trafficlights_sidenInter50)}

resultstrafficlightsStop = {'minTTCS':trafficlights_minTTC,
                          'minDistances':trafficlights_minDistances,
                          'PETs':trafficlights_PETs,
                          'nInter10': trafficlights_nInter10,
                          'nInter20': trafficlights_nInter20,
                          'nInter50': trafficlights_nInter50,
                          'rearEndnInter10': trafficlights_rearEndnInter10,
                          'rearEndnInter20': trafficlights_rearEndnInter20,
                          'rearEndnInter50': trafficlights_rearEndnInter50,
                          'trafficlights_sidenInter10': trafficlights_sidenInter10,
                          'trafficlights_sidenInter20': trafficlights_sidenInter20,
                          'trafficlights_sidenInter50':trafficlights_sidenInter50}

toolkit.saveYaml('trafficlights-stop-results.yml', resultstrafficlightsStop)

toolkit.saveYaml('trafficlights-stop-minTTC.yml', trafficlights_minTTCs)
toolkit.saveYaml('trafficlights-stop-minDistances.yml', trafficlights_minDistances)
toolkit.saveYaml('trafficlights-stop-PETs.yml', trafficlights_PETs)

toolkit.callWhenDone()



# #### PDF COMPLETES
#
# ### TTC side
#
# trafficlights_histogram, trafficlights_bin_centers = np.histogram(trafficlights_minTTCs[2])#, bins=bins, normed=False)
#
# trafficlights_bin_centers = 0.5*(trafficlights_bin_centers[1:] + trafficlights_bin_centers[:-1])
#
# trafficlights_histogram2 = np.array([k for k in range(len(trafficlights_histogram))])
#
# for k in range(0, len(trafficlights_histogram)):
#     trafficlights_histogram2[k] = 100 * trafficlights_histogram[k] / len(trafficlights_minTTCs[2])
#
# plt.plot(trafficlights_bin_centers, trafficlights_histogram, label="trafficlights crossing")
#
# plt.xlabel('Side\ Time\ to \ Collision\ (s)$')
# plt.ylabel('$Number\ of\ observations$')
# plt.legend()
# plt.savefig('pdf-side-trafficlights-TTCs-raw.pdf')
# plt.close()
#
# plt.plot(trafficlights_bin_centers, trafficlights_histogram2, label="trafficlights crossing")
# plt.xlabel('$Side\ Time\ to \ Collision\ (s)$')
# plt.ylabel('$Frequency\ (\%)$')
# plt.legend()
# plt.savefig('pdf-side-trafficlights-TTCs-normed.pdf')
# plt.close()
#
# ### PET
#
# trafficlights_histogram, trafficlights_bin_centers = np.histogram(trafficlights_PETs)#, bins=bins, normed=False)
#
# trafficlights_bin_centers = 0.5*(trafficlights_bin_centers[1:] + trafficlights_bin_centers[:-1])
#
# trafficlights_histogram2 = np.array([k for k in range(len(trafficlights_histogram))])
#
# for k in range(0, len(trafficlights_histogram)):
#     trafficlights_histogram2[k] = 100 * trafficlights_histogram[k] / len(trafficlights_PETs)
#
# plt.plot(trafficlights_bin_centers, trafficlights_histogram, label="trafficlights crossing")
#
# plt.xlabel('Post\ Encroachment\ Time\ (s)$')
# plt.ylabel('$Number\ of\ observations$')
# plt.legend()
# plt.savefig('pdf-side-trafficlights-PETs-raw.pdf')
# plt.close()
#
# plt.plot(trafficlights_bin_centers, trafficlights_histogram2, label="trafficlights crossing")
# plt.xlabel('Post\ Encroachment\ Time\ (s)$')
# plt.ylabel('$Frequency\ (\%)$')
# plt.legend()
# plt.savefig('pdf-side-trafficlights-PETs-normed.pdf')
# plt.close()
#
#
# number1 = 0
# number2 = 0
# number3 = 0
# number4 = 0
# number5 = 0
# number6 = 0
# number7 = 0
# number8 = 0
# number9 = 0
# number10 = 0
# # zoom pdf TTC side
# for inter in toolkit.flatten(trafficlights_analysis.interactions):
#     if inter.categoryNum == 2:
#         if inter.getIndicator('Time to Collision') is not None:
#             if 0 <= inter.getIndicator('Time to Collision').getMostSevereValue(1) * .1 < 1:
#                 number1 += 1
#             elif 1 <= inter.getIndicator('Time to Collision').getMostSevereValue(1) * .1 < 2:
#                 number2 += 1
#             elif 2 <= inter.getIndicator('Time to Collision').getMostSevereValue(1) * .1 < 3:
#                 number3 += 1
#             elif 3 <= inter.getIndicator('Time to Collision').getMostSevereValue(1) * .1 < 4:
#                 number4 += 1
#             elif 4 <= inter.getIndicator('Time to Collision').getMostSevereValue(1) * .1 < 5:
#                 number5 += 1
#             elif 5 <= inter.getIndicator('Time to Collision').getMostSevereValue(1) * .1 < 6:
#                 number6 += 1
#             elif 6 <= inter.getIndicator('Time to Collision').getMostSevereValue(1) * .1 < 7:
#                 number7 += 1
#             elif 7 <= inter.getIndicator('Time to Collision').getMostSevereValue(1) * .1 < 8:
#                 number8 += 1
#             elif 8 <= inter.getIndicator('Time to Collision').getMostSevereValue(1) * .1 < 9:
#                 number9 += 1
#             elif 9 <= inter.getIndicator('Time to Collision').getMostSevereValue(1) * .1 < 10:
#                 number10 += 1
# trafficlights_numbers_side_TTC = [number1, number2, number3, number4, number5, number6, number7, number8, number9, number10]
#
# plt.plot([0,1,2,3,4,5,6,7,8,9,10], [trafficlights_numbers_side_TTC[0]] + trafficlights_numbers_side_TTC)
# plt.xlabel('Side Time\ to \ Collision\ (s)')
# plt.ylabel('$Number\ of\ observations$')
# plt.legend(['trafficlights crossing'])#, 'yield sign', 'status quo'])
# plt.savefig('pdf-zoom-trafficlights-side-TTC-raw.pdf')
# plt.close()
#
# trafficlights_numbers_side_TTC = [100*trafficlights_numbers_side_TTC[k]/len(trafficlights_minTTCs[2]) for k in range(0,10)]#[stop_numbers[0]/len(stop_PETs), stop_numbers[1]/len(stop_PETs), stop_numbers[2]/len(stop_PETs), stop_numbers[3]/len(stop_PETs), stop_numbers[4]/len(stop_PETs)]
#
# plt.plot([k for k in range(0,11)], [stop_numbers[0]] + stop_numbers)
# plt.xlabel('Side Time\ to \ Collision\ (s)')
# plt.ylabel('$Frequency\ (\%)$')
# plt.legend(['trafficlights crossing'])#, 'yield sign', 'status quo'])
# plt.savefig('pdf-zoom-trafficlights-side-TTC-normed.pdf')
# plt.close()
#
# ## pdf zoom PETs
# number1 = 0
# number2 = 0
# number3 = 0
# number4 = 0
# number5 = 0
# for inter in toolkit.flatten(trafficlights_analysis.interactions):
#
#     if inter.getIndicator('Post Encroachment Time') is not None:
#         if 0 <= inter.getIndicator('Post Encroachment Time').getMostSevereValue(1) * .1 < 1:
#             number1 += 1
#         elif 1 <= inter.getIndicator('Post Encroachment Time').getMostSevereValue(1) * .1 < 2:
#             number2 += 1
#         elif 2 <= inter.getIndicator('Post Encroachment Time').getMostSevereValue(1) * .1 < 3:
#             number3 += 1
#         elif 3 <= inter.getIndicator('Post Encroachment Time').getMostSevereValue(1) * .1 < 4:
#             number4 += 1
#         elif 4 <= inter.getIndicator('Post Encroachment Time').getMostSevereValue(1) * .1 < 5:
#             number5 += 1
#
# trafficlights_numbers_PETs = [number1, number2, number3, number4, number5]
#
# plt.plot([0,1,2,3,4,5], [trafficlights_numbers_PETs[0]] + trafficlights_numbers_PETs)
# plt.xlabel('Post Encroachment Time (s)')
# plt.ylabel('$Number\ of\ observations$')
# plt.legend(['trafficlights crossing'])#, 'yield sign', 'status quo'])
# plt.savefig('pdf-zoom-trafficlights-PETs-raw.pdf')
# plt.close()
#
# trafficlights_numbers_PETs = [100*trafficlights_numbers_PETs[k]/len(trafficlights_PETs[1]) for k in range(0,10)]#[stop_numbers[0]/len(stop_PETs), stop_numbers[1]/len(stop_PETs), stop_numbers[2]/len(stop_PETs), stop_numbers[3]/len(stop_PETs), stop_numbers[4]/len(stop_PETs)]
#
# plt.plot([k for k in range(0,11)], [trafficlights_numbers_PETs[0]] + trafficlights_numbers_PETs)
# plt.xlabel('Post Encroachment Time (s)')
# plt.ylabel('$Frequency\ (\%)$')
# plt.legend(['trafficlights crossing'])#, 'yield sign', 'status quo'])
# plt.savefig('pdf-zoom-trafficlights-PETs-normed.pdf')
# plt.close()
#
#
# ################################################ CDF ################################################
#
# ## pets
# trafficlights_PETs_x = np.sort(trafficlights_PETs)
#
# normedtrafficlights_PETs_y = 1. * np.arange(len(trafficlights_PETs)) / (len(trafficlights_PETs) - 1)
# rawPedesrians_PETs_y = 1. * np.arange(len(trafficlights_PETs))
#
# plt.plot(trafficlights_PETs, normedtrafficlights_PETs_y)
#
# plt.xlabel('Post Encroachment Time (s)')
# plt.ylabel('Frequency')
#
# plt.legend(['trafficlights crossing'])# sign', 'yield sign', 'status quo'])
# plt.title('Post Encroachment Time cumulative distribution functions')
# plt.savefig('cdfNormed-PETs-trafficlights.pdf')
# plt.close()
#
#
# plt.plot(trafficlights_PETs_x, rawPedesrians_PETs_y)
# plt.xlabel('Post Encroachment Time (s)')
# plt.ylabel('Number of observations')
#
# plt.legend(['trafficlights crossing'])# sign', 'yield sign', 'status quo'])
# plt.title('Side Time to Collision cumulative distribution functions')
# plt.savefig('cdfRaw-PETs-trafficlights.pdf')
# plt.close()
#
# ### side TTC
#
# trafficlights_TTCs_x = np.sort(trafficlights_minTTCs[2])
#
# normedtrafficlights_TTCs_y = 1. * np.arange(len(trafficlights_minTTCs[2])) / (len(trafficlights_minTTCs[2]) - 1)
# rawPedesrians_TTCs_y = 1. * np.arange(len(trafficlights_minTTCs[2]))
#
# plt.plot(trafficlights_TTCs_x, normedtrafficlights_TTCs_y)
#
# plt.xlabel('Side Time to Collision (s)')
# plt.ylabel('Frequency')
#
# plt.legend(['trafficlights crossing'])# sign', 'yield sign', 'status quo'])
# plt.title('Side Time to Collision cumulative distribution functions')
# plt.savefig('cdfNormed-TTCs-trafficlights.pdf')
# plt.close()
#
#
# plt.plot(trafficlights_TTCs_x, rawPedesrians_TTCs_y)
# plt.xlabel('Side Time to Collision (s)')
# plt.ylabel('Number of observations')
#
# plt.legend(['trafficlights crossing'])# sign', 'yield sign', 'status quo'])
# plt.title('Side Time to Collision cumulative distribution functions')
# plt.savefig('cdfRaw-TTCs-trafficlights.pdf')
# plt.close()
#
# toolkit.callWhenDone()