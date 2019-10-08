import math

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

import toolkit

baseCaseResults = toolkit.loadYaml('sorties/00base-case-results.yml')
baseCaseResults['speedDifferential'] = [-k for k in baseCaseResults['speedDifferential']]

# for var in baseCaseResults:
#         if var == 'minTTCs':
#             baseCaseResults[var][1] = cleanData(baseCaseResults[var][1])
#             baseCaseResults[var][2] = cleanData(baseCaseResults[var][2])
#         elif var == 'PETs':
#             baseCaseResults[var] = cleanData(baseCaseResults[var])


baseCaseRearEndMeanTTCmin = np.mean(baseCaseResults["minTTCs"][1])
baseCaseRearEndSTdTTCmin = np.std(baseCaseResults["minTTCs"][1])

baseCaseRearEndMeanDistance = np.mean(baseCaseResults["minDistances"][1])
baseCaseRearEndSTDistance = np.std(baseCaseResults["minDistances"][1])

baseCaseSideDistance = np.mean(baseCaseResults["minDistances"][2])
baseCaseSideSTDistance = np.std(baseCaseResults["minDistances"][2])

baseCaseSideTTCmin = np.mean(baseCaseResults["minTTCs"][2])
baseCaseSideTTCminStd = np.std(baseCaseResults["minTTCs"][2])

baseCaseMeanPET = np.mean(baseCaseResults["PETs"])
baseCaseSTdPET = np.std(baseCaseResults["PETs"])

baseCaseMeanSideInter10 = np.mean(baseCaseResults["sidenInter10"])
baseCaseMeanSideInter20 = np.mean(baseCaseResults["sidenInter20"])
baseCaseMeanSideInter50 = np.mean(baseCaseResults["sidenInter50"])
baseCaseStdSideInter10 = np.std(baseCaseResults["sidenInter10"])
baseCaseStdSideInter20 = np.std(baseCaseResults["sidenInter20"])
baseCaseStdSideInter50 = np.std(baseCaseResults["sidenInter50"])

baseCaseMeanRearInter10 = np.mean(baseCaseResults["rearEndnInter10"])
baseCaseMeanRearInter20 = np.mean(baseCaseResults["rearEndnInter20"])
baseCaseMeanRearInter50 = np.mean(baseCaseResults["rearEndnInter50"])
baseCaseStdRearInter10 = np.std(baseCaseResults["rearEndnInter10"])
baseCaseStdRearInter20 = np.std(baseCaseResults["rearEndnInter20"])
baseCaseStdRearInter50 = np.std(baseCaseResults["rearEndnInter50"])

baseCaseCompletedUsers0Mean = np.mean(baseCaseResults['completedUser0'])
baseCaseCompletedUsers2Mean = np.mean(baseCaseResults['completedUSers2'])

baseCaseCompletedUsers0std = np.std(baseCaseResults['completedUser0'])
baseCaseCompletedUsers2std = np.std(baseCaseResults['completedUSers2'])

baseCaseTimeCongestionPercentageMean0 = np.mean(toolkit.loadYaml('sorties/00base-case-results-percentageCongestion.yml')['meanTimePercentageInCongestion'][0])
baseCaseTimeCongestionPercentageMean2 = np.mean(toolkit.loadYaml('sorties/00base-case-results-percentageCongestion.yml')['meanTimePercentageInCongestion'][2])

baseCaseV2 = np.mean(baseCaseResults['speedV1Lane2'])

