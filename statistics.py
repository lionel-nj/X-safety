import collections

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

values = ['rearEndTTCsMean', 'rearEndTTCsSTD', 'rearEndTTCsCount', 'readEndNinter10', 'rearEndNinter20', 'rearEndNinter50', 'sideTTCsMean', 'sideTTCsSTD', 'sideTTCsCount', 'sideNinter10', 'sideNinter20', 'sideNinter50', 'PETsMean', 'PETsSTD', 'PETsCount']

### code for stops sign ###

stopStatistics = [np.mean(stop_minTTCs[1]), np.std(stop_minTTCs[1]), len(stop_minTTCs[1]), stop_nInter10[1], stop_nInter20[1], stop_nInter50[1], np.mean(stop_minTTCs[2]), np.std(stop_minTTCs[2]), len(stop_minTTCs[2]), stop_nInter10[2], stop_nInter20[2], stop_nInter50[2], np.mean(stop_PETs), np.std(stop_PETs), len(stop_PETs)]

### code for yield sign ###

yieldStatistics = [np.mean(yield_minTTCs[1]), np.std(yield_minTTCs[1]), len(yield_minTTCs[1]), yield_nInter10[1], yield_nInter20[1], yield_nInter50[1], np.mean(yield_minTTCs[2]), np.std(yield_minTTCs[2]), len(yield_minTTCs[2]), yield_nInter10[2], yield_nInter20[2], yield_nInter50[2], np.mean(yield_PETs), np.std(yield_PETs), len(yield_PETs)]

## code for status quo ###

sQuoStatistics = [np.mean(sQuo_minTTCs[1]), np.std(sQuo_minTTCs[1]), len(sQuo_minTTCs[1]), sQuo_nInter10[1], sQuo_nInter20[1], sQuo_nInter50[1], np.mean(sQuo_minTTCs[2]), np.std(sQuo_minTTCs[2]), len(sQuo_minTTCs[2]), sQuo_nInter10[2], sQuo_nInter20[2], sQuo_nInter50[2], np.mean(sQuo_PETs), np.std(sQuo_PETs), len(sQuo_PETs)]

statistics = {'stop' : stopStatistics,
              'yield' : yieldStatistics,
              'squo' : sQuoStatistics}

### KS test for comparison between rear end TTC, side TTC for each facility ###

ksTestIntra = [stats.ks_2samp(stop_minTTCs[1], stop_minTTCs[2]), stats.ks_2samp(yield_minTTCs[1], yield_minTTCs[2]), stats.ks_2samp(sQuo_minTTCs[1], sQuo_minTTCs[2])]

## KS test to determine if distribution follow a normal or exponential distribution ###

ksTestIntraStop = {'norm-rearEndTTCs' : stats.kstest(stop_minTTCs[1], 'norm'),
                   'expon-rearEndTTCs' : stats.kstest(stop_minTTCs[1], 'expon'),
                   'norm-sideTTCs': stats.kstest(stop_minTTCs[2], 'norm'),
                   'expon-sideTTCs': stats.kstest(stop_minTTCs[2], 'expon'),
                    'norm-PETs': stats.kstest(stop_PETs, 'norm'),
                   'expon-PETs': stats.kstest(stop_PETs, 'expon')}

ksTestIntraYield = {'norm-rearEndTTCs' : stats.kstest(yield_minTTCs[1], 'norm'),
                   'expon-rearEndTTCs' : stats.kstest(yield_minTTCs[1], 'expon'),
                   'norm-sideTTCs': stats.kstest(yield_minTTCs[2], 'norm'),
                   'expon-sideTTCs': stats.kstest(yield_minTTCs[2], 'expon'),
                    'norm-PETs': stats.kstest(yield_PETs, 'norm'),
                   'expon-PETs': stats.kstest(yield_PETs, 'expon')}

ksTestIntraSquo = {'norm-rearEndTTCs' : stats.kstest(sQuo_minTTCs[1], 'norm'),
                   'expon-rearEndTTCs' : stats.kstest(sQuo_minTTCs[1], 'expon'),
                   'norm-sideTTCs': stats.kstest(sQuo_minTTCs[2], 'norm'),
                   'expon-sideTTCs': stats.kstest(sQuo_minTTCs[2], 'expon'),
                    'norm-PETs': stats.kstest(sQuo_PETs, 'norm'),
                   'expon-PETs': stats.kstest(sQuo_PETs, 'expon')}

## KS test to determine whether distributions are the same or not ###

ksTestInterStopYield = [stats.ks_2samp(stop_minTTCs[1], yield_minTTCs[1]), stats.ks_2samp(stop_minTTCs[2], yield_minTTCs[2]), stats.ks_2samp(stop_PETs, yield_PETs)]

ksTestInterStopSquo = [stats.ks_2samp(stop_minTTCs[1], sQuo_minTTCs[1]), stats.ks_2samp(stop_minTTCs[2], sQuo_minTTCs[2]), stats.ks_2samp(stop_PETs, sQuo_PETs)]

