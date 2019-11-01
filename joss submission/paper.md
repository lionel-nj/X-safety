---
title: X-Safety: An Open-Source Minimal Micro-Simulation Tool for Safety Analysis
tags:
  - Python
  - road safety
  - safety analysis
  - road users
  - user interactions
  - traffic conflicts
  - crossing
  - traffic simulation
  - safety simulation
  - surrogate measures of safety 
  - SMoS
authors:
  - name: Lionel Nébot-Janvier
    orcid: 0000-0002-9918-4502
    affiliation: 1
  - name: Nicolas Saunier
    orcid: 0000-0003-0218-7932
    affiliation: 1
	
affiliations:
 - name: École Polytechnique de Montréal. Civil, Geological and Mining Engineering Department
   index: 1
date: 16 October 2019
bibliography: paper.bib
---

# Summary

Road crashes remain a global public health issue. Road safety analysis most commonly relies on historical crash records and to make any change cities have to collect up to five years of crash data [@global-synergies]. Such an approach is reactive to the extent that one must wait for long periods of time to collect sufficient data coming from crash reports to identify unsafe sites and implement solutions. This constitutes therefore an ethical issue as one needs to wait for accidents to occur to be able to prevent them. 

To circumvent this limitation surrogate measures of safety (SMoS) have been studied and developed over the last decades [@laureshyn16appendix]. SMoS rely on indicators obtained from direct traffic observation. Safety indicators like the time-to-collision (TTC) and post-encroachment time (PET) are used to measure the severity of road user interaction, that is their proximity to a potential crash. SMoS enable the proactive analysis of road safety more quickly before accidents happen. However, only some SMoS, most prominently from traffic conflict techniques (TCT), have validated [@laureshyn16appendix]. Based on conflict observations using the Swedish TCT, Svensson studied the distribution of conflict safety indicators at different sites [@svensson1998method;@svensson06estimating]. This paper presents ``X-Safety``, a minimal microscopic traffic simulation tool for road safety analysis, with the main goal to investigate the distributions of interaction severity indicators. The tool currently focuses on road intersections, but is meant to be easy to configure and to be able to represent any road network. A tutorial is provided for users to get started with ``X-Safety`` for simple use cases. 


# X-Safety

``X-Safety`` is a Python package that allows to represent road users moving along roads. It relies on a relatively simple car-following model proposed by Newell [@newell2002simplified; @laval2008microscopic]. User behaviour at intersection are the result of a simple model at traffic control devices based on gap acceptance theory for yield and stop signs. 
The program has been developed following the methodology from the work of Gauthier [@gauthier2016calibration]. It is to be noted that the positions and indicators of each users are updated at a regular step time that is defined by the user of ``X-Safety``. 
In the current first version, turning movements and lane changes are not represented. 

In order to use ``X-safety``, the user needs to define the experimental setup: the road network, the duration of the simulation, the number of replications, and the model parameters. For each replication, the program generates and moves the road users, then saves the measures of interest. These measures can then be compared for different type of facilities.  

``X-Safety`` also contains a collection of functions that can be used to perform operations on lists but also to load, save and modify YAML files. The implementation of ``X-Safety`` relies on the open source ``Traffic Intelligence`` project [@jackson13flexible-trr; @st2015large] that provides a set of tools for transport data and video analysis. ``Traffic Intelligence`` provides a framework to represent roads and their coordinate systems, and road users with their trajectories. 

To remain minimal, simple models were chosen to represent the world and user behaviours. It therefore has several limitations, some by design, others by lack of time in the current version:

- Road users move at constant speeds over sucessive time intervals. TTC computation relies on predicting road user trajectories at each instant, which is currently done at constant speed and direction, which is in accordance with the road user motion model, but can be replaced with more advanced and realistic motion prediction methods [@mohamed13motion-trr; @st2015large];
- Road users change speed instantaneously, i.e. have infinite acceleration, which may bring discontinuities into their trajectories and indicators; 
- Road user lateral movement is not described and no lane change model is available in the current version. 

``X-safety`` had been used previously in several case studies that are presented in ``An Open-Source Minimal Micro-Simulation Tool for Safety Analysis`` [@nebot-janvier20minimal]. The results show that the distributions of interaction safety indicators are significantly different for different traffic control devices, namely yield and stop signs, and when user interactions are recorded in areas  of different sizes. 

# Acknowledgements

The authors wish to acknowledge the financial support of the National Science and Engineering Council (NSERC) of Canada through the Discovery Acceleration Supplement grant no 507950.

# References