def getSensivities(parameter):
    results = {"-40": {
                       'speedV1Lane2': toolkit.loadYaml('sorties/sa-meanSpeedV1Lane2{}.yml'.format(parameter))[parameter][-.4],
                           "timePercentageCongestion2Mean":  toolkit.loadYaml('sorties/sa-meanTimePercentageCongestion-{}.yml'.format(parameter))[parameter][-.4],
                       "completedUSers2": toolkit.loadYaml('sorties/numberOfUsers2-{}-0.4.yml'.format(parameter))[parameter][-.4],
                       "sidenInter10": toolkit.loadYaml('sorties/sa-side-nInter10-{}-0.4.yml'.format(parameter)),
                       "sidenInter20": toolkit.loadYaml('sorties/sa-side-nInter20-{}-0.4.yml'.format(parameter)),
                       "sidenInter50": toolkit.loadYaml('sorties/sa-side-nInter50-{}-0.4.yml'.format(parameter)),
                       "rearEndnInter10": toolkit.loadYaml('sorties/sa-rearEnd-nInter10-{}-0.4.yml'.format(parameter)),
                       "rearEndnInter20": toolkit.loadYaml('sorties/sa-rearEnd-nInter20-{}-0.4.yml'.format(parameter)),
                       "rearEndnInter50": toolkit.loadYaml('sorties/sa-rearEnd-nInter50-{}-0.4.yml'.format(parameter)),
                         "minTTCs": toolkit.loadYaml('sorties/sa-minTTCs-{}-0.4.yml'.format(parameter)),
                        "PETs": toolkit.loadYaml('sorties/sa-PETs-{}-0.4.yml'.format(parameter)),
                       'minDistances':toolkit.loadYaml('sorties/sa-minDistances-{}-0.4.yml'.format(parameter)),
                       'speedDifferential' : [-k for k in toolkit.loadYaml('sorties/sa-speedDifferentials-{}.yml'.format(parameter))[parameter][-.4]]
                        # "nInter10": toolkit.loadYaml('sorties/sa-nInter10{}-0.4.yml'.format(parameter)),
                        # "nInter20":toolkit.loadYaml('sorties/sa-nInter20{}-0.4.yml'.format(parameter)),
                        # "nInter50":toolkit.loadYaml('sorties/sa-nInter50{}-0.4.yml'.format(parameter)),
                       # "completedUser0":  toolkit.loadYaml('sorties/numberOfUsers0-{}-0.4.yml'.format(parameter))[parameter][-.4],

    },

                 "+40": {
                         'speedV1Lane2': toolkit.loadYaml('sorties/sa-meanSpeedV1Lane2{}.yml'.format(parameter))[parameter][.4],
                         "timePercentageCongestion2Mean": toolkit.loadYaml('sorties/sa-meanTimePercentageCongestion-{}.yml'.format(parameter))[parameter][.4],
                "completedUSers2":toolkit.loadYaml('sorties/numberOfUsers2-{}0.4.yml'.format(parameter))[parameter][.4],
               "sidenInter10": toolkit.loadYaml('sorties/sa-side-nInter10-{}0.4.yml'.format(parameter)),
               "sidenInter20": toolkit.loadYaml('sorties/sa-side-nInter20-{}0.4.yml'.format(parameter)),
               "sidenInter50": toolkit.loadYaml('sorties/sa-side-nInter50-{}0.4.yml'.format(parameter)),
               "rearEndnInter10": toolkit.loadYaml('sorties/sa-rearEnd-nInter10-{}0.4.yml'.format(parameter)),
               "rearEndnInter20": toolkit.loadYaml('sorties/sa-rearEnd-nInter20-{}0.4.yml'.format(parameter)),
               "rearEndnInter50": toolkit.loadYaml('sorties/sa-rearEnd-nInter50-{}0.4.yml'.format(parameter)),
                     "minTTCs": toolkit.loadYaml('sorties/sa-minTTCs-{}0.4.yml'.format(parameter)),
                        "PETs": toolkit.loadYaml('sorties/sa-PETs-{}0.4.yml'.format(parameter)),
                         'minDistances': toolkit.loadYaml('sorties/sa-minDistances-{}0.4.yml'.format(parameter)),
                         'speedDifferential': [-k for k in toolkit.loadYaml('sorties/sa-speedDifferentials-{}.yml'.format(parameter))[parameter][.4]]
                        # "nInter10":toolkit.loadYaml('sorties/sa-nInter10{}0.4.yml'.format(parameter)),
                        # "nInter20":toolkit.loadYaml('sorties/sa-nInter20{}0.4.yml'.format(parameter)),
                        # "nInter50":toolkit.loadYaml('sorties/sa-nInter50{}0.4.yml'.format(parameter)),
                # "completedUser0":toolkit.loadYaml('sorties/numberOfUsers0-{}0.4.yml'.format(parameter))[parameter][.4],

                         }
               }

    rearEndMeanDistance = {"-40": 100*(np.mean(results['-40']["minDistances"][1])-baseCaseRearEndMeanDistance)/baseCaseRearEndMeanDistance, "+40": 100*(np.mean(results['+40']["minDistances"][1])-baseCaseRearEndMeanDistance)/baseCaseRearEndMeanDistance}
    rearEndStdDistance = {"-40": (np.std(results['-40']["minDistances"][1]))/baseCaseRearEndSTDistance, "+40": (np.mean(results['+40']["minDistances"][1]))/baseCaseRearEndSTDistance}

    sideMeanDistance = {"-40": 100*(np.mean(results['-40']["minDistances"][2])-baseCaseSideDistance)/baseCaseSideDistance, "+40": 100*(np.mean(results['+40']["minDistances"][2])-baseCaseSideDistance)/baseCaseSideDistance}
    sideStdDistance = {"-40": (np.std(results['-40']["minDistances"][2]))/baseCaseSideSTDistance, "+40": (np.mean(results['+40']["minDistances"][2]))/baseCaseSideSTDistance}

    rearEndMeanTTCmin = {"-40": 100*(np.mean(results['-40']["minTTCs"][1])-baseCaseRearEndMeanTTCmin)/baseCaseRearEndMeanTTCmin, "+40": 100*(np.mean(results['+40']["minTTCs"][1])-baseCaseRearEndMeanTTCmin)/baseCaseRearEndMeanTTCmin}
    rearEndSTdTTC = {"-40": np.std(results['-40']["minTTCs"][1])/baseCaseRearEndSTdTTCmin, "+40": np.std(results['+40']["minTTCs"][1])/baseCaseRearEndSTdTTCmin}

    sideMeanTTCmin = {"-40": 100*(np.mean(results['-40']["minTTCs"][2])-baseCaseSideTTCmin)/baseCaseSideTTCmin, "+40": 100*(np.mean(results['+40']["minTTCs"][2])-baseCaseSideTTCmin)/baseCaseSideTTCmin}
    sideSTdTTCmin = {"-40": np.std(results['-40']["minTTCs"][2])/baseCaseSideTTCminStd, "+40": np.std(results['+40']["minTTCs"][2])/baseCaseSideTTCminStd}

    meanPET = {"-40": 100*(np.mean(results['-40']["PETs"])-baseCaseMeanPET)/baseCaseMeanPET, "+40": 100*(np.mean(results['+40']["PETs"])-baseCaseMeanPET)/baseCaseMeanPET}
    stdPET = {"-40": np.std(results['-40']["PETs"])/baseCaseSTdPET, "+40": np.std(results['+40']["PETs"])/baseCaseSTdPET}
    #
    meanSideInter10 = {"-40": 100*(np.mean(results["-40"]["sidenInter10"])-baseCaseMeanSideInter10)/baseCaseMeanSideInter10, "+40": 100*(np.mean(results["+40"]["sidenInter10"])-baseCaseMeanSideInter10)/baseCaseMeanSideInter10}
    meanSideInter20 = {"-40": 100*(np.mean(results["-40"]["sidenInter20"])-baseCaseMeanSideInter20)/baseCaseMeanSideInter20, "+40": 100*(np.mean(results["+40"]["sidenInter20"])-baseCaseMeanSideInter20)/baseCaseMeanSideInter50}
    meanSideInter50 = {"-40": 100*(np.mean(results["-40"]["sidenInter50"])-baseCaseMeanSideInter50)/baseCaseMeanSideInter50, "+40": 100*(np.mean(results["+40"]["sidenInter50"])-baseCaseMeanSideInter50)/baseCaseMeanSideInter50}

    meanSideInter10_std = {"-40": np.std(results["-40"]["sidenInter10"])/baseCaseMeanSideInter10, "+40": np.std(results["+40"]["sidenInter10"])/baseCaseMeanSideInter10}
    meanSideInter20_std = {"-40": np.std(results["-40"]["sidenInter20"])/baseCaseMeanSideInter20, "+40": np.std(results["+40"]["sidenInter20"])/baseCaseMeanSideInter20}
    meanSideInter50_std = {"-40": np.std(results["-40"]["sidenInter50"])/baseCaseMeanSideInter50, "+40": np.std(results["+40"]["sidenInter50"])/baseCaseMeanSideInter50}
    #
    meanRearInter10 = {"-40": 100*(np.mean(results["-40"]["rearEndnInter10"])-baseCaseMeanRearInter10)/baseCaseMeanRearInter10, "+40": 100*(np.mean(results["+40"]["rearEndnInter10"])-baseCaseMeanRearInter10)/baseCaseMeanRearInter10}
    meanRearInter20 = {"-40": 100*(np.mean(results["-40"]["rearEndnInter20"])-baseCaseMeanRearInter20)/baseCaseMeanRearInter20, "+40": 100*(np.mean(results["+40"]["rearEndnInter20"])-baseCaseMeanRearInter20)/baseCaseMeanRearInter20}
    meanRearInter50 = {"-40": 100*(np.mean(results["-40"]["rearEndnInter50"])-baseCaseMeanRearInter50)/baseCaseMeanRearInter50, "+40": 100*(np.mean(results["+40"]["rearEndnInter50"])-baseCaseMeanRearInter50)/baseCaseMeanRearInter50}

    meanRearInter10_std = {"-40": np.std(results["-40"]["rearEndnInter10"])/baseCaseMeanRearInter10, "+40": np.std(results["+40"]["rearEndnInter10"])/baseCaseMeanRearInter10}
    meanRearInter20_std = {"-40": np.std(results["-40"]["rearEndnInter20"])/baseCaseMeanRearInter20, "+40": np.std(results["+40"]["rearEndnInter20"])/baseCaseMeanRearInter20}
    meanRearInter50_std = {"-40": np.std(results["-40"]["rearEndnInter50"])/baseCaseMeanRearInter50, "+40": np.std(results["+40"]["rearEndnInter50"])/baseCaseMeanRearInter50}

    completedUSers2_mean = {'-40': 100*(np.mean(results['-40']["completedUSers2"])-baseCaseCompletedUsers2Mean)/baseCaseCompletedUsers2Mean, '+40': 100*(np.mean(results['+40']["completedUSers2"])-baseCaseCompletedUsers2Mean)/baseCaseCompletedUsers2Mean}
    percentageTimeCongestion2Mean = {'-40': 100*(np.mean(results['-40']["timePercentageCongestion2Mean"])-baseCaseTimeCongestionPercentageMean2)/baseCaseTimeCongestionPercentageMean2, '+40': 100*(np.mean(results['+40']["timePercentageCongestion2Mean"])-baseCaseTimeCongestionPercentageMean2)/baseCaseTimeCongestionPercentageMean2}
    speedV1Lane2mean = {'-40': 100*(np.mean(results['-40']["speedV1Lane2"])-baseCaseV2)/baseCaseV2, '+40': 100*(np.mean(results['+40']["speedV1Lane2"])-baseCaseV2)/baseCaseV2}


    values = {
                'speedV1Lane2mean':{'-40':np.mean(results['-40']["speedV1Lane2"]), '+40':np.mean(results['+40']["speedV1Lane2"])},
                'percentageTimeCongestion2Mean':{'-40':np.mean(results['-40']["timePercentageCongestion2Mean"]), '+40':np.mean(results['+40']["timePercentageCongestion2Mean"])},
                "completedUsers2": {'-40':np.mean(results['-40']["completedUSers2"]), '+40':np.mean(results['+40']["completedUSers2"])},
                "sidenInter10": {'-40':np.mean(results["-40"]["sidenInter10"]), '+40': np.mean(results["+40"]["sidenInter10"])},
                "sidenInter20": {'-40':np.mean(results["-40"]["sidenInter20"]), '+40': np.mean(results["+40"]["sidenInter20"])},
                "sidenInter50": {'-40':np.mean(results["-40"]["sidenInter50"]), '+40': np.mean(results["+40"]["sidenInter50"])},
                "sideTTCmin": {'-40':np.mean(results["-40"]["minTTCs"][2]), '+40': np.mean(results["+40"]["minTTCs"][2])},
                "PETs": {'-40':np.mean(results["-40"]["PETs"]), '+40': np.mean(results["+40"]["PETs"])},
                "sideMeanDistance": {'-40':np.mean(results["-40"]["minDistances"][2]), '+40': np.mean(results["+40"]["minDistances"][2])},
                "rearnInter10": {'-40':np.mean(results["-40"]["rearEndnInter10"]), '+40': np.mean(results["+40"]["rearEndnInter10"])},
                "rearnInter20": {'-40':np.mean(results["-40"]["rearEndnInter20"]), '+40': np.mean(results["+40"]["rearEndnInter20"])},
                "rearnInter50": {'-40':np.mean(results["-40"]["rearEndnInter50"]), '+40': np.mean(results["+40"]["rearEndnInter50"])},
                "rearEndTTCmin": {'-40':np.mean(results["-40"]["minTTCs"][1]), '+40': np.mean(results["+40"]["minTTCs"][1])},
                "rearEndMeanDistance": {'-40': np.mean(results["-40"]["minDistances"][1]), '+40': np.mean(results["+40"]["minDistances"][1])},

    }




    rearEndTTCSensitivity = rearEndMeanTTCmin#{"-40": np.mean([(100 * (x - baseCaseRearEndMeanTTCmin)) / baseCaseRearEndMeanTTCmin for x in results['-40']["minTTCs"][1]]), "+40": np.mean([(100 * (x - baseCaseRearEndMeanTTCmin)) / baseCaseRearEndMeanTTCmin for x in results['+40']["minTTCs"][1]])}
    sideTTCSensitivity = sideMeanTTCmin#{"-40": np.mean([(100 * (x - baseCaseSideTTCmin)) / baseCaseSideTTCmin for x in results['-40']["minTTCs"][2]]), "+40": np.mean([(100 * (x - baseCaseSideTTCmin)) / baseCaseSideTTCmin for x in results['+40']["minTTCs"][2]])}
    petsSensitivity = meanPET#{"-40": np.mean([(100 * (x - baseCaseMeanPET)) / baseCaseMeanPET for x in results['-40']["PETs"]]), "+40": np.mean([(100 * (x - baseCaseMeanPET)) / baseCaseMeanPET for x in results['+40']["PETs"]])}

    rearEndTTCSensitivity_std = rearEndSTdTTC#{"-40": ((100 * (rearEndSTdTTC["-40"] - baseCaseRearEndSTdTTCmin)) / baseCaseRearEndSTdTTCmin), "+40": ((100 * (rearEndSTdTTC["+40"] - baseCaseRearEndSTdTTCmin)) / baseCaseRearEndSTdTTCmin)}
    sideTTCSensitivity_std = sideSTdTTCmin#{"-40": ((100 * (sideSTdTTCmin["-40"] - baseCaseSideTTCminStd)) / baseCaseSideTTCminStd), "+40": ((100 * (sideSTdTTCmin["+40"] - baseCaseSideTTCminStd)) / baseCaseSideTTCminStd)}
    petsSensitivity_std = stdPET#{"-40": ((100 * (stdPET["-40"] - baseCaseSTdPET)) / baseCaseSTdPET), "+40": ((100 * (stdPET["+40"] - baseCaseSTdPET)) / baseCaseSTdPET)}
    #
    sidenInter10Sensitivity = meanSideInter10#{"-40": np.mean([(100 * (x - baseCaseMeanSideInter10)) / baseCaseMeanSideInter10 for x in results['-40']["sidenInter10"]]), "+40": np.mean([(100 * (x - baseCaseMeanSideInter10)) / baseCaseMeanSideInter10 for x in results['+40']["sidenInter10"]])}
    sidenInter20Sensitivity = meanSideInter20#{"-40": np.mean([(100 * (x - baseCaseMeanSideInter20)) / baseCaseMeanSideInter20 for x in results['-40']["sidenInter20"]]), "+40": np.mean([(100 * (x - baseCaseMeanSideInter20)) / baseCaseMeanSideInter10 for x in results['+40']["sidenInter20"]])}
    sidenInter50Sensitivity = meanSideInter50#{"-40": np.mean([(100 * (x - baseCaseMeanSideInter50)) / baseCaseMeanSideInter50 for x in results['-40']["sidenInter50"]]), "+40": np.mean([(100 * (x - baseCaseMeanSideInter50)) / baseCaseMeanSideInter10 for x in results['+40']["sidenInter50"]])}

    sidenInter10Sensitivity_std = meanSideInter10_std#{"-40": np.std([(100 * (x - baseCaseMeanSideInter10)) / baseCaseMeanSideInter10 for x in results['-40']["sidenInter10"]])/baseCaseMeanSideInter10, "+40": np.std([(100 * (x - baseCaseMeanSideInter10)) / baseCaseMeanSideInter10 for x in results['+40']["sidenInter10"]])/baseCaseMeanSideInter10}
    sidenInter20Sensitivity_std = meanSideInter20_std#{"-40": np.std([(100 * (x - baseCaseMeanSideInter20)) / baseCaseMeanSideInter20 for x in results['-40']["sidenInter20"]])/baseCaseMeanSideInter20, "+40": np.std([(100 * (x - baseCaseMeanSideInter20)) / baseCaseMeanSideInter10 for x in results['+40']["sidenInter20"]])/baseCaseMeanSideInter20}
    sidenInter50Sensitivity_std = meanSideInter50_std#{"-40": np.std([(100 * (x - baseCaseMeanSideInter50)) / baseCaseMeanSideInter50 for x in results['-40']["sidenInter50"]])/baseCaseMeanSideInter50, "+40": np.std([(100 * (x - baseCaseMeanSideInter50)) / baseCaseMeanSideInter10 for x in results['+40']["sidenInter50"]])/baseCaseMeanSideInter50}

    rearInter10Sensitivity = meanRearInter10#{"-40": np.mean([(100 * (x - baseCaseMeanRearInter10)) / baseCaseMeanRearInter10 for x in results['-40']["rearEndnInter10"]]), "+40": np.mean([(100 * (x - baseCaseMeanRearInter10)) / baseCaseMeanRearInter10 for x in results['+40']["rearEndnInter10"]])}
    rearInter20Sensitivity = meanRearInter20#{"-40": np.mean([(100 * (x - baseCaseMeanRearInter20)) / baseCaseMeanRearInter20 for x in results['-40']["rearEndnInter20"]]), "+40": np.mean([(100 * (x - baseCaseMeanRearInter20)) / baseCaseMeanRearInter20 for x in results['+40']["rearEndnInter20"]])}
    rearInter50Sensitivity = meanRearInter50#{"-40": np.mean([(100 * (x - baseCaseMeanRearInter50)) / baseCaseMeanRearInter50 for x in results['-40']["rearEndnInter50"]]), "+40": np.mean([(100 * (x - baseCaseMeanRearInter50)) / baseCaseMeanRearInter50 for x in results['+40']["rearEndnInter50"]])}

    rearInter10Sensitivity_std = meanRearInter10_std#{"-40": np.std([(100 * (x - baseCaseMeanRearInter10)) / baseCaseMeanRearInter10 for x in results['-40']["rearEndnInter10"]])/baseCaseMeanRearInter10, "+40": np.std([(100 * (x - baseCaseMeanRearInter10)) / baseCaseMeanRearInter10 for x in results['+40']["rearEndnInter10"]])/baseCaseMeanRearInter10}
    rearInter20Sensitivity_std = meanRearInter20_std#{"-40": np.std([(100 * (x - baseCaseMeanRearInter20)) / baseCaseMeanRearInter20 for x in results['-40']["rearEndnInter20"]])/baseCaseMeanRearInter20, "+40": np.std([(100 * (x - baseCaseMeanRearInter20)) / baseCaseMeanRearInter20 for x in results['+40']["rearEndnInter20"]])/baseCaseMeanRearInter20}
    rearInter50Sensitivity_std = meanRearInter50_std#{"-40": np.std([(100 * (x - baseCaseMeanRearInter50)) / baseCaseMeanRearInter50 for x in results['-40']["rearEndnInter50"]])/baseCaseMeanRearInter50, "+40": np.std([(100 * (x - baseCaseMeanRearInter50)) / baseCaseMeanRearInter50 for x in results['+40']["rearEndnInter50"]])/baseCaseMeanRearInter50}


    sensitivities = {
                    'speedV1Lane2mean':speedV1Lane2mean,
                    'percentageTimeCongestion2Mean':percentageTimeCongestion2Mean,
                    "completedUsers2": completedUSers2_mean,
                    "sidenInter10": sidenInter10Sensitivity,
                    "sidenInter20": sidenInter20Sensitivity,
                    "sidenInter50": sidenInter50Sensitivity,
                    # "sideMinDistance": sideMeanDistance,
                    "rearnInter10": rearInter10Sensitivity,
                    "rearnInter20": rearInter20Sensitivity,
                    "rearnInter50": rearInter50Sensitivity,
                    "sideTTCmin": sideTTCSensitivity,
                    "PETs": petsSensitivity,
                    "rearTTCmin": rearEndTTCSensitivity,
                    # "rearEndMinDistance": rearEndMeanDistance
                     }


    sensitivities_std = {
                      "rearnInter10": rearInter10Sensitivity_std,
                      "rearnInter20": rearInter20Sensitivity_std,
                      "rearnInter50": rearInter50Sensitivity_std,
                        # "rearEndStdDistance": rearEndStdDistance,
                      "sidenInter10": sidenInter10Sensitivity_std,
                      "sidenInter20": sidenInter20Sensitivity_std,
                      "sidenInter50": sidenInter50Sensitivity_std,
                      "sideTTCmin": sideTTCSensitivity_std,
                      "PETs": petsSensitivity_std,
                        # "sideMeanDistance": sideStdDistance,
        "rearTTCmin": rearEndTTCSensitivity_std,
                        # "completedUsers0": completedUsers0_std,
                        # "completedUsers2": completedUsers2_std,
                         # 'percentageTimeCongestion0':percentageTimeCongestion0Std,
                        # 'percentageTimeCongestion2':percentageTimeCongestion2Std,
                        #   'speedV1Lane2std':speedV1Lane2std,
                         }

    toolkit.saveYaml('{}Sensitivities.yml'.format(parameter), sensitivities)
    toolkit.saveYaml('{}Sensitivities_std.yml'.format(parameter), sensitivities_std)

    positiveVariation_std = []
    negativeVariation_std = []

    positiveVariation = []
    negativeVariation = []

    for item in sensitivities:
        negativeVariation.append(sensitivities[item]['-40'])
    for item in sensitivities:
        positiveVariation.append(sensitivities[item]['+40'])

    for item in sensitivities_std:
        negativeVariation_std.append(sensitivities_std[item]['-40'])
    for item in sensitivities_std:
        positiveVariation_std.append(sensitivities_std[item]['+40'])

    infStd = [x for x in negativeVariation_std if ((math.isnan(x) == False) and float('inf') != abs(x))]
    supStd = [x for x in positiveVariation_std if ((math.isnan(x) == False) and float('inf') != abs(x))]

    infMean = [x for x in negativeVariation if ((math.isnan(x) == False) and float('inf') != abs(x))]
    supMean = [x for x in positiveVariation if ((math.isnan(x) == False) and float('inf') != abs(x))]
    return infMean, supMean, infStd, supStd, sensitivities, values