ksTestInterYieldSquo = [stats.ks_2samp(yield_minTTCs[1], sQuo_minTTCs[1]), stats.ks_2samp(yield_minTTCs[2], sQuo_minTTCs[2]), stats.ks_2samp(yield_PETs, sQuo_PETs)]

f = open("statistics.txt","w+")
f.write(str(values) + '\n' + '\n' + statistics + '\n' + '\n' + 'ks intra stop-yield-squo-TTC1-TTC2' + str(ksTestIntra) + 'KS for each facility to compare with norm and expon distributions' + str(ksTestIntraStop) + '\n' + '\n' + str(ksTestIntraYield) + '\n' + '\n' + str(ksTestIntraSquo) + '\n' + '\n' + 'ks to compare distribution betwen them: stop/yield - stop/squo - yield/squo' + '\n' + '\n' + str(ksTestInterStopYield) + str(ksTestInterStopSquo) + str(ksTestInterYieldSquo))
f.close()

### histograms ###

# rear end TTCs
rearEnd_stop_minTTCs_x = np.sort(stop_minTTCs[1])
rearEnd_yield_minTTCs_x = np.sort(yield_minTTCs[1])
rearEnd_sQuo_minTTCs_x = np.sort(sQuo_minTTCs[1])

## side_stop_minTTCs_x = np.sort(stop_minTTCs[2])
## side_yield_minTTCs_x = np.sort(yield_minTTCs[2])
## side_sQuo_minTTCs_x = np.sort(sQuo_minTTCs[2])


normedRearEnd_stop_minTTCs_y = 1. * np.arange(len(stop_minTTCs[1])) / (len(stop_minTTCs[1]) - 1)
rawRearEnd_stop_minTTCs_y = 1. * np.arange(len(stop_minTTCs[1]))

normedRearEnd_yield_minTTCs_y = 1. * np.arange(len(yield_minTTCs[1])) / (len(yield_minTTCs[1]) - 1)
rawRearEnd_yield_minTTCs_y = 1. * np.arange(len(yield_minTTCs[1]))

normedRearEnd_sQuo_minTTCs_y = 1. * np.arange(len(sQuo_minTTCs[1])) / (len(sQuo_minTTCs[1]) - 1)
rawRearEnd_sQuo_minTTCs_y = 1. * np.arange(len(sQuo_minTTCs[1]))

plt.plot(rearEnd_stop_minTTCs_x, normedRearEnd_stop_minTTCs_y)
plt.plot(rearEnd_yield_minTTCs_x, normedRearEnd_yield_minTTCs_y)
plt.plot(rearEnd_sQuo_minTTCs_x, normedRearEnd_sQuo_minTTCs_y)

plt.xlabel('Time to Collision (s)')
plt.ylabel('Frequency')

plt.legend(['stop sign', 'yield sign', 'status quo'])
plt.title('Rear end Time to Collision cumulative distribution functions')
plt.savefig('cdfNormed-minTTCs-rearEnd.pdf')
plt.close()

plt.plot(rearEnd_stop_minTTCs_x, rawRearEnd_stop_minTTCs_y)
plt.plot(rearEnd_yield_minTTCs_x, rawRearEnd_yield_minTTCs_y)
plt.plot(rearEnd_sQuo_minTTCs_x, rawRearEnd_sQuo_minTTCs_y)

plt.xlabel('Time to Collision (s)')
plt.ylabel('Number of observations')

plt.legend(['stop sign', 'yield sign', 'status quo'])
plt.title('Rear end Time to Collision cumulative distribution functions')
plt.savefig('cdfRaw-minTTCs-rearEnd.pdf')
plt.close()
###############################################################

# side TTCs

side_stop_minTTCs_x = np.sort(stop_minTTCs[2])
side_yield_minTTCs_x = np.sort(yield_minTTCs[2])
side_sQuo_minTTCs_x = np.sort(sQuo_minTTCs[2])


normedSide_stop_minTTCs_y = 1. * np.arange(len(stop_minTTCs[2])) / (len(stop_minTTCs[2]) - 1)
rawSide_stop_minTTCs_y = 1. * np.arange(len(stop_minTTCs[2]))

normedSide_yield_minTTCs_y = 1. * np.arange(len(yield_minTTCs[2])) / (len(yield_minTTCs[2]) - 1)
rawSide_yield_minTTCs_y = 1. * np.arange(len(yield_minTTCs[2]))

normedSide_sQuo_minTTCs_y = 1. * np.arange(len(sQuo_minTTCs[2])) / (len(sQuo_minTTCs[2]) - 1)
rawSide_sQuo_minTTCs_y = 1. * np.arange(len(sQuo_minTTCs[2]))

plt.plot(side_stop_minTTCs_x, normedSide_stop_minTTCs_y)
plt.plot(side_yield_minTTCs_x, normedSide_yield_minTTCs_y)
plt.plot(side_sQuo_minTTCs_x, normedSide_sQuo_minTTCs_y)

plt.xlabel('Time to Collision (s)')
plt.ylabel('Frequency')

