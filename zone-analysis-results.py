import matplotlib as plt
import numpy as np

import simulation
import toolkit

results = {}
surfaces = [2000, 7000, 15000]
for zone in surfaces:
    results[zone] = toolkit.loadYaml('sorties/zone analysis/zone{}-results-v3.yml'.format(zone))

sim = simulation.Simulation.load('config.yml')
seeds = [sim.seed+i*sim.increment for i in range(sim.rep)]

surfaces = [2000]
for surface in surfaces:
    rearEndTTC_mean = []
    rearEndTTC_std = []

    sideTTC_mean = []
    sideTTC_std = []

    PETS_mean = []
    PETS_std = []

    rearEndnInter10_mean = []
    rearEndnInter20_mean = []
    rearEndnInter50_mean = []

    rearEndnInter10_std = []
    rearEndnInter20_std = []
    rearEndnInter50_std = []

    sidenInter10_mean = []
    sidenInter20_mean = []
    sidenInter50_mean = []

    sidenInter10_std = []
    sidenInter20_std = []
    sidednInter50_std = []

    for seed in seeds:
        rearEndTTC_mean.append(np.mean(results[surface]['TTCs'][surface][1][seed]))
        rearEndTTC_std.append(np.std(results[surface]['TTCs'][surface][1][seed]))

        sideTTC_mean.append(np.mean(results[surface]['TTCs'][surface][2][seed]))
        sideTTC_std.append(np.std(results[surface]['TTCs'][surface][2][seed]))

        PETS_mean.append(np.mean(results[surface]['PETS'][surface][seed]))
        PETS_std.append(np.std(results[surface]['PETS'][surface][seed]))

    rearEndnInter10_mean = np.mean(results[surface]['rear-nInter10'][surface])
    rearEndnInter20_mean = np.mean(results[surface]['rear-nInter20'][surface])
    rearEndnInter50_mean = np.mean(results[surface]['rear-nInter50'][surface])

    sidenInter10_mean = np.mean(results[surface]['side-nInter10'][surface])
    sidenInter20_mean = np.mean(results[surface]['side-nInter20'][surface])
    sidenInter50_mean = np.mean(results[surface]['side-nInter50'][surface])

    rearEndnInter10_std = np.std(results[surface]['rear-nInter10'][surface])
    rearEndnInter20_std = np.std(results[surface]['rear-nInter20'][surface])
    rearEndnInter50_std = np.std(results[surface]['rear-nInter50'][surface])

    sidenInter10_std = np.std(results[surface]['side-nInter10'][surface])
    sidenInter20_std = np.std(results[surface]['side-nInter20'][surface])
    sidednInter50_std = np.std(results[surface]['side-nInter50'][surface])

    print('rear end TTC mean', np.mean(rearEndTTC_mean))
    print('rear end TTC std', np.std(rearEndTTC_std))
    print('obs', len(toolkit.flatten(results[surface]['TTCs'][surface][1].values()))/15)

    print('side TTC mean', np.mean(sideTTC_mean))
    print('side TTC std', np.std(sideTTC_std))
    print('obs', len(toolkit.flatten(results[surface]['TTCs'][surface][2].values()))/15)

    print('PET mean', np.mean(PETS_mean))
    print(' std', np.std(PETS_std))
    print('obs', len(toolkit.flatten(results[surface]['PETS'][surface].values()))/15)

    print('rear end nInter10 mean', rearEndnInter10_mean)
    print(' std', rearEndnInter10_std)
    print('obs', len(results[surface]['rear-nInter10'][surface])/15)

    print('rear end nInter20 mean', rearEndnInter20_mean)
    print(' std', rearEndnInter20_std)
    print('obs', len(results[surface]['rear-nInter20'][surface]) / 15)

    print('rear end nInter50 mean', rearEndnInter50_mean)
    print(' std', rearEndnInter50_std)
    print('obs', len(results[surface]['rear-nInter50'][surface]) / 15)

    print('side nInter10 mean', sidenInter10_mean)
    print(' std', sidenInter10_std)
    print('obs', len(results[surface]['side-nInter10'][surface]) / 15)

    print('side nInter20 mean', sidenInter20_mean)
    print(' std', sidenInter20_std)
    print('obs', len(results[surface]['side-nInter20'][surface]) / 15)

    print('side nInter50 mean', sidenInter50_mean)
    print(' std', sidednInter50_std)
    print('obs', len(results[surface]['side-nInter50'][surface]) / 15)


for surface in surfaces :
    ## pdf min sde distacces - raw
    data = toolkit.flatten(results[surface]['minDistances'][surface][2].values())
    histogram, bins = np.histogram(data)
    bin_centers = 0.5 * (bins[1:] + bins[:-1])
    plt.plot(bin_centers, [k / 15 for k in histogram])  # , label="Histogram of samples")
    plt.xlabel('Minimum distance for side interactions (m)')
    plt.ylabel('Number of observations')
    plt.legend(['area: 2000 m2', 'area: 7000m2', 'area: 15000 m2'])
plt.savefig('pdf-zone-side-minDistance-raw.pdf')
plt.close()