def getTornadoCharts(parameter):

    if parameter == 'dn':
        param = r"$\mu_{d}$"
    elif parameter == 'headway':
        param = r"$1/\lambda}$"
    elif parameter == 'tau':
        param = r"$\mu_{\tau}$"
    elif parameter == "speed":
        param = r"$\mu_{v_{f}}$"
    elif parameter == "length":
        param = r"$\mu_{l}$"
    elif parameter == 'criticalGap':
        param = r"$\mu_{g}$"

    x1 = ['$\overline{TTC}_{min}^{arrière}$', '$\overline{TTC}_{min}^{latéral}$', '$\overline{PET}$']#, 'rear end $\overline{nInter}_{10}$', 'rear end $\overline{nInter}_{20}$', 'rear end $\overline{nInter}_{50}$', 'side $\overline{nInter}_{10}$', 'side $\overline{nInter}_{20}$', 'side $\overline{nInter}_{50}$', r'$\overline{nUsers}_{2}^{completed}$', r'$\overline{t_{2}}^{\%congested}$', r'$\overline{v}$']# 'timePecentageInCongestedState2']
    x2 = ['$\overline{nInter}^{arrière}_{10}$', '$\overline{nInter}^{arrière}_{20}$', '$\overline{nInter}^{arrière}_{50}$', '$\overline{nInter}^{latéral}_{10}$', '$\overline{nInter}^{latéral}_{20}$', '$\overline{nInter}^{latéral}_{50}$']#, r'$\overline{nUsers}_{2}^{completed}$', r'$\overline{t_{2}}^{\%congested}$', r'$\overline{v}$']# 'timePecentageInCongestedState2']

    negativeVariation, positiveVariation, negErr, posErr, _, _ = getSensivities(parameter)

    fig = plt.figure(figsize=(10,8))
    redPatch = mpatches.Patch(color='red', label=param+"+40%")
    bluePatch = mpatches.Patch(color='blue', label=param+"-40%")

    fig.legend(handles=[redPatch, bluePatch])
    #
    ax = plt.subplot(1,2,1)
    ax.barh(x1, negativeVariation[0:3], color='None', align='edge', height=.8, edgecolor='b',  xerr=negErr[0:3], error_kw=dict(ecolor='blue', capsize=3))
    ax.barh(x1, positiveVariation[0:3], color='None', align='edge', height=.8, edgecolor='r',  xerr=posErr[0:3], error_kw=dict(ecolor='red', capsize=3))

    x_pos = [i+.4 for i in range(0, len(x1))]
    plt.yticks(np.arange(0, len(x1), step=1), x1)
    plt.xlabel('Pourcentage de variation (%)')
    # plt.tight_layout()
    plt.plot([0,0], [0,len(x1)], color='black')

    ax = plt.subplot(1,2,2)
    ax.barh(x2, negativeVariation[3:], color='None', align='edge', height=.8, edgecolor='b', xerr=negErr[3:], error_kw=dict(ecolor='blue', capsize=3))
    ax.barh(x2, positiveVariation[3:], color='None', align='edge', height=.8, edgecolor='r', xerr=posErr[3:], error_kw=dict(ecolor='red', capsize=3))

    # plt.legend(loc='lower left')
    x_pos = [i+.4 for i in range(0, len(x2))]
    plt.yticks(np.arange(0, len(x2), step=1), x2)
    plt.xlabel('Pourcentage de variation (%)')
    # plt.tight_layout()
    plt.plot([0,0], [0,len(x2)], color='black')
    #
    plt.savefig('tornado-sa-{}.pdf'.format(parameter))
    plt.close('all')


