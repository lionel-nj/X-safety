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

# side_stop_minTTCs_x = np.sort(stop_minTTCs[2])
# side_yield_minTTCs_x = np.sort(yield_minTTCs[2])
side_sQuo_minTTCs_x = np.sort(sQuo_minTTCs[2])


# normedSide_stop_minTTCs_y = 1. * np.arange(len(stop_minTTCs[2])) / (len(stop_minTTCs[2]) - 1)
# rawSide_stop_minTTCs_y = 1. * np.arange(len(stop_minTTCs[2]))
#
# normedSide_yield_minTTCs_y = 1. * np.arange(len(yield_minTTCs[2])) / (len(yield_minTTCs[2]) - 1)
# rawSide_yield_minTTCs_y = 1. * np.arange(len(yield_minTTCs[2]))

normedSide_sQuo_minTTCs_y = 1. * np.arange(len(sQuo_minTTCs[2])) / (len(sQuo_minTTCs[2]) - 1)
rawSide_sQuo_minTTCs_y = 1. * np.arange(len(sQuo_minTTCs[2]))

# plt.plot(side_stop_minTTCs_x, normedSide_stop_minTTCs_y)
# plt.plot(side_yield_minTTCs_x, normedSide_yield_minTTCs_y)
plt.plot(side_sQuo_minTTCs_x, normedSide_sQuo_minTTCs_y)

plt.xlabel('Time to Collision (s)')
plt.ylabel('Frequency')
plt.legend(['status quo'])
# plt.legend(['stop sign', 'yield sign', 'status quo'])
plt.title('Side Time to Collision cumulative distribution functions')
plt.savefig('test-cdfNormed-minTTCs-side.pdf')
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

plt.xlabel('Post Encroachment Time (s)')
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

#### import collections

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

# side_stop_minTTCs_x = np.sort(stop_minTTCs[2])
# side_yield_minTTCs_x = np.sort(yield_minTTCs[2])
side_sQuo_minTTCs_x = np.sort(sQuo_minTTCs[2])


# normedSide_stop_minTTCs_y = 1. * np.arange(len(stop_minTTCs[2])) / (len(stop_minTTCs[2]) - 1)
# rawSide_stop_minTTCs_y = 1. * np.arange(len(stop_minTTCs[2]))
#
# normedSide_yield_minTTCs_y = 1. * np.arange(len(yield_minTTCs[2])) / (len(yield_minTTCs[2]) - 1)
# rawSide_yield_minTTCs_y = 1. * np.arange(len(yield_minTTCs[2]))

normedSide_sQuo_minTTCs_y = 1. * np.arange(len(sQuo_minTTCs[2])) / (len(sQuo_minTTCs[2]) - 1)
rawSide_sQuo_minTTCs_y = 1. * np.arange(len(sQuo_minTTCs[2]))

# plt.plot(side_stop_minTTCs_x, normedSide_stop_minTTCs_y)
# plt.plot(side_yield_minTTCs_x, normedSide_yield_minTTCs_y)
plt.plot(side_sQuo_minTTCs_x, normedSide_sQuo_minTTCs_y)

plt.xlabel('Time to Collision (s)')
plt.ylabel('Frequency')
plt.legend(['status quo'])
# plt.legend(['stop sign', 'yield sign', 'status quo'])
plt.title('Side Time to Collision cumulative distribution functions')
plt.savefig('test-cdfNormed-minTTCs-side.pdf')
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

plt.xlabel('Post Encroachment Time (s)')
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

############################################################
### pdf

## PETs


stop_histogram, stop_bin_centers = np.histogram(stop_PETs)
yield_histogram, yield_bin_centers = np.histogram(yield_PETs)#, bins=bins, normed=False)
sQuo_histogram, sQuo_bin_centers = np.histogram(sQuo_PETs)#, bins=bins, normed=False)

stop_bin_centers = 0.5*(stop_bin_centers[1:] + stop_bin_centers[:-1])
yield_bin_centers = 0.5*(yield_bin_centers[1:] + yield_bin_centers[:-1])
sQuo_bin_centers = 0.5*(sQuo_bin_centers[1:] + sQuo_bin_centers[:-1])

stop_histogram2 = np.array([k for k in range(len(stop_histogram))])
yield_histogram2 = np.array([k for k in range(len(yield_histogram))])
sQuo_histogram2 = np.array([k for k in range(len(sQuo_histogram))])

