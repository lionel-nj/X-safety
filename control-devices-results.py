import numpy as np

import toolkit

results = {}
controlDevices = ['stop', 'yield', 'sQuo']

for cd in controlDevices:
    results[cd] = toolkit.loadYaml('sorties/control devices/{}_results.yml'.format(cd))

for cd in controlDevices:
    ## cdf normée TTC rear end
    data = results[cd]['TTCs'][1]
    sorted_data = np.sort(data)
    yvals = np.arange(len(sorted_data)) #/ float(len(sorted_data) - 1)
    plt.plot(sorted_data, [k/15 for k in yvals])
    # plt.show()
    plt.xlabel('Rear-end minimum time-to-collision (s)')
    plt.ylabel('Number of observations')
    plt.legend(['stop sign', 'yield sign', 'no TCD'])
plt.savefig('cdf-rearEnd-TTC-raw.pdf')
plt.close()

for cd in controlDevices:
    ## cdf normée side end
    data = results[cd]['TTCs'][2]
    sorted_data = np.sort(data)
    yvals = np.arange(len(sorted_data)) / float(len(sorted_data) - 1)
    plt.plot(sorted_data, yvals)
    # plt.plot(sorted_data, [k/15 for k in yvals])
    # plt.show()
    plt.xlabel('Side minimum time-to-collision (s)')
    plt.ylabel('Number of observations')
    plt.legend(['stop sign', 'yield sign', 'no TCD'])
plt.savefig('cdf-side-TTC-normed.pdf')
plt.close()

for cd in controlDevices:
    ## cdf raw PETS
    data = results[cd]['PETS']
    sorted_data = np.sort(data)
    yvals = np.arange(len(sorted_data)) / float(len(sorted_data) - 1)
    # plt.plot(sorted_data, yvals)
    plt.plot([k*.1 for k in sorted_data], yvals)
    # plt.show()
    plt.xlabel('Post encroachment time (s)')
    plt.ylabel('Frequencies')
    plt.legend(['stop sign', 'yield sign', 'no TCD'])
plt.savefig('cdf-side-PET-normed.pdf')
plt.close()

for cd in controlDevices:
    ## cdf raw nInter
    data = toolkit.flatten(results[cd]['minDistances'][1].values())
    sorted_data = np.sort(data)
    yvals = np.arange(len(sorted_data))/ float(len(sorted_data) - 1)
    plt.plot(sorted_data, yvals)
    # plt.plot([k*.1 for k in sorted_data], [k/15 for k in yvals])
    # plt.show()
    plt.xlabel('Minimum distances of rear-end interactions (m)')
    plt.ylabel('Frequencies')
    plt.legend(['stop sign', 'yield sign', 'no TCD'])
plt.savefig('cdf-nInter-PET-rear-end-normed.pdf')
plt.close()

for cd in controlDevices:
    ## cdf raw nInter
    data = toolkit.flatten(results[cd]['minDistances'][2].values())
    sorted_data = np.sort(data)
    yvals = np.arange(len(sorted_data))/ float(len(sorted_data) - 1)
    plt.plot(sorted_data, yvals)
    # plt.plot([k*.1 for k in sorted_data], [k/15 for k in yvals])
    # plt.show()
    plt.xlabel('Minimum distances of side interactions (m)')
    plt.ylabel('Frequencies')
    plt.legend(['stop sign', 'yield sign', 'no TCD'])
plt.savefig('cdf-nInter-PET-side-normed.pdf')
plt.close()

for cd in controlDevices:
    ## pdf rear end TTC - raw
    data = results[cd]['TTCs'][1]
    # bins = np.linspace(min(data), max(data), 1)
    histogram, bins = np.histogram(data)
    bin_centers = 0.5 * (bins[1:] + bins[:-1])
    plt.plot(bin_centers, [k/15 for k in histogram])#, label="Histogram of samples")
    plt.xlabel('Rear-end minimum time-to-collision (s)')
    plt.ylabel('Number of observations')
    plt.legend(['stop sign', 'yield sign', 'no TCD'])
plt.savefig('pdf-rearEnd-TTC-raw.pdf')
plt.close()

for cd in controlDevices:
    ## pdf side TTC - raw
    data = results[cd]['TTCs'][2]
    # bins = np.linspace(min(data), max(data), 1)
    histogram, bins = np.histogram(data)
    bin_centers = 0.5 * (bins[1:] + bins[:-1])
    plt.plot(bin_centers, [k/15 for k in histogram])#, label="Histogram of samples")
    plt.xlabel('Side minimum time-to-collision (s)')
    plt.ylabel('Number of observations')
    plt.legend(['stop sign', 'yield sign', 'no TCD'])
plt.savefig('pdf-side-TTC-raw.pdf')
plt.close()

for cd in controlDevices:
    ## pdf PETS- raw
    data = results[cd]['PETS']
    histogram, bins = np.histogram(data)
    bin_centers = .1* 0.5 * (bins[1:] + bins[:-1])
    plt.plot(bin_centers, [k/15 for k in histogram])#, label="Histogram of samples")
    plt.xlabel('Post encroachment time (s)')
    plt.ylabel('Number of observations')
    plt.legend(['stop sign', 'yield sign', 'no TCD'])
plt.savefig('pdf-PETS-raw.pdf')
plt.close()

for cd in controlDevices:
    ## pdf rear end min distance- raw
    data = toolkit.flatten(results[cd]['minDistances'][1].values())
    histogram, bins = np.histogram(data)
    bin_centers = 0.5 * (bins[1:] + bins[:-1])
    plt.plot(bin_centers, [k/15 for k in histogram])#, label="Histogram of samples")
    plt.xlabel('Rear-end minimum interaction distance (m)')
    plt.ylabel('Number of observations')
    plt.legend(['stop sign', 'yield sign', 'no TCD'])
plt.savefig('pdf-rear-end-minDistance-raw.pdf')
plt.close()


for cd in controlDevices:
    ## pdf side min distance- raw
    data = toolkit.flatten(results[cd]['minDistances'][2].values())
    histogram, bins = np.histogram(data)
    bin_centers = 0.5 * (bins[1:] + bins[:-1])
    plt.plot(bin_centers, [k/15 for k in histogram])#, label="Histogram of samples")
    plt.xlabel('Side minimum interaction distance (m)')
    plt.ylabel('Number of observations')
    plt.legend(['stop sign', 'yield sign', 'no TCD'])
plt.savefig('pdf-side-minDistance-raw.pdf')
plt.close()

## pdf side min distance- raw
for cd in controlDevices:
    y = []
    data = [10, 20, 50]
    plt.plot(data, [results[cd]['nInter10'][2], results[cd]['nInter20'][2], results[cd]['nInter50'][2]])

plt.xlabel('Minimum distance of side interaction (m)')
plt.ylabel('Number of observations')
plt.legend(['stop sign', 'yield sign', 'no TCD'])
plt.savefig('sidenInter_variations.pdf')
plt.close()