def getHeatmaps():


    x = [r"$\mu_{\tau}$", "$\mu_{d}$", '$1/\lambda$', "$\mu_{v_{f}}$", "$\mu_{l}$", "$\mu_{g}$"]
    y = ['$\overline{nInter}^{latéral}_{10}$', '$\overline{nInter}^{latéral}_{20}$', '$\overline{nInter}^{latéral}_{50}$', '$\overline{TTC}_{min}^{latéral}$', '$\overline{PET}$', '$\overline{nInter}^{arrière}_{10}$', '$\overline{nInter}^{arrière}_{20}$', '$\overline{nInter}^{arrière}_{50}$', '$\overline{TTC}_{min}^{arrière}$']

    posVar = []
    negVar = []
    parameters = ['tau', 'dn', 'headway', 'speed', 'length', 'criticalGap']
    for param in parameters:
        neg, pos, _, _, _, _= getSensivities(param)
        posVar.append(pos[3:])
        negVar.append(neg[3:])

    dataPos = pd.DataFrame(posVar, index=x, columns=y) .transpose()
    dataNeg = pd.DataFrame(negVar, index=x, columns=y).transpose()

    myCmap = sns.diverging_palette(h_neg=240, h_pos=10, as_cmap=True)
    fig = plt.figure(figsize=(18,12))
    plt.subplot(1, 2, 1)

    sns.heatmap(dataNeg, cmap=myCmap, center=0.00, linewidths=.9, vmin=min(min(toolkit.flatten(negVar)), min(toolkit.flatten(posVar))), vmax=max(max(toolkit.flatten(negVar)), max(toolkit.flatten(posVar))), cbar=False)
    plt.rc('xtick')
    plt.rc('ytick')
    plt.yticks(rotation=0)#, fontsize=18)
    plt.title('Variation des paramètres de -40%')#, fontsize=18)
    plt.xticks(rotation=0)#, fontsize=18)

    plt.subplot(1,2,2)

    sns.set(font_scale=2)
    sns.heatmap(dataPos, cmap=myCmap, center=0.00, linewidths=.9, vmin=min(min(toolkit.flatten(negVar)), min(toolkit.flatten(posVar))), vmax=max(max(toolkit.flatten(negVar)), max(toolkit.flatten(posVar))), yticklabels=False, cbar_kws={'label': 'Variation des indicateurs (%)', 'ticks':[k for k in range(-33, 180, 30)]})

    plt.rc('xtick')
    plt.rc('ytick')
    plt.xticks(rotation=0)#, fontsize=10)

    plt.title('Variation des paramètres de +40%')#, fontsize=16)

    plt.savefig('sa-heatmap.pdf')
    plt.close()


