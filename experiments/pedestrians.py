#! /usr/bin/env python3
import numpy as np

import events
import network
import simulation
import toolkit

pedestrians_world = network.World.load('pedestrians.yml')
pedestrians_sim = simulation.Simulation.load('pedestrians-config.yml')
# pedestrians_analysis = an.Analysis(idx=0, world=pedestrians_world, seed=pedestrians_sim.seed)
# pedestrians_analysis.interactions = []

seeds = [pedestrians_sim.seed+i*pedestrians_sim.increment for i in range(pedestrians_sim.rep)]
pedestrians_minTTCs = {1: [], 2: []}
pedestrians_minDistances = {1: {}, 2: {}}
for categoryNum in pedestrians_minDistances:
    for seed in seeds:
        pedestrians_minDistances[categoryNum][seed] = []#

pedestrians_PETs = []
pedestrians_interactions = []

pedestrians_rearEndnInter10 = []
pedestrians_rearEndnInter20 = []
pedestrians_rearEndnInter50 = []

pedestrians_sidenInter10 = []
pedestrians_sidenInter20 = []
pedestrians_sidenInter50 = []


#analysis.saveParametersToTable(sim.dbName)
for seed in seeds:
    print(str(seeds.index(seed)+1) + 'out of {}'.format(len(seeds)))
    pedestrians_world = network.World.load('pedestrians.yml')
    pedestrians_sim.seed = seed
    pedestrians_sim.run(pedestrians_world)
    # pedestrians_analysis.seed = seed
    # pedestrians_analysis.interactions.append(pedestrians_world.completedInteractions)
    for inter in pedestrians_world.completedInteractions:
        if inter.categoryNum is not None:
            pedestrians_distance = inter.getIndicator(events.Interaction.indicatorNames[2])
            if pedestrians_distance is not None:

                if inter.categoryNum == 1:
                    if inter.roadUser1.getInitialAlignment().idx == 0:
                        pedestrians_minDistances[inter.categoryNum][seed].append(pedestrians_distance.getMostSevereValue(1))
                else:
                    pedestrians_minDistances[inter.categoryNum][seed].append(pedestrians_distance.getMostSevereValue(1))

                pedestrians_minDistances[inter.categoryNum][seed].append(pedestrians_distance.getMostSevereValue(1))
            pedestrians_ttc = inter.getIndicator(events.Interaction.indicatorNames[7])
            if pedestrians_ttc is not None:
                pedestrians_minTTC = pedestrians_ttc.getMostSevereValue(1)*pedestrians_sim.timeStep  # seconds
                if pedestrians_minTTC < 0:
                    print(inter.num, inter.categoryNum, pedestrians_ttc.values)
                if pedestrians_minTTC < 20:

                    if inter.categoryNum == 1:
                        if inter.roadUser1.getInitialAlignment().idx == 0:
                            pedestrians_minTTCs[inter.categoryNum].append(pedestrians_minTTC)
                    else:
                        pedestrians_minTTCs[inter.categoryNum].append(pedestrians_minTTC)

                    # pedestrians_minTTCs[inter.categoryNum].append(pedestrians_minTTC)
                values = pedestrians_ttc.getValues(False)
                if len(values) > 5:
                    pedestrians_interactions.append(inter)
            if inter.getIndicator(events.Interaction.indicatorNames[10]) is not None:
                pedestrians_PETs.append(inter.getIndicator(events.Interaction.indicatorNames[10]).getMostSevereValue(1))

    pedestrians_rearEndnInter10.append((np.array(pedestrians_minDistances[1][seed]) <= 10).sum())
    pedestrians_rearEndnInter20.append((np.array(pedestrians_minDistances[1][seed]) <= 20).sum())
    pedestrians_rearEndnInter50.append((np.array(pedestrians_minDistances[1][seed]) <= 50).sum())

    pedestrians_sidenInter10.append((np.array(pedestrians_minDistances[2][seed]) <= 10).sum())
    pedestrians_sidenInter20.append((np.array(pedestrians_minDistances[2][seed]) <= 20).sum())
    pedestrians_sidenInter50.append((np.array(pedestrians_minDistances[2][seed]) <= 50).sum())

pedestrians_nInter10 = {1: np.mean(pedestrians_rearEndnInter10), 2: np.mean(pedestrians_sidenInter10)}
pedestrians_nInter20 = {1: np.mean(pedestrians_rearEndnInter20), 2: np.mean(pedestrians_sidenInter20)}
pedestrians_nInter50 = {1: np.mean(pedestrians_rearEndnInter50), 2: np.mean(pedestrians_sidenInter50)}