for k in range(0, len(stop_histogram)):
    stop_histogram2[k] = (100 * stop_histogram[k] / 15) / (len(stop_PETs) / 15)
for k in range(0, len(yield_histogram)):
    yield_histogram2[k] = (100 * yield_histogram[k] / 15) / (len(yield_PETs) / 15)
for k in range(0, len(sQuo_histogram)):
    sQuo_histogram2[k] = (100 * sQuo_histogram[k] / 15) / (len(sQuo_PETs) / 15)

plt.plot(stop_bin_centers, stop_histogram, label="stop sign")
plt.plot(yield_bin_centers, yield_histogram, label="yield sign")
plt.plot(sQuo_bin_centers, sQuo_histogram, label="status quo")

plt.xlabel('$Post\ Encroachment\ Time\ (s)$')
plt.ylabel('$Number\ of\ observations$')
plt.legend()
plt.savefig('pdf-PETs-raw.pdf')

plt.close()


plt.plot(stop_bin_centers, stop_histogram2, label="stop sign")
plt.plot(yield_bin_centers, yield_histogram2, label="yield sign")
plt.plot(sQuo_bin_centers, sQuo_histogram2, label="status quo")

plt.xlabel('$Post\ Encroachment\ Time\ (s)$')
plt.ylabel('$Frequency\ (\%)$')
plt.legend()
plt.savefig('pdf-PETs-normed.pdf')


## rear end TTCs


stop_histogram, stop_bin_centers = np.histogram(stop_minTTCs[1])
yield_histogram, yield_bin_centers = np.histogram(yield_minTTCs[1])#, bins=bins, normed=False)
sQuo_histogram, sQuo_bin_centers = np.histogram(sQuo_minTTCs[1])#, bins=bins, normed=False)

stop_bin_centers = 0.5*(stop_bin_centers[1:] + stop_bin_centers[:-1])
yield_bin_centers = 0.5*(yield_bin_centers[1:] + yield_bin_centers[:-1])
sQuo_bin_centers = 0.5*(sQuo_bin_centers[1:] + sQuo_bin_centers[:-1])

stop_histogram2 = np.array([k for k in range(len(stop_histogram))])
yield_histogram2 = np.array([k for k in range(len(yield_histogram))])
sQuo_histogram2 = np.array([k for k in range(len(sQuo_histogram))])

for k in range(0, len(stop_histogram)):
    stop_histogram2[k] = 100 * stop_histogram[k] / len(stop_minTTCs[1])
for k in range(0, len(yield_histogram)):
    yield_histogram2[k] = 100 * yield_histogram[k] / len(yield_minTTCs[1])
for k in range(0, len(sQuo_histogram)):
    sQuo_histogram2[k] = 100 * sQuo_histogram[k] / len(sQuo_minTTCs[1])

plt.plot(stop_bin_centers, stop_histogram, label="stop sign")
plt.plot(yield_bin_centers, yield_histogram, label="yield sign")
plt.plot(sQuo_bin_centers, sQuo_histogram, label="status quo")

plt.xlabel('$Rear-end\ Time\ to \ Collision\ (s)$')
plt.ylabel('$Number\ of\ observations$')
plt.legend()
plt.savefig('pdf-rearEnd-TTCs-raw.pdf')

plt.close()

plt.plot(stop_bin_centers, stop_histogram2, label="stop sign")
plt.plot(yield_bin_centers, yield_histogram2, label="yield sign")
plt.plot(sQuo_bin_centers, sQuo_histogram2, label="status quo")

plt.xlabel('$Rear-end\ Time\ to \ Collision\ (s)$')
plt.ylabel('$Frequency\ (\%)$')
plt.legend()
plt.savefig('pdf-rearEnd-TTCs-normed.pdf')


####

stop_histogram, stop_bin_centers = np.histogram(stop_minTTCs[2])
yield_histogram, yield_bin_centers = np.histogram(yield_minTTCs[2])#, bins=bins, normed=False)
sQuo_histogram, sQuo_bin_centers = np.histogram(sQuo_minTTCs[2])#, bins=bins, normed=False)

stop_bin_centers = 0.5*(stop_bin_centers[1:] + stop_bin_centers[:-1])
yield_bin_centers = 0.5*(yield_bin_centers[1:] + yield_bin_centers[:-1])
sQuo_bin_centers = 0.5*(sQuo_bin_centers[1:] + sQuo_bin_centers[:-1])