def getCDF(parameter, normed):
    baseCaseResults = toolkit.loadYaml('sorties/00base-case-results.yml')
    results = {"-40": {"minTTCs": toolkit.loadYaml('sorties/sa-minTTCs-{}-0.4.yml'.format(parameter)),
                       "PETs": toolkit.loadYaml('sorties/sa-PETs-{}-0.4.yml'.format(parameter)),
                       "nInter10": toolkit.loadYaml('sorties/sa-nInter10{}-0.4.yml'.format(parameter)),
                       "nInter20": toolkit.loadYaml('sorties/sa-nInter20{}-0.4.yml'.format(parameter)),
                       "nInter50": toolkit.loadYaml('sorties/sa-nInter50{}-0.4.yml'.format(parameter)),
                       "sidenInter10": toolkit.loadYaml('sorties/sa-side-nInter10-{}-0.4.yml'.format(parameter)),
                       "sidenInter20": toolkit.loadYaml('sorties/sa-side-nInter20-{}-0.4.yml'.format(parameter)),
                       "sidenInter50": toolkit.loadYaml('sorties/sa-side-nInter50-{}-0.4.yml'.format(parameter)),
                       "rearEndnInter10": toolkit.loadYaml('sorties/sa-rearEnd-nInter10-{}-0.4.yml'.format(parameter)),
                       "rearEndnInter20": toolkit.loadYaml('sorties/sa-rearEnd-nInter20-{}-0.4.yml'.format(parameter)),
                       "rearEndnInter50": toolkit.loadYaml('sorties/sa-rearEnd-nInter50-{}-0.4.yml'.format(parameter)),
                       "completedUser0": toolkit.loadYaml('sorties/numberOfUsers0-{}-0.4.yml'.format(parameter))[parameter][-.4],
                       "completedUSers2": toolkit.loadYaml('sorties/numberOfUsers2-{}-0.4.yml'.format(parameter))[parameter][-.4],
                       "minDistances": toolkit.loadYaml('sorties/sa-minDistances-{}-0.4.yml'.format(parameter))

                       },

               "+40": {"minTTCs": toolkit.loadYaml('sorties/sa-minTTCs-{}0.4.yml'.format(parameter)),
                       "PETs": toolkit.loadYaml('sorties/sa-PETs-{}0.4.yml'.format(parameter)),
                       "nInter10": toolkit.loadYaml('sorties/sa-nInter10{}0.4.yml'.format(parameter)),
                       "nInter20": toolkit.loadYaml('sorties/sa-nInter20{}0.4.yml'.format(parameter)),
                       "nInter50": toolkit.loadYaml('sorties/sa-nInter50{}0.4.yml'.format(parameter)),
                       "sidenInter10": toolkit.loadYaml('sorties/sa-side-nInter10-{}0.4.yml'.format(parameter)),
                       "sidenInter20": toolkit.loadYaml('sorties/sa-side-nInter20-{}0.4.yml'.format(parameter)),
                       "sidenInter50": toolkit.loadYaml('sorties/sa-side-nInter50-{}0.4.yml'.format(parameter)),
                       "rearEndnInter10": toolkit.loadYaml('sorties/sa-rearEnd-nInter10-{}0.4.yml'.format(parameter)),
                       "rearEndnInter20": toolkit.loadYaml('sorties/sa-rearEnd-nInter20-{}0.4.yml'.format(parameter)),
                       "rearEndnInter50": toolkit.loadYaml('sorties/sa-rearEnd-nInter50-{}0.4.yml'.format(parameter)),
                       "completedUser0": toolkit.loadYaml('sorties/numberOfUsers0-{}0.4.yml'.format(parameter))[parameter][.4],
                       "completedUSers2": toolkit.loadYaml('sorties/numberOfUsers2-{}0.4.yml'.format(parameter))[parameter][.4],
                       "minDistances": toolkit.loadYaml('sorties/sa-minDistances-{}0.4.yml'.format(parameter))

                       }}

    if parameter == 'dn':
        param = r"$\mu_{d}$"
    elif parameter == 'headway':
        param = r"$1/\lambda}$"
    elif parameter == 'tau':
        param = r"$\mu_{\tau}$"
    elif parameter == "speed":
        param = r"$\mu_{v_{f}}$"
    elif parameter == "length":
        param = r"$\mu_{l}$"
    elif parameter == 'criticalGap':
        param = r"$\mu_{g}$"


    ####### PETS #######

    posVarX = results['+40']["PETs"]
    negVarX = results['-40']["PETs"]
    baseCaseX = baseCaseResults["PETs"]

    sorted_dataPos = np.sort(posVarX)
    sorted_dataNeg = np.sort(negVarX)
    sorted_dataBC = np.sort(baseCaseX)

    if not normed:
        yvalsPos = np.arange(len(sorted_dataPos))
        yvalsNeg = np.arange(len(sorted_dataNeg))
        yvalsBC = np.arange(len(sorted_dataBC))
    else:
        yvalsPos = np.arange(len(sorted_dataPos)) / float(len(sorted_dataPos) - 1)
        yvalsNeg = np.arange(len(sorted_dataNeg)) / float(len(sorted_dataNeg) - 1)
        yvalsBC = np.arange(len(sorted_dataBC)) / float(len(sorted_dataBC) - 1)

    fig = plt.figure(figsize=(12,14))

    plt.subplot(3, 2, 1)
    plt.plot(sorted_dataPos, yvalsPos,  label=str(param)+"+40%", color='r')
    plt.plot(sorted_dataNeg, yvalsNeg, label=str(param)+"-40%", color='b')
    plt.plot(sorted_dataBC, yvalsBC, label="cas de référence", color='grey')
    plt.legend(loc='lower right')
    plt.xlabel('PET(s)')

    if not normed:
        plt.ylabel("Nombre d'observations cumulées")
    else:
        plt.ylabel('Fréquences cumulées')


    ax1 = plt.subplot(3, 2, 2)
    subx1 = [k for k in sorted_dataPos if k <= .5]
    subx2 = [k for k in sorted_dataNeg if k <= .5]
    subx3 = [k for k in sorted_dataBC if k <= .5]
    plt.plot(subx1, yvalsPos[0:len(subx1)],  label=str(param)+"+40%", color='r')
    plt.plot(subx2, yvalsNeg[0:len(subx2)], label=str(param)+"-40%", color='b')
    plt.plot(subx3, yvalsBC[0:len(subx3)], label="cas de référence", color='grey')
    plt.xlabel('PET(s)')
    plt.title('Zoom entre 0 and 0.5s')

    plt.legend(loc='lower right')

    n = len(posVarX)
    supBorn = []
    epsilon = math.sqrt(np.log(2/.05)/(2*n))
    for k in yvalsPos[0:len(subx1)]:
        if k + epsilon > 1:
            supBorn.append(1)
        else:
            supBorn.append(k + epsilon)

    infBorn = []
    for k in yvalsPos[0:len(subx1)]:
        if k - epsilon < 0:
            infBorn.append(0)
        else:
            infBorn.append(k - epsilon)

    plt.fill_between(subx1, y1=yvalsPos[0:len(subx1)], y2=supBorn, color='r', alpha=.2)
    plt.fill_between(subx1, y1=yvalsPos[0:len(subx1)], y2=infBorn, color='r', alpha=.2)

    n = len(negVarX)
    supBorn = []
    epsilon = math.sqrt(np.log(2/.05)/(2*n))
    for k in yvalsNeg[0:len(subx2)]:
        if k + epsilon > 1:
            supBorn.append(1)
        else:
            supBorn.append(k + epsilon)

    infBorn = []
    for k in yvalsNeg[0:len(subx2)]:
        if k - epsilon < 0:
            infBorn.append(0)
        else:
            infBorn.append(k - epsilon)

    plt.fill_between(subx2, y1=yvalsNeg[0:len(subx2)], y2=supBorn, color='b', alpha=.2)
    plt.fill_between(subx2, y1=yvalsNeg[0:len(subx2)], y2=infBorn, color='b', alpha=.2)

    n = len(baseCaseX)
    supBorn = []
    epsilon = math.sqrt(np.log(2/.05)/(2*n))
    for k in yvalsBC[0:len(subx3)]:
        if k + epsilon > 1:
            supBorn.append(1)
        else:
            supBorn.append(k + epsilon)

    infBorn = []
    for k in yvalsBC[0:len(subx3)]:
        if k - epsilon < 0:
            infBorn.append(0)
        else:
            infBorn.append(k - epsilon)
    plt.fill_between(subx3, y1=yvalsBC[0:len(subx3)], y2=supBorn, color='grey', alpha=.2)
    plt.fill_between(subx3, y1=yvalsBC[0:len(subx3)], y2=infBorn, color='grey', alpha=.2)


    ####### side TTC #######
    posVarX = results['+40']["minTTCs"][2]
    negVarX = results['-40']["minTTCs"][2]
    baseCaseX = baseCaseResults["minTTCs"][2]

    sorted_dataPos = np.sort(posVarX)
    sorted_dataNeg = np.sort(negVarX)
    sorted_dataBC = np.sort(baseCaseX)

    if not normed:
        yvalsPos = np.arange(len(sorted_dataPos))
        yvalsNeg = np.arange(len(sorted_dataNeg))
        yvalsBC = np.arange(len(sorted_dataBC))
    else:
        yvalsPos = np.arange(len(sorted_dataPos)) / float(len(sorted_dataPos) - 1)
        yvalsNeg = np.arange(len(sorted_dataNeg)) / float(len(sorted_dataNeg) - 1)
        yvalsBC = np.arange(len(sorted_dataBC)) / float(len(sorted_dataBC) - 1)


    plt.subplot(3, 2, 3)
    plt.plot(sorted_dataPos, yvalsPos,  label=str(param)+"+40%", color='r')
    plt.plot(sorted_dataNeg, yvalsNeg, label=str(param)+"-40%", color='b')
    plt.plot(sorted_dataBC, yvalsBC, label="cas de référence", color='grey')
    plt.legend(loc='lower right')
    plt.xlabel('$TTC_{min}^{latéral}$ (s)')

    if not normed:
        plt.ylabel("Nombre d'observations cumulées")
    else:
        plt.ylabel('Fréquences cumulées')
    ax2 = plt.subplot(3, 2, 4, sharex=ax1)
    subx1 = [k for k in sorted_dataPos if k <= .5]
    subx2 = [k for k in sorted_dataNeg if k <= .5]
    subx3 = [k for k in sorted_dataBC if k <= .5]
    plt.plot(subx1, yvalsPos[0:len(subx1)],  label=str(param)+"+40%", color='r')
    plt.plot(subx2, yvalsNeg[0:len(subx2)], label=str(param)+"-40%", color='b')
    plt.plot(subx3, yvalsBC[0:len(subx3)], label="cas de référence", color='grey')
    plt.xlabel('$TTC_{min}^{latéral}$ (s)')
    plt.legend(loc='lower right')

    n = len(posVarX)
    supBorn = []
    epsilon = math.sqrt(np.log(2/.05)/(2*n))
    for k in yvalsPos[0:len(subx1)]:
        if k + epsilon > 1:
            supBorn.append(1)
        else:
            supBorn.append(k + epsilon)

    infBorn = []
    for k in yvalsPos[0:len(subx1)]:
        if k - epsilon < 0:
            infBorn.append(0)
        else:
            infBorn.append(k - epsilon)

    plt.fill_between(subx1, y1=yvalsPos[0:len(subx1)], y2=supBorn, color='r', alpha=.2)
    plt.fill_between(subx1, y1=yvalsPos[0:len(subx1)], y2=infBorn, color='r', alpha=.2)

    n = len(negVarX)
    supBorn = []
    epsilon = math.sqrt(np.log(2/.05)/(2*n))
    for k in yvalsNeg[0:len(subx2)]:
        if k + epsilon > 1:
            supBorn.append(1)
        else:
            supBorn.append(k + epsilon)

    infBorn = []
    for k in yvalsNeg[0:len(subx2)]:
        if k - epsilon < 0:
            infBorn.append(0)
        else:
            infBorn.append(k - epsilon)

    plt.fill_between(subx2, y1=yvalsNeg[0:len(subx2)], y2=supBorn, color='b', alpha=.2)
    plt.fill_between(subx2, y1=yvalsNeg[0:len(subx2)], y2=infBorn, color='b', alpha=.2)

    n = len(baseCaseX)
    supBorn = []
    epsilon = math.sqrt(np.log(2/.05)/(2*n))
    for k in yvalsBC[0:len(subx3)]:
        if k + epsilon > 1:
            supBorn.append(1)
        else:
            supBorn.append(k + epsilon)

    infBorn = []
    for k in yvalsBC[0:len(subx3)]:
        if k - epsilon < 0:
            infBorn.append(0)
        else:
            infBorn.append(k - epsilon)
    plt.fill_between(subx3, y1=yvalsBC[0:len(subx3)], y2=supBorn, color='grey', alpha=.2)
    plt.fill_between(subx3, y1=yvalsBC[0:len(subx3)], y2=infBorn, color='grey', alpha=.2)


    ####### rear end TTC #######

    posVarX = results['+40']["minTTCs"][1]
    negVarX = results['-40']["minTTCs"][1]
    baseCaseX = baseCaseResults["minTTCs"][1]

    sorted_dataPos = np.sort(posVarX)
    sorted_dataNeg = np.sort(negVarX)
    sorted_dataBC = np.sort(baseCaseX)

    if not normed:
        yvalsPos = np.arange(len(sorted_dataPos))
        yvalsNeg = np.arange(len(sorted_dataNeg))
        yvalsBC = np.arange(len(sorted_dataBC))
    else:
        yvalsPos = np.arange(len(sorted_dataPos)) / float(len(sorted_dataPos) - 1)
        yvalsNeg = np.arange(len(sorted_dataNeg)) / float(len(sorted_dataNeg) - 1)
        yvalsBC = np.arange(len(sorted_dataBC)) / float(len(sorted_dataBC) - 1)

    plt.subplot(3, 2, 5)
    plt.plot(sorted_dataPos, yvalsPos,  label=str(param)+"+40%", color='r')
    plt.plot(sorted_dataNeg, yvalsNeg, label=str(param)+"-40%", color='b')
    plt.plot(sorted_dataBC, yvalsBC, label="cas de référence", color='grey')
    plt.legend(loc='lower right')
    plt.xlabel('$TTC_{min}^{arrière}$ (s)')

    if not normed:
        plt.ylabel("Nombre d'observations cumulées")
    else:
        plt.ylabel('Fréquences cumulées')
    ax3 = plt.subplot(3, 2, 6, sharex=ax1)
    subx1 = [k for k in sorted_dataPos if k <= .5]
    subx2 = [k for k in sorted_dataNeg if k <= .5]
    subx3 = [k for k in sorted_dataBC if k <= .5]
    plt.plot(subx1, yvalsPos[0:len(subx1)],  label=str(param)+"+40%", color='r')
    plt.plot(subx2, yvalsNeg[0:len(subx2)], label=str(param)+"-40%", color='b')
    plt.plot(subx3, yvalsBC[0:len(subx3)], label="cas de référence", color='grey')
    plt.xlabel('$TTC_{min}^{arrière}$ (s)')
    plt.legend(loc='lower right')

    n = len(posVarX)
    supBorn = []
    epsilon = math.sqrt(np.log(2/.05)/(2*n))
    for k in yvalsPos[0:len(subx1)]:
        if k + epsilon > 1:
            supBorn.append(1)
        else:
            supBorn.append(k + epsilon)

    infBorn = []
    for k in yvalsPos[0:len(subx1)]:
        if k - epsilon < 0:
            infBorn.append(0)
        else:
            infBorn.append(k - epsilon)

    plt.fill_between(subx1, y1=yvalsPos[0:len(subx1)], y2=supBorn, color='r', alpha=.2)
    plt.fill_between(subx1, y1=yvalsPos[0:len(subx1)], y2=infBorn, color='r', alpha=.2)

    n = len(negVarX)
    supBorn = []
    epsilon = math.sqrt(np.log(2/.05)/(2*n))
    for k in yvalsNeg[0:len(subx2)]:
        if k + epsilon > 1:
            supBorn.append(1)
        else:
            supBorn.append(k + epsilon)

    infBorn = []
    for k in yvalsNeg[0:len(subx2)]:
        if k - epsilon < 0:
            infBorn.append(0)
        else:
            infBorn.append(k - epsilon)

    plt.fill_between(subx2, y1=yvalsNeg[0:len(subx2)], y2=supBorn, color='b', alpha=.2)
    plt.fill_between(subx2, y1=yvalsNeg[0:len(subx2)], y2=infBorn, color='b', alpha=.2)

    n = len(baseCaseX)
    supBorn = []
    epsilon = math.sqrt(np.log(2/.05)/(2*n))
    for k in yvalsBC[0:len(subx3)]:
        if k + epsilon > 1:
            supBorn.append(1)
        else:
            supBorn.append(k + epsilon)

    infBorn = []
    for k in yvalsBC[0:len(subx3)]:
        if k - epsilon < 0:
            infBorn.append(0)
        else:
            infBorn.append(k - epsilon)
    plt.fill_between(subx3, y1=yvalsBC[0:len(subx3)], y2=supBorn, color='grey', alpha=.2)
    plt.fill_between(subx3, y1=yvalsBC[0:len(subx3)], y2=infBorn, color='grey', alpha=.2)

    # plt.show()
    plt.savefig('sa-stacked-cdf{}{}.pdf'.format(parameter, normed))

    plt.close()

    # min Distances - rearEnd
    plt.figure(figsize=(10,12))

    posVarX = results['+40']["minDistances"][1]
    negVarX = results['-40']["minDistances"][1]
    baseCaseX = baseCaseResults["minDistances"][1]

    sorted_dataPos = np.sort(posVarX)
    sorted_dataNeg = np.sort(negVarX)
    sorted_dataBC = np.sort(baseCaseX)

    if not normed:
        yvalsPos = np.arange(len(sorted_dataPos))
        yvalsNeg = np.arange(len(sorted_dataNeg))
        yvalsBC = np.arange(len(sorted_dataBC))
    else:
        yvalsPos = np.arange(len(sorted_dataPos)) / float(len(sorted_dataPos) - 1)
        yvalsNeg = np.arange(len(sorted_dataNeg)) / float(len(sorted_dataNeg) - 1)
        yvalsBC = np.arange(len(sorted_dataBC)) / float(len(sorted_dataBC) - 1)

    plt.subplot(2, 2, 1)
    plt.plot(sorted_dataPos, yvalsPos,  label=str(param)+"+40%", color='r')
    plt.plot(sorted_dataNeg, yvalsNeg, label=str(param)+"-40%", color='b')
    plt.plot(sorted_dataBC, yvalsBC, label="cas de référence", color='grey')
    plt.legend(loc='lower right')
    plt.xlabel('$D_{min}^{arrière}$ (m)')

    if not normed:
        plt.ylabel("Nombre d'observations cumulées")
    else:
        plt.ylabel('Fréquences cumulées')
    plt.subplot(2, 2, 2)
    subx1 = [k for k in sorted_dataPos if k <= 10]
    subx2 = [k for k in sorted_dataNeg if k <= 10]
    subx3 = [k for k in sorted_dataBC if k <= 10]
    plt.plot(subx1, yvalsPos[0:len(subx1)],  label=str(param)+"+40%", color='r')
    plt.plot(subx2, yvalsNeg[0:len(subx2)], label=str(param)+"-40%", color='b')
    plt.plot(subx3, yvalsBC[0:len(subx3)], label="cas de référence", color='grey')
    plt.xlabel('$D_{min}^{arrière}$ (m)')
    plt.legend(loc='lower right')

    # min Distances - side

    posVarX = results['+40']["minDistances"][2]
    negVarX = results['-40']["minDistances"][2]
    baseCaseX = baseCaseResults["minDistances"][2]

    sorted_dataPos = np.sort(posVarX)
    sorted_dataNeg = np.sort(negVarX)
    sorted_dataBC = np.sort(baseCaseX)

    if not normed:
        yvalsPos = np.arange(len(sorted_dataPos))
        yvalsNeg = np.arange(len(sorted_dataNeg))
        yvalsBC = np.arange(len(sorted_dataBC))
    else:
        yvalsPos = np.arange(len(sorted_dataPos)) / float(len(sorted_dataPos) - 1)
        yvalsNeg = np.arange(len(sorted_dataNeg)) / float(len(sorted_dataNeg) - 1)
        yvalsBC = np.arange(len(sorted_dataBC)) / float(len(sorted_dataBC) - 1)

    plt.subplot(2, 2, 3)
    plt.plot(sorted_dataPos, yvalsPos, label=str(param) + "+40%", color='r')
    plt.plot(sorted_dataNeg, yvalsNeg, label=str(param) + "-40%", color='b')
    plt.plot(sorted_dataBC, yvalsBC, label="cas de référence", color='grey')
    plt.legend(loc='lower right')
    plt.xlabel('$D_{min}^{latéral}$ (m)')

    if not normed:
        plt.ylabel("Nombre d'observations cumulées")
    else:
        plt.ylabel('Fréquences cumulées')
    plt.subplot(2, 2, 4)
    subx1 = [k for k in sorted_dataPos if k <= 10]
    subx2 = [k for k in sorted_dataNeg if k <= 10]
    subx3 = [k for k in sorted_dataBC if k <= 10]
    subx3 = [k for k in sorted_dataBC if k <= 10]
    plt.plot(subx1, yvalsPos[0:len(subx1)], label=str(param) + "+40%", color='r')
    plt.plot(subx2, yvalsNeg[0:len(subx2)], label=str(param) + "-40%", color='b')
    plt.plot(subx3, yvalsBC[0:len(subx3)], label="cas de référence", color='grey')
    plt.xlabel('$D_{min}^{latéral}$ (m)')
    plt.legend(loc='lower right')


    plt.savefig('sa-stacked-suite-cdf{}{}.pdf'.format(parameter, normed))

    plt.close('all')