resultsPedestriansStop = {'minTTCS':pedestrians_minTTC,
                          'minDistances':pedestrians_minDistances,
                          'PETs':pedestrians_PETs,
                          'nInter10': pedestrians_nInter10,
                          'nInter20': pedestrians_nInter20,
                          'nInter50': pedestrians_nInter50,
                          'rearEndnInter10': pedestrians_rearEndnInter10,
                          'rearEndnInter20': pedestrians_rearEndnInter20,
                          'rearEndnInter50': pedestrians_rearEndnInter50,
                          'pedestrians_sidenInter10': pedestrians_sidenInter10,
                          'pedestrians_sidenInter20': pedestrians_sidenInter20,
                          'pedestrians_sidenInter50':pedestrians_sidenInter50}

toolkit.saveYaml('pedestrians-results.yml', resultsPedestriansStop)

toolkit.saveYaml('pedestrians-minTTC.yml', pedestrians_minTTCs)
toolkit.saveYaml('pedestrians-minDistances.yml', pedestrians_minDistances)
toolkit.saveYaml('pedestrians-PETs.yml', pedestrians_PETs)




# #### PDF COMPLETES
#
# ### TTC side
#
# pedestrians_histogram, pedestrians_bin_centers = np.histogram(pedestrians_minTTCs[2])#, bins=bins, normed=False)
#
# pedestrians_bin_centers = 0.5*(pedestrians_bin_centers[1:] + pedestrians_bin_centers[:-1])
#
# pedestrians_histogram2 = np.array([k for k in range(len(pedestrians_histogram))])
#
# for k in range(0, len(pedestrians_histogram)):
#     pedestrians_histogram2[k] = 100 * pedestrians_histogram[k] / len(pedestrians_minTTCs[2])
#
# plt.plot(pedestrians_bin_centers, pedestrians_histogram, label="pedestrians crossing")
#
# plt.xlabel('Side\ Time\ to \ Collision\ (s)$')
# plt.ylabel('$Number\ of\ observations$')
# plt.legend()
# plt.savefig('pdf-side-pedestrians-TTCs-raw.pdf')
# plt.close()
#
# plt.plot(pedestrians_bin_centers, pedestrians_histogram2, label="pedestrians crossing")
# plt.xlabel('$Side\ Time\ to \ Collision\ (s)$')
# plt.ylabel('$Frequency\ (\%)$')
# plt.legend()
# plt.savefig('pdf-side-pedestrians-TTCs-normed.pdf')
# plt.close()
#
# ### PET
#
# pedestrians_histogram, pedestrians_bin_centers = np.histogram(pedestrians_PETs)#, bins=bins, normed=False)
#
# pedestrians_bin_centers = 0.5*(pedestrians_bin_centers[1:] + pedestrians_bin_centers[:-1])
#
# pedestrians_histogram2 = np.array([k for k in range(len(pedestrians_histogram))])
#
# for k in range(0, len(pedestrians_histogram)):
#     pedestrians_histogram2[k] = 100 * pedestrians_histogram[k] / len(pedestrians_PETs)
#
# plt.plot(pedestrians_bin_centers, pedestrians_histogram, label="pedestrians crossing")
#
# plt.xlabel('Post\ Encroachment\ Time\ (s)$')
# plt.ylabel('$Number\ of\ observations$')
# plt.legend()
# plt.savefig('pdf-side-pedestrians-PETs-raw.pdf')
# plt.close()
#
# plt.plot(pedestrians_bin_centers, pedestrians_histogram2, label="pedestrians crossing")
# plt.xlabel('Post\ Encroachment\ Time\ (s)$')
# plt.ylabel('$Frequency\ (\%)$')
# plt.legend()
# plt.savefig('pdf-side-pedestrians-PETs-normed.pdf')
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
# for inter in toolkit.flatten(pedestrians_analysis.interactions):
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
# pedestrians_numbers_side_TTC = [number1, number2, number3, number4, number5, number6, number7, number8, number9, number10]
#
# plt.plot([0,1,2,3,4,5,6,7,8,9,10], [pedestrians_numbers_side_TTC[0]] + pedestrians_numbers_side_TTC)
# plt.xlabel('Side Time\ to \ Collision\ (s)')
# plt.ylabel('$Number\ of\ observations$')
# plt.legend(['pedestrians crossing'])#, 'yield sign', 'status quo'])
# plt.savefig('pdf-zoom-pedestrians-side-TTC-raw.pdf')
# plt.close()
#
# pedestrians_numbers_side_TTC = [100*pedestrians_numbers_side_TTC[k]/len(pedestrians_minTTCs[2]) for k in range(0,10)]#[stop_numbers[0]/len(stop_PETs), stop_numbers[1]/len(stop_PETs), stop_numbers[2]/len(stop_PETs), stop_numbers[3]/len(stop_PETs), stop_numbers[4]/len(stop_PETs)]
#
# plt.plot([k for k in range(0,11)], [stop_numbers[0]] + stop_numbers)
# plt.xlabel('Side Time\ to \ Collision\ (s)')
# plt.ylabel('$Frequency\ (\%)$')
# plt.legend(['pedestrians crossing'])#, 'yield sign', 'status quo'])
# plt.savefig('pdf-zoom-pedestrians-side-TTC-normed.pdf')
# plt.close()
#
# ## pdf zoom PETs
# number1 = 0
# number2 = 0
# number3 = 0
# number4 = 0
# number5 = 0
# for inter in toolkit.flatten(pedestrians_analysis.interactions):
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
# pedestrians_numbers_PETs = [number1, number2, number3, number4, number5]
#
# plt.plot([0,1,2,3,4,5], [pedestrians_numbers_PETs[0]] + pedestrians_numbers_PETs)
# plt.xlabel('Post Encroachment Time (s)')
# plt.ylabel('$Number\ of\ observations$')
# plt.legend(['pedestrians crossing'])#, 'yield sign', 'status quo'])
# plt.savefig('pdf-zoom-pedestrians-PETs-raw.pdf')
# plt.close()
#
# pedestrians_numbers_PETs = [100*pedestrians_numbers_PETs[k]/len(pedestrians_PETs[1]) for k in range(0,10)]#[stop_numbers[0]/len(stop_PETs), stop_numbers[1]/len(stop_PETs), stop_numbers[2]/len(stop_PETs), stop_numbers[3]/len(stop_PETs), stop_numbers[4]/len(stop_PETs)]
#
# plt.plot([k for k in range(0,11)], [pedestrians_numbers_PETs[0]] + pedestrians_numbers_PETs)
# plt.xlabel('Post Encroachment Time (s)')
# plt.ylabel('$Frequency\ (\%)$')
# plt.legend(['pedestrians crossing'])#, 'yield sign', 'status quo'])
# plt.savefig('pdf-zoom-pedestrians-PETs-normed.pdf')
# plt.close()
#
#
# ################################################ CDF ################################################
#
# ## pets
# pedestrians_PETs_x = np.sort(pedestrians_PETs)
#
# normedPedestrians_PETs_y = 1. * np.arange(len(pedestrians_PETs)) / (len(pedestrians_PETs) - 1)
# rawPedesrians_PETs_y = 1. * np.arange(len(pedestrians_PETs))
#
# plt.plot(pedestrians_PETs, normedPedestrians_PETs_y)
#
# plt.xlabel('Post Encroachment Time (s)')
# plt.ylabel('Frequency')
#
# plt.legend(['pedestrians crossing'])# sign', 'yield sign', 'status quo'])
# plt.title('Post Encroachment Time cumulative distribution functions')
# plt.savefig('cdfNormed-PETs-pedestrians.pdf')
# plt.close()
#
#
# plt.plot(pedestrians_PETs_x, rawPedesrians_PETs_y)
# plt.xlabel('Post Encroachment Time (s)')
# plt.ylabel('Number of observations')
#
# plt.legend(['pedestrians crossing'])# sign', 'yield sign', 'status quo'])
# plt.title('Side Time to Collision cumulative distribution functions')
# plt.savefig('cdfRaw-PETs-pedestrians.pdf')
# plt.close()
#
# ### side TTC
#
# pedestrians_TTCs_x = np.sort(pedestrians_minTTCs[2])
#
# normedPedestrians_TTCs_y = 1. * np.arange(len(pedestrians_minTTCs[2])) / (len(pedestrians_minTTCs[2]) - 1)
# rawPedesrians_TTCs_y = 1. * np.arange(len(pedestrians_minTTCs[2]))
#
# plt.plot(pedestrians_TTCs_x, normedPedestrians_TTCs_y)
#
# plt.xlabel('Side Time to Collision (s)')
# plt.ylabel('Frequency')
#
# plt.legend(['pedestrians crossing'])# sign', 'yield sign', 'status quo'])
# plt.title('Side Time to Collision cumulative distribution functions')
# plt.savefig('cdfNormed-TTCs-pedestrians.pdf')
# plt.close()
#
#
# plt.plot(pedestrians_TTCs_x, rawPedesrians_TTCs_y)
# plt.xlabel('Side Time to Collision (s)')
# plt.ylabel('Number of observations')
#
# plt.legend(['pedestrians crossing'])# sign', 'yield sign', 'status quo'])
# plt.title('Side Time to Collision cumulative distribution functions')
# plt.savefig('cdfRaw-TTCs-pedestrians.pdf')
# plt.close()
#
# toolkit.callWhenDone()