stop_histogram2 = np.array([k for k in range(len(stop_histogram))])
yield_histogram2 = np.array([k for k in range(len(yield_histogram))])
sQuo_histogram2 = np.array([k for k in range(len(sQuo_histogram))])

for k in range(0, len(stop_histogram)):
    stop_histogram2[k] = 100 * stop_histogram[k] / len(stop_minTTCs[2])
for k in range(0, len(yield_histogram)):
    yield_histogram2[k] = 100 * yield_histogram[k] / len(yield_minTTCs[2])
for k in range(0, len(sQuo_histogram)):
    sQuo_histogram2[k] = 100 * sQuo_histogram[k] / len(sQuo_minTTCs[2])

plt.plot(stop_bin_centers, stop_histogram, label="stop sign")
plt.plot(yield_bin_centers, yield_histogram, label="yield sign")
plt.plot(sQuo_bin_centers, sQuo_histogram, label="status quo")

plt.xlabel('Side\ Time\ to \ Collision\ (s)$')
plt.ylabel('$Number\ of\ observations$')
plt.legend()
plt.savefig('pdf-side-TTCs-raw.pdf')

plt.close()

plt.plot(stop_bin_centers, stop_histogram2, label="stop sign")
plt.plot(yield_bin_centers, yield_histogram2, label="yield sign")
plt.plot(sQuo_bin_centers, sQuo_histogram2, label="status quo")

plt.xlabel('$Side\ Time\ to \ Collision\ (s)$')
plt.ylabel('$Frequency\ (\%)$')
plt.legend()
plt.savefig('pdf-side-TTCs-normed.pdf')


### zoom PET

number1 = 0
number2 = 0
number3 = 0
number4 = 0
number5 = 0
for inter in toolkit.flatten(stop_analysis.interactions):

    if inter.getIndicator('Post Encroachment Time') is not None:
        if 0 <= inter.getIndicator('Post Encroachment Time').getMostSevereValue(1)*.1 < 1:
            number1 += 1
        elif 1<= inter.getIndicator('Post Encroachment Time').getMostSevereValue(1)*.1 < 2:
            number2 += 1
        elif 2 <= inter.getIndicator('Post Encroachment Time').getMostSevereValue(1)*.1 < 3:
            number3 += 1
        elif 3 <= inter.getIndicator('Post Encroachment Time').getMostSevereValue(1)*.1 < 4:
            number4 += 1
        elif 4 <= inter.getIndicator('Post Encroachment Time').getMostSevereValue(1)*.1 < 5:
            number5 += 1

numbers = [number1, number2, number3, number4, number5]
plt.plot([0,1,2,3,4,5], [stop_numbers[0]] + stop_numbers)
plt.plot([0,1,2,3,4,5], [yield_numbers[0]] + yield_numbers)
plt.plot([0,1,2,3,4,5], [sQuo_numbers[0]] + sQuo_numbers)
plt.xlabel('Post Encroachment Time (s)')
plt.ylabel('$Number\ of\ observations$')
plt.legend(['stop sign', 'yield sign', 'status quo'])
plt.savefig('pdf-zoom-PETs-raw.pdf')

number1 = 0
number2 = 0
number3 = 0
number4 = 0
number5 = 0
for inter in toolkit.flatten(yield_analysis.interactions):

    if inter.getIndicator('Post Encroachment Time') is not None:
        if 0 <= inter.getIndicator('Post Encroachment Time').getMostSevereValue(1) * .1 < 1:
            number1 += 1
        elif 1 <= inter.getIndicator('Post Encroachment Time').getMostSevereValue(1) * .1 < 2:
            number2 += 1
        elif 2 <= inter.getIndicator('Post Encroachment Time').getMostSevereValue(1) * .1 < 3:
            number3 += 1
        elif 3 <= inter.getIndicator('Post Encroachment Time').getMostSevereValue(1) * .1 < 4:
            number4 += 1
        elif 4 <= inter.getIndicator('Post Encroachment Time').getMostSevereValue(1) * .1 < 5:
            number5 += 1
numbers = [number1, number2, number3, number4, number5]

plt.plot([0,1,2,3,4,5], [numbers[0]] + numbers)