def getTornadoCDF(parameter, normed):
    results = {"-40": {"minTTCs": toolkit.loadYaml('sorties/sa-minTTCs-{}-0.4.yml'.format(parameter)),
                        "PETs": toolkit.loadYaml('sorties/sa-PETs-{}-0.4.yml'.format(parameter)),
                        # "nInter10": toolkit.loadYaml('sorties/sa-nInter10{}-0.4.yml'.format(parameter)),
                        # "nInter20":toolkit.loadYaml('sorties/sa-nInter20{}-0.4.yml'.format(parameter)),
                        # "nInter50":toolkit.loadYaml('sorties/sa-nInter50{}-0.4.yml'.format(parameter)),
                        "sidenInter10": toolkit.loadYaml('sorties/sa-side-nInter10-{}-0.4.yml'.format(parameter)),
                        "sidenInter20": toolkit.loadYaml('sorties/sa-side-nInter20-{}-0.4.yml'.format(parameter)),
                        "sidenInter50": toolkit.loadYaml('sorties/sa-side-nInter50-{}-0.4.yml'.format(parameter)),
                        "rearEndnInter10": toolkit.loadYaml('sorties/sa-rearEnd-nInter10-{}-0.4.yml'.format(parameter)),
                        "rearEndnInter20": toolkit.loadYaml('sorties/sa-rearEnd-nInter20-{}-0.4.yml'.format(parameter)),
                        "rearEndnInter50": toolkit.loadYaml('sorties/sa-rearEnd-nInter50-{}-0.4.yml'.format(parameter)),
                        "completedUser0":  toolkit.loadYaml('sorties/numberOfUsers0-{}-0.4.yml'.format(parameter))[parameter][-.4],
                        "completedUSers2": toolkit.loadYaml('sorties/numberOfUsers2-{}-0.4.yml'.format(parameter))[parameter][-.4],
                        "timePercentageCongestion2Mean":  toolkit.loadYaml('sorties/sa-meanTimePercentageCongestion-{}.yml'.format(parameter))[parameter][-.4],
                        'speedV1Lane2': toolkit.loadYaml('sorties/sa-meanSpeedV1Lane2{}.yml'.format(parameter))[parameter][-.4],
                        'minDistances':toolkit.loadYaml('sorties/sa-minDistances-{}-0.4.yml'.format(parameter)),
                        'speedDifferential' : [-k for k in toolkit.loadYaml('sorties/sa-speedDifferentials-{}.yml'.format(parameter))[parameter][-.4]]

    },

                 "+40": {"minTTCs": toolkit.loadYaml('sorties/sa-minTTCs-{}0.4.yml'.format(parameter)),
                        "PETs": toolkit.loadYaml('sorties/sa-PETs-{}0.4.yml'.format(parameter)),
                        # "nInter10":toolkit.loadYaml('sorties/sa-nInter10{}0.4.yml'.format(parameter)),
                        # "nInter20":toolkit.loadYaml('sorties/sa-nInter20{}0.4.yml'.format(parameter)),
                        # "nInter50":toolkit.loadYaml('sorties/sa-nInter50{}0.4.yml'.format(parameter)),
                        "sidenInter10": toolkit.loadYaml('sorties/sa-side-nInter10-{}0.4.yml'.format(parameter)),
                        "sidenInter20": toolkit.loadYaml('sorties/sa-side-nInter20-{}0.4.yml'.format(parameter)),
                        "sidenInter50": toolkit.loadYaml('sorties/sa-side-nInter50-{}0.4.yml'.format(parameter)),
                        "rearEndnInter10": toolkit.loadYaml('sorties/sa-rearEnd-nInter10-{}0.4.yml'.format(parameter)),
                        "rearEndnInter20": toolkit.loadYaml('sorties/sa-rearEnd-nInter20-{}0.4.yml'.format(parameter)),
                        "rearEndnInter50": toolkit.loadYaml('sorties/sa-rearEnd-nInter50-{}0.4.yml'.format(parameter)),
                        "completedUser0":toolkit.loadYaml('sorties/numberOfUsers0-{}0.4.yml'.format(parameter))[parameter][.4],
                        "completedUSers2":toolkit.loadYaml('sorties/numberOfUsers2-{}0.4.yml'.format(parameter))[parameter][.4],
                        "timePercentageCongestion2Mean": toolkit.loadYaml('sorties/sa-meanTimePercentageCongestion-{}.yml'.format(parameter))[parameter][.4],
                        'speedV1Lane2': toolkit.loadYaml('sorties/sa-meanSpeedV1Lane2{}.yml'.format(parameter))[parameter][.4],
                        'minDistances': toolkit.loadYaml('sorties/sa-minDistances-{}0.4.yml'.format(parameter)),
                        'speedDifferential': [-k for k in toolkit.loadYaml('sorties/sa-speedDifferentials-{}.yml'.format(parameter))[parameter][.4]]

                         }
               }

    if parameter == 'dn':
        param = r"$\mu_{d}$"
    elif parameter == 'headway':
        param = r"$1/\lambda}$"
    elif parameter == 'tau':
        param = r"$\mu_{\tau}$"
    elif parameter == "speed":
        param = r"$\mu_{v_{f}}$"
    elif parameter == "length":
        param = r"$\mu_{l}$"
    elif parameter == 'criticalGap':
        param = r"$\mu_g$"

    fig = plt.figure(figsize=(12,9))

    redPatch = mpatches.Patch(color='red', label=param+"+40%")
    greyPatch = mpatches.Patch(color='grey', label="cas de référence")
    bluePatch = mpatches.Patch(color='blue', label=param+"-40%")

    fig.legend(handles=[redPatch, greyPatch, bluePatch], loc='upper left')

    ax1 = plt.subplot2grid((4, 2), (0, 0), rowspan=4)
    ax2 = plt.subplot2grid((4, 2), (0, 1), colspan=1, rowspan=1)
    ax3 = plt.subplot2grid((4, 2), (1, 1), rowspan=1, colspan=1)
    ax4 = plt.subplot2grid((4, 2), (2, 1), colspan=1, rowspan=1)
    ax5 = plt.subplot2grid((4, 2), (3, 1), colspan=2, rowspan=1)

    x1 = ['$\overline{TTC}_{min}^{latéral}$', '$\overline{PET}$', '$\overline{TTC}_{min}^{arrière}$', ]#, 'rear end $\overline{nInter}_{10}$', 'rear end $\overline{nInter}_{20}$', 'rear end $\overline{nInter}_{50}$', 'side $\overline{nInter}_{10}$', 'side $\overline{nInter}_{20}$', 'side $\overline{nInter}_{50}$', r'$\overline{nUsers}_{2}^{completed}$', r'$\overline{t_{2}}^{\%congested}$', r'$\overline{v}$']# 'timePecentageInCongestedState2']

    negativeVariation, positiveVariation, negErr, posErr, _, _ = getSensivities(parameter)

    ax1.barh(x1, negativeVariation[-3:], color='None', align='center', height=.8, edgecolor='b',  xerr=negErr[-3:], error_kw=dict(ecolor='blue', capsize=3), tick_label=x1)
    ax1.barh(x1, positiveVariation[-3:], color='None', align='center', height=.8, edgecolor='r',  xerr=posErr[-3:], error_kw=dict(ecolor='red', capsize=3), tick_label=x1)
    # x_pos = [k +.4 for k in np.arange(3)]
    # ax1.set_yticks(x_pos, x1)
    ax1.set_xlabel('Pourcentage de variation (%)')
    plt.tight_layout(pad=0.8, w_pad=0.5, h_pad=1.5)
    ax1.plot([0,0], [0,len(x1)], color='black')

    posVarX = results['+40']["PETs"]
    negVarX = results['-40']["PETs"]
    baseCaseX = baseCaseResults["PETs"]

    sorted_dataPos = np.sort(posVarX)
    sorted_dataNeg = np.sort(negVarX)
    sorted_dataBC = np.sort(baseCaseX)

    if not normed:
        yvalsPos = np.arange(len(sorted_dataPos))
        yvalsNeg = np.arange(len(sorted_dataNeg))
        yvalsBC = np.arange(len(sorted_dataBC))
    else:
        yvalsPos = np.arange(len(sorted_dataPos)) / float(len(sorted_dataPos) - 1)
        yvalsNeg = np.arange(len(sorted_dataNeg)) / float(len(sorted_dataNeg) - 1)
        yvalsBC = np.arange(len(sorted_dataBC)) / float(len(sorted_dataBC) - 1)

    ax2.plot(sorted_dataPos, yvalsPos,  label=str(param)+"+40%", color='r')
    ax2.plot(sorted_dataNeg, yvalsNeg, label=str(param)+"-40%", color='b')
    ax2.plot(sorted_dataBC, yvalsBC, label="cas de référence", color='grey')
    # plt.legend(loc='lower right')
    ax2.set_xlabel('PET(s)')

    posVarX = results['+40']["minTTCs"][1]
    negVarX = results['-40']["minTTCs"][1]
    baseCaseX = baseCaseResults["minTTCs"][1]

    sorted_dataPos = np.sort(posVarX)
    sorted_dataNeg = np.sort(negVarX)
    sorted_dataBC = np.sort(baseCaseX)

    if not normed:
        yvalsPos = np.arange(len(sorted_dataPos))
        yvalsNeg = np.arange(len(sorted_dataNeg))
        yvalsBC = np.arange(len(sorted_dataBC))
    else:
        yvalsPos = np.arange(len(sorted_dataPos)) / float(len(sorted_dataPos) - 1)
        yvalsNeg = np.arange(len(sorted_dataNeg)) / float(len(sorted_dataNeg) - 1)
        yvalsBC = np.arange(len(sorted_dataBC)) / float(len(sorted_dataBC) - 1)

    ax4.plot(sorted_dataPos, yvalsPos,  label=str(param)+"+40%", color='r')
    ax4.plot(sorted_dataNeg, yvalsNeg, label=str(param)+"-40%", color='b')
    ax4.plot(sorted_dataBC, yvalsBC, label="cas de référence", color='grey')
    # plt.legend(loc='lower right')
    ax4.set_xlabel('$TTC_{min}^{arrière}$ (s)')

    posVarX = results['+40']["minTTCs"][2]
    negVarX = results['-40']["minTTCs"][2]
    baseCaseX = baseCaseResults["minTTCs"][2]

    sorted_dataPos = np.sort(posVarX)
    sorted_dataNeg = np.sort(negVarX)
    sorted_dataBC = np.sort(baseCaseX)

    if not normed:
        yvalsPos = np.arange(len(sorted_dataPos))
        yvalsNeg = np.arange(len(sorted_dataNeg))
        yvalsBC = np.arange(len(sorted_dataBC))
    else:
        yvalsPos = np.arange(len(sorted_dataPos)) / float(len(sorted_dataPos) - 1)
        yvalsNeg = np.arange(len(sorted_dataNeg)) / float(len(sorted_dataNeg) - 1)
        yvalsBC = np.arange(len(sorted_dataBC)) / float(len(sorted_dataBC) - 1)


    ax3.plot(sorted_dataPos, yvalsPos,  label=str(param)+"+40%", color='r')
    ax3.plot(sorted_dataNeg, yvalsNeg, label=str(param)+"-40%", color='b')
    ax3.plot(sorted_dataBC, yvalsBC, label="cas de référence", color='grey')
    # plt.legend(loc='lower right')
    ax3.set_xlabel('$TTC_{min}^{latéral}$ (s)')


    posVarX = results['+40']["speedDifferential"]
    negVarX = results['-40']["speedDifferential"]
    baseCaseX = baseCaseResults["speedDifferential"]

    sorted_dataPos = np.sort(posVarX)
    sorted_dataNeg = np.sort(negVarX)
    sorted_dataBC = np.sort(baseCaseX)

    if not normed:
        yvalsPos = np.arange(len(sorted_dataPos))
        yvalsNeg = np.arange(len(sorted_dataNeg))
        yvalsBC = np.arange(len(sorted_dataBC))
    else:
        yvalsPos = np.arange(len(sorted_dataPos)) / float(len(sorted_dataPos) - 1)
        yvalsNeg = np.arange(len(sorted_dataNeg)) / float(len(sorted_dataNeg) - 1)
        yvalsBC = np.arange(len(sorted_dataBC)) / float(len(sorted_dataBC) - 1)

    ax5.plot(sorted_dataPos, yvalsPos,  label=str(param)+"+40%", color='r')
    ax5.plot(sorted_dataNeg, yvalsNeg, label=str(param)+"-40%", color='b')
    ax5.plot(sorted_dataBC, yvalsBC, label="cas de référence", color='grey')
    ax5.set_xlabel('$\Delta v_{min}$ (m/s)')

    plt.savefig('sa-tornado-cdf{}.pdf'.format(parameter))

    plt.close('all')


    fig = plt.figure(figsize=(13,10))

    redPatch = mpatches.Patch(color='red', label=param+"+40%")
    greyPatch = mpatches.Patch(color='grey', label="cas de référence")
    bluePatch = mpatches.Patch(color='blue', label=param+"-40%")

    fig.legend(handles=[redPatch, greyPatch, bluePatch], loc= 'upper left')

    ax1 = plt.subplot2grid((2, 2), (0, 0), rowspan=2)
    ax2 = plt.subplot2grid((2, 2), (0, 1), colspan=1, rowspan=1)
    ax3 = plt.subplot2grid((2, 2), (1, 1), rowspan=1, colspan=1)

    x2 = ['$\overline{nInter}^{arrière}_{50}$', '$\overline{nInter}^{arrière}_{20}$', '$\overline{nInter}^{arrière}_{10}$', '$\overline{nInter}^{latéral}_{50}$', '$\overline{nInter}^{latéral}_{20}$', '$\overline{nInter}^{latéral}_{10}$']#, r'$\overline{nUsers}_{2}^{completed}$', r'$\overline{t_{2}}^{\%congested}$', r'$\overline{v}$']# 'timePecentageInCongestedState2']

    negativeVariation, positiveVariation, negErr, posErr, _, _ = getSensivities(parameter)

    ax1.barh(x2, negativeVariation[3:-3][::-1], color='None', align='center', height=.8, edgecolor='b',  xerr=negErr[3:], error_kw=dict(ecolor='blue', capsize=3), tick_label=x2)
    ax1.barh(x2, positiveVariation[3:-3][::-1], color='None', align='center', height=.8, edgecolor='r',  xerr=posErr[3:], error_kw=dict(ecolor='red', capsize=3), tick_label=x2)

    ax1.set_xlabel('Pourcentage de variation (%)')
    plt.tight_layout(pad=0.8, w_pad=0.5, h_pad=1.5)
    ax1.plot([0,0], [0,len(x2)], color='black')

    posVarX = results['+40']["minDistances"][1]
    negVarX = results['-40']["minDistances"][1]
    baseCaseX = baseCaseResults["minDistances"][1]

    sorted_dataPos = np.sort(posVarX)
    sorted_dataNeg = np.sort(negVarX)
    sorted_dataBC = np.sort(baseCaseX)

    if not normed:
        yvalsPos = np.arange(len(sorted_dataPos))
        yvalsNeg = np.arange(len(sorted_dataNeg))
        yvalsBC = np.arange(len(sorted_dataBC))
    else:
        yvalsPos = np.arange(len(sorted_dataPos)) / float(len(sorted_dataPos) - 1)
        yvalsNeg = np.arange(len(sorted_dataNeg)) / float(len(sorted_dataNeg) - 1)
        yvalsBC = np.arange(len(sorted_dataBC)) / float(len(sorted_dataBC) - 1)


    ax3.plot(sorted_dataPos, yvalsPos,  label=str(param)+"+40%", color='r')
    ax3.plot(sorted_dataNeg, yvalsNeg, label=str(param)+"-40%", color='b')
    ax3.plot(sorted_dataBC, yvalsBC, label="cas de référence", color='grey')
    ax3.set_xlabel('$D_{min}^{arrière}$ (m)')

    posVarX = results['+40']["minDistances"][2]
    negVarX = results['-40']["minDistances"][2]
    baseCaseX = baseCaseResults["minDistances"][2]

    sorted_dataPos = np.sort(posVarX)
    sorted_dataNeg = np.sort(negVarX)
    sorted_dataBC = np.sort(baseCaseX)

    if not normed:
        yvalsPos = np.arange(len(sorted_dataPos))
        yvalsNeg = np.arange(len(sorted_dataNeg))
        yvalsBC = np.arange(len(sorted_dataBC))
    else:
        yvalsPos = np.arange(len(sorted_dataPos)) / float(len(sorted_dataPos) - 1)
        yvalsNeg = np.arange(len(sorted_dataNeg)) / float(len(sorted_dataNeg) - 1)
        yvalsBC = np.arange(len(sorted_dataBC)) / float(len(sorted_dataBC) - 1)


    ax2.plot(sorted_dataPos, yvalsPos,  label=str(param)+"+40%", color='r')
    ax2.plot(sorted_dataNeg, yvalsNeg, label=str(param)+"-40%", color='b')
    ax2.plot(sorted_dataBC, yvalsBC, label="cas de référence", color='grey')
    ax2.set_xlabel('$D_{min}^{latéral}$ (m)')


    plt.savefig('sa-tornado-cdf{}-suite.pdf'.format(parameter))