plt.legend(['stop sign', 'yield sign', 'status quo'])
plt.title('Side Time to Collision cumulative distribution functions')
plt.savefig('cdfNormed-minTTCs-side.pdf')
plt.close()

plt.plot(side_stop_minTTCs_x, rawSide_stop_minTTCs_y)
plt.plot(side_yield_minTTCs_x, rawSide_yield_minTTCs_y)
plt.plot(side_sQuo_minTTCs_x, rawSide_sQuo_minTTCs_y)

plt.xlabel('Time to Collision (s)')
plt.ylabel('Number of observations')

plt.legend(['stop sign', 'yield sign', 'status quo'])
plt.title('Rear end Time to Collision cumulative distribution functions')
plt.savefig('cdfRaw-minTTCs-side.pdf')
plt.close()

############################################################
# PETs

stop_PETs_x = np.sort(stop_PETs)
yield_PETs_x = np.sort(yield_PETs)
sQuo_PETs_x = np.sort(sQuo_PETs)

normedStop_PETs_y = 1. * np.arange(len(stop_PETs)) / (len(stop_PETs) - 1)
rawStop_PETs_y = 1. * np.arange(len(stop_PETs))

normedYield_PETs_y = 1. * np.arange(len(yield_PETs)) / (len(yield_PETs) - 1)
rawYield_PETs_y = 1. * np.arange(len(yield_PETs))

normedSquo_PETs_y = 1. * np.arange(len(sQuo_PETs)) / (len(sQuo_PETs) - 1)
rawSquo_PETs_y = 1. * np.arange(len(sQuo_PETs))

plt.plot(stop_PETs_x, normedStop_PETs_y)
plt.plot(yield_PETs_x, normedYield_PETs_y)
plt.plot(sQuo_PETs_x, normedSquo_PETs_y)

plt.xlabel('Time to Collision (s)')
plt.ylabel('Frequency')

plt.legend(['stop sign', 'yield sign', 'status quo'])
plt.title('Post Encroachment Time cumulative distribution functions')
plt.savefig('cdfNormed-PETs.pdf')
plt.close()

plt.plot(stop_PETs_x, rawStop_PETs_y)
plt.plot(yield_PETs_x, rawYield_PETs_y)
plt.plot(sQuo_PETs_x, rawSquo_PETs_y)

plt.xlabel('Time to Collision (s)')
plt.ylabel('Number of observations')

plt.legend(['stop sign', 'yield sign', 'status quo'])
plt.title('Post Encroachment Time cumulative distribution functions')
plt.savefig('cdfRaw-PETs.pdf')
plt.close()


# min distance distributions

yield_minDistancesRearEnd = []
yield_minDistancesSide = []

stop_minDistancesRearEnd = []
stop_minDistancesSide = []

sQuo_minDistancesRearEnd = []
sQuo_minDistancesSide = []

for seed in seeds:
    yield_minDistancesRearEnd.extend(yield_minDistances[1][seed])
    yield_minDistancesSide.extend(yield_minDistances[2][seed])

    stop_minDistancesRearEnd.extend(stop_minDistances[1][seed])
    stop_minDistancesSide.extend(stop_minDistances[2][seed])

    sQuo_minDistancesRearEnd.extend(sQuo_minDistances[1][seed])
    sQuo_minDistancesSide.extend(sQuo_minDistances[2][seed])


yield_minDistancesRearEndCounter = collections.Counter(yield_minDistancesRearEnd)
yield_minDistancesSideCounter = collections.Counter(yield_minDistancesSide)

stop_minDistancesRearEndCounter = collections.Counter(stop_minDistancesRearEnd)
stop_minDistancesSideCounter = collections.Counter(stop_minDistancesSide)

sQuo_minDistancesRearEndCounter = collections.Counter(sQuo_minDistancesRearEnd)
sQuo_minDistancesSideCounter = collections.Counter(sQuo_minDistancesSide)

plt.plot(stop_minDistancesRearEndCounter.keys(), stop_minDistancesRearEndCounter.values())
plt.plot(yield_minDistancesRearEndCounter.keys(), yield_minDistancesRearEndCounter.values())
plt.plot(sQuo_minDistancesRearEndCounter.keys(), sQuo_minDistancesRearEndCounter.values())
plt.legend(['stop sign', 'yield sign', 'status quo'])
plt.title('Rear-end minimum distance cumulative distribution functions')
plt.xlabel('Distances (m)')
plt.ylabel('Frequency')
plt.savefig('cdf-rearEndminDistances.pdf')
plt.close()

plt.plot(stop_minDistancesSideCounter.keys(), stop_minDistancesSideCounter.values())
plt.plot(yield_minDistancesSideCounter.keys(), yield_minDistancesSideCounter.values())
plt.plot(sQuo_minDistancesSideCounter.keys(), sQuo_minDistancesSideCounter.values())
plt.legend(['stop sign', 'yield sign', 'status quo'])
plt.title('Rear-end minimum distance cumulative distribution functions')
plt.xlabel('Distances (m)')
plt.ylabel('Frequency')
plt.savefig('cdf-sideMinDistances.pdf')
plt.close()