number1 = 0
number2 = 0
number3 = 0
number4 = 0
number5 = 0
for inter in toolkit.flatten(sQuo_analysis.interactions):

    if inter.getIndicator('Post Encroachment Time') is not None:
        if 0 <= inter.getIndicator('Post Encroachment Time').getMostSevereValue(1) * .1 < 1:
            number1 += 1
        elif 1 <= inter.getIndicator('Post Encroachment Time').getMostSevereValue(1) * .1 < 2:
            number2 += 1
        elif 2 <= inter.getIndicator('Post Encroachment Time').getMostSevereValue(1) * .1 < 3:
            number3 += 1
        elif 3 <= inter.getIndicator('Post Encroachment Time').getMostSevereValue(1) * .1 < 4:
            number4 += 1
        elif 4 <= inter.getIndicator('Post Encroachment Time').getMostSevereValue(1) * .1 < 5:
            number5 += 1
numbers = [number1, number2, number3, number4, number5]
plt.plot([0,1,2,3,4,5], [sQuo_numbers[0]] + sQuo_numbers)


stop_numbers = [stop_numbers[0]/len(stop_PETs), stop_numbers[1]/len(stop_PETs), stop_numbers[2]/len(stop_PETs), stop_numbers[3]/len(stop_PETs), stop_numbers[4]/len(stop_PETs)]
yield_numbers = [yield_numbers[0]/len(yield_PETs), yield_numbers[1]/len(yield_PETs), yield_numbers[2]/len(yield_PETs), yield_numbers[3]/len(yield_PETs), yield_numbers[4]/len(yield_PETs)]
sQuo_numbers = [sQuo_numbers[0]/len(sQuo_PETs), sQuo_numbers[1]/len(sQuo_PETs), sQuo_numbers[2]/len(sQuo_PETs), sQuo_numbers[3]/len(sQuo_PETs), sQuo_numbers[4]/len(sQuo_PETs)]

plt.plot([0,1,2,3,4,5], [stop_numbers[0]] + stop_numbers)
plt.plot([0,1,2,3,4,5], [yield_numbers[0]] + yield_numbers)
plt.plot([0,1,2,3,4,5], [sQuo_numbers[0]] + sQuo_numbers)
plt.xlabel('Post Encroachment Time (s)')
plt.ylabel('$Number\ of\ observations$')
plt.legend(['stop sign', 'yield sign', 'status quo'])
plt.savefig('pdf-zoom-PETs-normed.pdf')

### PDF Zoon TTC rear end/ side

number1 = 0
number2 = 0
number3 = 0
number4 = 0
number5 = 0
number6 = 0
number7 = 0
number8= 0
number9 = 0
number10 = 0

for inter in toolkit.flatten(stop_analysis.interactions):
    if inter.categoryNum == 2:
        if inter.getIndicator('Time to Collision') is not None:
            if 0 <= inter.getIndicator('Time to Collision').getMostSevereValue(1) * .1 < 1:
                number1 += 1
            elif 1 <= inter.getIndicator('Time to Collision').getMostSevereValue(1) * .1 < 2:
                number2 += 1
            elif 2 <= inter.getIndicator('Time to Collision').getMostSevereValue(1) * .1 < 3:
                number3 += 1
            elif 3 <= inter.getIndicator('Time to Collision').getMostSevereValue(1) * .1 < 4:
                number4 += 1
            elif 4 <= inter.getIndicator('Time to Collision').getMostSevereValue(1) * .1 < 5:
                number5 += 1
            elif 5 <= inter.getIndicator('Time to Collision').getMostSevereValue(1) * .1 < 6:
                number6 += 1
            elif 6 <= inter.getIndicator('Time to Collision').getMostSevereValue(1) * .1 < 7:
                number7 += 1
            elif 7 <= inter.getIndicator('Time to Collision').getMostSevereValue(1) * .1 < 8:
                number8 += 1
            elif 8 <= inter.getIndicator('Time to Collision').getMostSevereValue(1) * .1 < 9:
                number9 += 1
            elif 9 <= inter.getIndicator('Time to Collision').getMostSevereValue(1) * .1 < 10:
                number10 += 1

stop_numbers = [number1, number2, number3, number4, number5, number6, number7, number8, number9, number10]
# plt.plot([k for k in range(0, 11)], [stop_numbers[0]] + stop_numbers)

number1 = 0
number2 = 0
number3 = 0
number4 = 0
number5 = 0
number6 = 0
number7 = 0
number8 = 0
number9 = 0
number10 = 0