# function for setting the colors of the box plots pairs
def setBoxColors(bp):
    plt.setp(bp['boxes'][0], color='blue')
    plt.setp(bp['caps'][0], color='blue')
    plt.setp(bp['caps'][1], color='blue')
    plt.setp(bp['whiskers'][0], color='blue')
    plt.setp(bp['whiskers'][1], color='blue')
    plt.setp(bp['fliers'][0], color='blue')
    # plt.setp(bp['fliers'][1], color='blue')
    plt.setp(bp['medians'][0], color='blue')

    plt.setp(bp['boxes'][1], color='grey')
    plt.setp(bp['caps'][2], color='grey')
    plt.setp(bp['caps'][3], color='grey')
    plt.setp(bp['whiskers'][2], color='grey')
    plt.setp(bp['whiskers'][3], color='grey')
    plt.setp(bp['fliers'][1], color='grey')
    # plt.setp(bp['fliers'][2], color='grey')
    plt.setp(bp['medians'][1], color='grey')

    plt.setp(bp['boxes'][2], color='red')
    plt.setp(bp['caps'][4], color='red')
    plt.setp(bp['caps'][5], color='red')
    plt.setp(bp['whiskers'][4], color='red')
    plt.setp(bp['whiskers'][5], color='red')
    plt.setp(bp['fliers'][2], color='red')
    # plt.setp(bp['fliers'][3], color='red')
    plt.setp(bp['medians'][2], color='red')