for surface in surfaces :
    ## pdf min sde distacces - raw
    data = toolkit.flatten(results[surface]['minDistances'][surface][1].values())
    histogram, bins = np.histogram(data)
    bin_centers = 0.5 * (bins[1:] + bins[:-1])
    plt.plot(bin_centers, [k / 15 for k in histogram])  # , label="Histogram of samples")
    plt.xlabel('Minimum distance for rear-end interactions (m)')
    plt.ylabel('Number of observations')
    plt.legend(['area: 2000 m2', 'area: 7000m2', 'area: 15000 m2'])
plt.savefig('pdf-zone-rear-end-minDistance-raw.pdf')
plt.close()

for surface in surfaces :
    ## pdf min sde distaces - raw
    data = toolkit.flatten(results[surface]['TTCs'][surface][2].values())
    histogram, bins = np.histogram(data)
    bin_centers = 0.5 * (bins[1:] + bins[:-1])
    plt.plot(bin_centers, [k / 15 for k in histogram])  # , label="Histogram of samples")
    plt.xlabel('Minimum time to collision for side interactions (s)')
    plt.ylabel('Number of observations')
    plt.legend(['area: 2000 m2', 'area: 7000m2', 'area: 15000 m2'])
plt.savefig('pdf-zone-side-TTCs-raw.pdf')
plt.close()

for surface in surfaces :
    ## pdf min sde distaces - raw
    data = toolkit.flatten(results[surface]['TTCs'][surface][1].values())
    histogram, bins = np.histogram(data)
    bin_centers = 0.5 * (bins[1:] + bins[:-1])
    plt.plot(bin_centers, [k / 15 for k in histogram])  # , label="Histogram of samples")
    plt.xlabel('Minimum time to collision for rear-end interactions (s)')
    plt.ylabel('Number of observations')
    plt.legend(['area: 2000 m2', 'area: 7000m2', 'area: 15000 m2'])
plt.savefig('pdf-zone-rear-TTCs-raw.pdf')
plt.close()

for surface in surfaces :
    ## pdf min sde distaces - raw
    data = toolkit.flatten(results[surface]['PETS'][surface].values())
    histogram, bins = np.histogram(data)
    bin_centers = 0.5 * (bins[1:] + bins[:-1])
    plt.plot(bin_centers, [k / 15 for k in histogram])  # , label="Histogram of samples")
    plt.xlabel('Post encrochament time (s)')
    plt.ylabel('Number of observations')
    plt.legend(['area: 2000 m2', 'area: 7000m2', 'area: 15000 m2'])
plt.savefig('pdf-zone-side-PETS-raw.pdf')
plt.close()


from scipy import stats

ksTestTTCS_side = [stats.ks_2samp(toolkit.flatten(results[2000]['TTCs'][2000][2].values()), toolkit.flatten(results[7000]['TTCs'][7000][2].values())), stats.ks_2samp(toolkit.flatten(results[2000]['TTCs'][2000][2].values()), toolkit.flatten(results[15000]['TTCs'][15000][2].values())), stats.ks_2samp(toolkit.flatten(results[15000]['TTCs'][15000][2].values()), toolkit.flatten(results[7000]['TTCs'][7000][2].values()))]

ksTestPETS = [stats.ks_2samp(toolkit.flatten(results[2000]['PETS'][2000].values()), toolkit.flatten(results[7000]['PETS'][7000].values())), stats.ks_2samp(toolkit.flatten(results[2000]['PETS'][2000].values()), toolkit.flatten(results[15000]['PETS'][15000].values())), stats.ks_2samp(toolkit.flatten(results[15000]['PETS'][15000].values()), toolkit.flatten(results[7000]['PETS'][7000].values()))]

ksTesksTest_minDistance_side = [stats.ks_2samp(toolkit.flatten(results[2000]['minDistances'][2000][2].values()), toolkit.flatten(results[7000]['minDistances'][7000][2].values())), stats.ks_2samp(toolkit.flatten(results[2000]['minDistances'][2000][2].values()), toolkit.flatten(results[15000]['minDistances'][15000][2].values())), stats.ks_2samp(toolkit.flatten(results[15000]['minDistances'][15000][2].values()), toolkit.flatten(results[7000]['minDistances'][7000][2].values()))]

ksTesksTest_minDistance_rear = [stats.ks_2samp(toolkit.flatten(results[2000]['minDistances'][2000][1].values()), toolkit.flatten(results[7000]['minDistances'][7000][1].values())), stats.ks_2samp(toolkit.flatten(results[2000]['minDistances'][2000][1].values()), toolkit.flatten(results[15000]['minDistances'][15000][1].values())), stats.ks_2samp(toolkit.flatten(results[15000]['minDistances'][15000][1].values()), toolkit.flatten(results[7000]['minDistances'][7000][1].values()))]

ksTestTTCS_rear = [stats.ks_2samp(toolkit.flatten(results[2000]['TTCs'][2000][1].values()), toolkit.flatten(results[7000]['TTCs'][7000][1].values())), stats.ks_2samp(toolkit.flatten(results[2000]['TTCs'][2000][1].values()), toolkit.flatten(results[15000]['TTCs'][15000][1].values())), stats.ks_2samp(toolkit.flatten(results[15000]['TTCs'][15000][1].values()), toolkit.flatten(results[7000]['TTCs'][7000][1].values()))]


#####

