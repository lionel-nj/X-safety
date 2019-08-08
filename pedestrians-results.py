import matplotlib.pyplot as plt
import numpy as np

import toolkit

results = {}
priorities = ['priorite auto', 'priorite pieton']

results[priorities[0]] = toolkit.loadYaml('sorties/pedestrians/pedestrians-results.yml')
results[priorities[1]] = toolkit.loadYaml('sorties/pedestrians/pedestrians-stop-results.yml')

minTTCs = {'priorite auto': toolkit.loadYaml('sorties/pedestrians/pedestrians-minTTC.yml'),
          'priorite pieton': toolkit.loadYaml('sorties/pedestrians/pedestrians-stop-minTTC.yml')}

for priority in priorities:
    ## cdf normée TTC rear end
    data = minTTCs[priority][1]
    sorted_data = np.sort(data)
    yvals = np.arange(len(sorted_data)) #/ float(len(sorted_data) - 1)
    plt.plot(sorted_data, yvals)
    # plt.show()
    plt.xlabel('$TTC_{min}$ de suivi (s)')
    plt.ylabel("Nombre d'observations cumulées")
    plt.legend(['priorité autos', 'priorité piétons'])
plt.savefig('cdf-pedestrians-rearEnd-TTC-raw.pdf')
plt.close()

for priority in priorities:
    ## cdf normée side end
    data = minTTCs[priority][2]
    sorted_data = np.sort(data)
    yvals = np.arange(len(sorted_data)) #/ float(len(sorted_data) - 1)
    plt.plot(sorted_data, yvals)
    # plt.plot(sorted_data, [k/15 for k in yvals])
    # plt.show()
    plt.xlabel('$TTC_{min}$ de côté (s)')
    plt.ylabel("Nombre d'observations cumulées")
    plt.legend(['priorité autos', 'priorité piétons'])
plt.savefig('cdf-pedetrians-side-TTC-raw.pdf')
plt.close()

for priority in priorities:
    ## cdf raw PETS
    data = [k* .1 for k in results[priority]['PETs']]
    sorted_data = np.sort(data)
    yvals = np.arange(len(sorted_data)) #/ float(len(sorted_data) - 1)
    plt.plot(sorted_data, yvals)
    # plt.show()
    plt.xlabel('PET (s)')
    plt.ylabel("Nombre d'observations cumulées")
    plt.legend(['priorité autos', 'priorité piétons'])
plt.savefig('cdf-pedestrians-PET-raw.pdf')
plt.close()

for priority in priorities:
    ## cdf raw nInter
    data = toolkit.flatten(results[priority]['minDistances'][1].values())
    sorted_data = np.sort(data)
    yvals = np.arange(len(sorted_data))
    plt.plot(sorted_data, yvals)
    # plt.plot([k*.1 for k in sorted_data], [k/15 for k in yvals])
    # plt.show()
    plt.xlabel("$D_{min}$ d'interaction de suivi(m)")
    plt.ylabel("Nombre d'observations cumulées")
    plt.legend(['priorité autos', 'priorité piétons'])
plt.savefig('cdf-pedestrians-minDistances-rear-end-raw.pdf')
plt.close()

for priority in priorities:
    ## cdf raw nInter
    data = toolkit.flatten(results[priority]['minDistances'][2].values())
    sorted_data = np.sort(data)
    yvals = np.arange(len(sorted_data))
    plt.plot(sorted_data, yvals)
    # plt.plot([k*.1 for k in sorted_data], [k/15 for k in yvals])
    # plt.show()
    plt.xlabel("$D_{min}$ d'interaction de côté(m)")
    plt.ylabel("Nombre d'observations cumulées")
    plt.legend(['priorité autos', 'priorité piétons'])
plt.savefig('cdf-pedestrians-minDistances-side-raw.pdf')
plt.close()



from scipy import stats

ksTestTTCS_side = [stats.ks_2samp(minTTCs['priorite pieton'][2], minTTCs['priorite auto'][2])]#toolkit.flatten(results[7000]['TTCs'][7000][2].values())), stats.ks_2samp(toolkit.flatten(results[2000]['TTCs'][2000][2].values()), toolkit.flatten(results[15000]['TTCs'][15000][2].values())), stats.ks_2samp(toolkit.flatten(results[15000]['TTCs'][15000][2].values()), toolkit.flatten(results[7000]['TTCs'][7000][2].values()))]

ksTestTTCS_rear = [stats.ks_2samp(minTTCs['priorite pieton'][1], minTTCs['priorite auto'][1])]#toolkit.flatten(results[7000]['TTCs'][7000][2].values())), stats.ks_2samp(toolkit.flatten(results[2000]['TTCs'][2000][2].values()), toolkit.flatten(results[15000]['TTCs'][15000][2].values())), stats.ks_2samp(toolkit.flatten(results[15000]['TTCs'][15000][2].values()), toolkit.flatten(results[7000]['TTCs'][7000][2].values()))]

ksTestPETS = [stats.ks_2samp(results['priorite pieton']['PETs'], results['priorite auto']['PETs'])]#toolkit.flatten(results[7000]['PETS'][7000].values())), stats.ks_2samp(toolkit.flatten(results[2000]['PETS'][2000].values()), toolkit.flatten(results[15000]['PETS'][15000].values())), stats.ks_2samp(toolkit.flatten(results[15000]['PETS'][15000].values()), toolkit.flatten(results[7000]['PETS'][7000].values()))]

ksTesksTest_minDistance_rear = [stats.ks_2samp(toolkit.flatten(results['priorite pieton']['minDistances'][1].values()), toolkit.flatten(results['priorite auto']['minDistances'][1].values()))]#toolkit.flatten(results[7000]['minDistances'][7000][2].values())), stats.ks_2samp(toolkit.flatten(results[2000]['minDistances'][2000][2].values()), toolkit.flatten(results[15000]['minDistances'][15000][2].values())), stats.ks_2samp(toolkit.flatten(results[15000]['minDistances'][15000][2].values()), toolkit.flatten(results[7000]['minDistances'][7000][2].values()))]

ksTesksTest_minDistance_side = [stats.ks_2samp(toolkit.flatten(results['priorite pieton']['minDistances'][2].values()), toolkit.flatten(results['priorite auto']['minDistances'][2].values()))]#toolkit.flatten(results[7000]['minDistances'][7000][2].values())), stats.ks_2samp(toolkit.flatten(results[2000]['minDistances'][2000][2].values()), toolkit.flatten(results[15000]['minDistances'][15000][2].values())), stats.ks_2samp(toolkit.flatten(results[15000]['minDistances'][15000][2].values()), toolkit.flatten(results[7000]['minDistances'][7000][2].values()))]

#
# samples = [expSample0, expSample1]
# for item in samples:
#     ## cdf raw PETS
#     data = item
#     sorted_data = np.sort(data)
#     yvals = np.arange(len(sorted_data))/ float(len(sorted_data) - 1)
#     plt.plot(sorted_data, yvals)
#     # plt.show()
#     plt.xlabel('x')
#     plt.ylabel("CDF")
#
#     plt.legend(['Échantillon 1', 'Échantillon 2'])
# plt.savefig('explication-ks.pdf')
# plt.close()
#