def getBoxPlots(parameter):
    baseCaseResults = toolkit.loadYaml('sorties/00base-case-results.yml')
    results = {"-40": {"minTTCs": toolkit.loadYaml('sorties/sa-minTTCs-{}-0.4.yml'.format(parameter)),
                       "PETs": toolkit.loadYaml('sorties/sa-PETs-{}-0.4.yml'.format(parameter)),
                       "nInter10": toolkit.loadYaml('sorties/sa-nInter10{}-0.4.yml'.format(parameter)),
                       "nInter20": toolkit.loadYaml('sorties/sa-nInter20{}-0.4.yml'.format(parameter)),
                       "nInter50": toolkit.loadYaml('sorties/sa-nInter50{}-0.4.yml'.format(parameter)),
                       "sidenInter10": toolkit.loadYaml('sorties/sa-side-nInter10-{}-0.4.yml'.format(parameter)),
                       "sidenInter20": toolkit.loadYaml('sorties/sa-side-nInter20-{}-0.4.yml'.format(parameter)),
                       "sidenInter50": toolkit.loadYaml('sorties/sa-side-nInter50-{}-0.4.yml'.format(parameter)),
                       "rearEndnInter10": toolkit.loadYaml('sorties/sa-rearEnd-nInter10-{}-0.4.yml'.format(parameter)),
                       "rearEndnInter20": toolkit.loadYaml('sorties/sa-rearEnd-nInter20-{}-0.4.yml'.format(parameter)),
                       "rearEndnInter50": toolkit.loadYaml('sorties/sa-rearEnd-nInter50-{}-0.4.yml'.format(parameter)),
                       "completedUser0": toolkit.loadYaml('sorties/numberOfUsers0-{}-0.4.yml'.format(parameter))[parameter][-.4],
                       "completedUSers2": toolkit.loadYaml('sorties/numberOfUsers2-{}-0.4.yml'.format(parameter))[parameter][-.4],
                       "minDistances": toolkit.loadYaml('sorties/sa-minDistances-{}-0.4.yml'.format(parameter))

                       },

               "+40": {"minTTCs": toolkit.loadYaml('sorties/sa-minTTCs-{}0.4.yml'.format(parameter)),
                       "PETs": toolkit.loadYaml('sorties/sa-PETs-{}0.4.yml'.format(parameter)),
                       "nInter10": toolkit.loadYaml('sorties/sa-nInter10{}0.4.yml'.format(parameter)),
                       "nInter20": toolkit.loadYaml('sorties/sa-nInter20{}0.4.yml'.format(parameter)),
                       "nInter50": toolkit.loadYaml('sorties/sa-nInter50{}0.4.yml'.format(parameter)),
                       "sidenInter10": toolkit.loadYaml('sorties/sa-side-nInter10-{}0.4.yml'.format(parameter)),
                       "sidenInter20": toolkit.loadYaml('sorties/sa-side-nInter20-{}0.4.yml'.format(parameter)),
                       "sidenInter50": toolkit.loadYaml('sorties/sa-side-nInter50-{}0.4.yml'.format(parameter)),
                       "rearEndnInter10": toolkit.loadYaml('sorties/sa-rearEnd-nInter10-{}0.4.yml'.format(parameter)),
                       "rearEndnInter20": toolkit.loadYaml('sorties/sa-rearEnd-nInter20-{}0.4.yml'.format(parameter)),
                       "rearEndnInter50": toolkit.loadYaml('sorties/sa-rearEnd-nInter50-{}0.4.yml'.format(parameter)),
                       "completedUser0": toolkit.loadYaml('sorties/numberOfUsers0-{}0.4.yml'.format(parameter))[parameter][.4],
                       "completedUSers2": toolkit.loadYaml('sorties/numberOfUsers2-{}0.4.yml'.format(parameter))[parameter][.4],
                       "minDistances": toolkit.loadYaml('sorties/sa-minDistances-{}0.4.yml'.format(parameter))

                       }}

    plt.figure()
    ax = plt.axes()

    # first boxplot pair
    bp = plt.boxplot([results['-40']['minTTCs'][1], results['-40']['minTTCs'][2] , results['-40']['PETs']], positions=[1, 2, 3], widths=0.6)
    setBoxColors(bp)

    # second boxplot pair
    bp = plt.boxplot([baseCaseResults['minTTCs'][1], baseCaseResults['minTTCs'][2] , baseCaseResults['PETs']], positions=[4, 5, 6], widths=0.6)

    setBoxColors(bp)

    # third boxplot pair
    bp = plt.boxplot([results['+40']['minTTCs'][1], results['+40']['minTTCs'][2] , results['+40']['PETs']], positions=[7, 8, 9], widths=0.6)
    setBoxColors(bp)

    # set axes limits and labels
    plt.xlim(0, 20)
    plt.ylim(0, 20)
    ax.set_xticklabels(['min TTC rear', 'min TTC side%', 'PET%'])
    ax.set_xticks([1.5, 4.5, 7.5])

    # draw temporary red and blue lines and use them to create a legend
    hB, = plt.plot([1, 1], 'b-')
    hG, = plt.plot([1, 1], 'grey')
    hR, = plt.plot([1, 1], 'r-')

    plt.legend((hB, hG, hR), ('-40%', '0%', '+40%'))
    hB.set_visible(False)
    hG.set_visible(False)
    hR.set_visible(False)
    plt.savefig('sa-boxplots-{}.pdf'.format(parameter))

def getVariationTableAsCSV():
    results = {}
    parameters = ['tau', 'dn', 'headway', 'speed', 'length', 'criticalGap']

    for param in parameters:
        results[param] = getSensivities(param)



    d = {'tau-': results['tau'][0],
         'tau+': results['tau'][1],
         'dn-': results['dn'][0],
         'dn+': results['dn'][1],
         'headway-': results['headway'][0],
         'headway+':results['headway'][1],
         'speed-': results['speed'][0],
         'speed+': results['speed'][1],
         'length-': results['length'][0],
         'length+': results['length'][1],
         'criticalGap-': results['length'][0],
         'criticalGap+': results['length'][1]
         }

    df = pd.DataFrame(data=d)
    df.to_csv('sa-tableData-variations.csv')

def getValuesTableAsCSV(variations=False):
    results = {}
    parameters = ['tau', 'dn', 'headway', 'speed', 'length', 'criticalGap']

    if variations is False:
        for param in parameters:
            results[param] = getSensivities(param)[-1]

    else:
        for param in parameters:
            results[param] = getSensivities(param)[-2]

    d = {'tau-': [elem for elem in [results['tau'][key]['-40'] for key in results['tau']]],
         'tau+': [elem for elem in [results['tau'][key]['+40'] for key in results['tau']]],
         'dn-': [elem for elem in [results['dn'][key]['-40'] for key in results['dn']]],
         'dn+': [elem for elem in [results['dn'][key]['+40'] for key in results['dn']]],
         'headway-': [elem for elem in [results['headway'][key]['-40'] for key in results['headway']]],
         'headway+': [elem for elem in [results['headway'][key]['+40'] for key in results['headway']]],
         'speed-': [elem for elem in [results['speed'][key]['-40'] for key in results['speed']]],
         'speed+': [elem for elem in [results['speed'][key]['+40'] for key in results['speed']]],
         'length-': [elem for elem in [results['length'][key]['-40'] for key in results['length']]],
         'length+': [elem for elem in [results['length'][key]['+40'] for key in results['length']]],
         'criticalGap-': [elem for elem in [results['criticalGap'][key]['-40'] for key in results['criticalGap']]],
         'criticalGap+': [elem for elem in [results['criticalGap'][key]['+40'] for key in results['criticalGap']]],
         }

    df = pd.DataFrame(data=d)
    if variations is False:
        value = 'values'
    else:
        value = 'variations'
    df.to_csv('sa-tableData-{}.csv'.format(value))

from scipy import stats
xList = stats.norm.rvs(loc=6, scale=3, size=1000)
xList = np.sort(xList)
yList = np.arange(len(xList)) / float(len(xList) - 1)
plt.ylabel('Fréquences cumulées')
plt.xlabel('x')
plt.plot(xList, yList, label='Échantillon 1')

xList = stats.norm.rvs(loc=5, scale=2, size=1000)
xList = np.sort(xList)
yList = np.arange(len(xList)) / float(len(xList) - 1)
plt.plot(xList, yList, label='Échantillon 2')
x = 8.1
y = .74
dx = 0
dy = .95 - y
plt.annotate(xy=(x,y), xytext=(x+dx,y+dy), arrowprops=dict(arrowstyle='<->'), text='')
plt.annotate(xy=(x,(y+dy)/2), xytext=(8.48,0.86), text='D')
plt.legend()
plt.savefig('explication-ks.pdf')
# baseCaseX = xList
#
# sorted_dataBC = np.sort(baseCaseX)
# yvalsBC = np.arange(len(sorted_dataBC)) / float(len(sorted_dataBC) - 1)
#
# plt.plot(sorted_dataBC, yvalsBC, label="cas de référence", color='grey')
# plt.legend(loc='lower right')
# plt.xlabel('$D_{min}^{arrière}$ (m)')