for inter in toolkit.flatten(yield_analysis.interactions):
    if inter.categoryNum == 2:
        if inter.getIndicator('Time to Collision') is not None:
            if 0 <= inter.getIndicator('Time to Collision').getMostSevereValue(1) * .1 < 1:
                number1 += 1
            elif 1 <= inter.getIndicator('Time to Collision').getMostSevereValue(1) * .1 < 2:
                number2 += 1
            elif 2 <= inter.getIndicator('Time to Collision').getMostSevereValue(1) * .1 < 3:
                number3 += 1
            elif 3 <= inter.getIndicator('Time to Collision').getMostSevereValue(1) * .1 < 4:
                number4 += 1
            elif 4 <= inter.getIndicator('Time to Collision').getMostSevereValue(1) * .1 < 5:
                number5 += 1
            elif 5 <= inter.getIndicator('Time to Collision').getMostSevereValue(1) * .1 < 6:
                number6 += 1
            elif 6 <= inter.getIndicator('Time to Collision').getMostSevereValue(1) * .1 < 7:
                number7 += 1
            elif 7 <= inter.getIndicator('Time to Collision').getMostSevereValue(1) * .1 < 8:
                number8 += 1
            elif 8 <= inter.getIndicator('Time to Collision').getMostSevereValue(1) * .1 < 9:
                number9 += 1
            elif 9 <= inter.getIndicator('Time to Collision').getMostSevereValue(1) * .1 < 10:
                number10 += 1

yield_numbers = [number1, number2, number3, number4, number5, number6, number7, number8, number9, number10]
# plt.plot([k for k in range(0, 11)], [yield_numbers[0]] + yield_numbers)

number1 = 0
number2 = 0
number3 = 0
number4 = 0
number5 = 0
number6 = 0
number7 = 0
number8 = 0
number9 = 0
number10 = 0

for inter in toolkit.flatten(sQuo_analysis.interactions):
    if inter.categoryNum == 2:
        if inter.getIndicator('Time to Collision') is not None:
            if 0 <= inter.getIndicator('Time to Collision').getMostSevereValue(1) * .1 < 1:
                number1 += 1
            elif 1 <= inter.getIndicator('Time to Collision').getMostSevereValue(1) * .1 < 2:
                number2 += 1
            elif 2 <= inter.getIndicator('Time to Collision').getMostSevereValue(1) * .1 < 3:
                number3 += 1
            elif 3 <= inter.getIndicator('Time to Collision').getMostSevereValue(1) * .1 < 4:
                number4 += 1
            elif 4 <= inter.getIndicator('Time to Collision').getMostSevereValue(1) * .1 < 5:
                number5 += 1
            elif 5 <= inter.getIndicator('Time to Collision').getMostSevereValue(1) * .1 < 6:
                number6 += 1
            elif 6 <= inter.getIndicator('Time to Collision').getMostSevereValue(1) * .1 < 7:
                number7 += 1
            elif 7 <= inter.getIndicator('Time to Collision').getMostSevereValue(1) * .1 < 8:
                number8 += 1
            elif 8 <= inter.getIndicator('Time to Collision').getMostSevereValue(1) * .1 < 9:
                number9 += 1
            elif 9 <= inter.getIndicator('Time to Collision').getMostSevereValue(1) * .1 < 10:
                number10 += 1
sQuo_numbers = [number1, number2, number3, number4, number5, number6, number7, number8, number9, number10]
# plt.plot([k for k in range(0, 11)], [sQuo_numbers[0]] + sQuo_numbers)

stop_numbers = [100*stop_numbers[k]/len(stop_minTTCs[2]) for k in range(len(stop_numbers))]
yield_numbers = [100*yield_numbers[k]/len(yield_minTTCs[2]) for k in range(len(yield_numbers))]
sQuo_numbers = [100*sQuo_numbers[k]/len(sQuo_minTTCs[2]) for k in range(len(sQuo_numbers))]

plt.plot([k for k in range(0, 11)], [stop_numbers[0]] + stop_numbers)
plt.plot([k for k in range(0, 11)], [yield_numbers[0]] + yield_numbers)
plt.plot([k for k in range(0, 11)], [sQuo_numbers[0]] + sQuo_numbers)

plt.xlabel('$Side\ Time\ to\ Collision\ (s)$')
# plt.ylabel('Number\ of\ observations')
plt.ylabel('$Frequency\ (\%)$')
plt.legend(['stop sign', 'yield sign','status quo'])
plt.savefig('pdf-zoom-TTC-side-normed.pdf')