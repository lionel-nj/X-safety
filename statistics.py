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
plt.hist(stop_minTTCs[1], density=True, histtype='step', cumulative=True, label='stop sign', fill=False)
plt.hist(yield_minTTCs[1], density=True, histtype='step', cumulative=True, label='yield sign', fill=False)
plt.hist(sQuo_minTTCs[1], density=True, histtype='step', cumulative=True, label='status quo', fill=False)

plt.legend(loc='right')
plt.title('Rear end Time to Collision cumulative distribution functions')
plt.xlabel('Time to Collision (s)')
plt.ylabel('Frequency')

plt.savefig('cdf-rearEndTTCs.pdf')
plt.close()

#side TTCs
plt.hist(stop_minTTCs[2], density=True, histtype='step', cumulative=True, label='stop sign', fill=False)
plt.hist(yield_minTTCs[2], density=True, histtype='step', cumulative=True, label='yield sign', fill=False)
plt.hist(sQuo_minTTCs[2], density=True, histtype='step', cumulative=True, label='status quo', fill=False)

plt.legend(loc='right')
plt.title('Side Time to Collision cumulative distribution functions')
plt.xlabel('Time to Collision (s)')
plt.ylabel('Frequency')

plt.savefig('cdf-sideTTCs.pdf')
plt.close()

# PETs
plt.hist(stop_PETs, density=True, histtype='step', cumulative=True, label='stop sign', fill=False)
plt.hist(yield_PETs, density=True, histtype='step', cumulative=True, label='yield sign', fill=False)
plt.hist(sQuo_PETs, density=True, histtype='step', cumulative=True, label='status quo', fill=False)

plt.legend(loc='right')
plt.title('Post Encroachment Time Cumulative Distribution Functions')
plt.xlabel('Post Encroachment Time (s)')
plt.ylabel('Frequency')

plt.savefig('cdf-PETs.pdf')
plt.close()