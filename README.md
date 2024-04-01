# H123-Website-Fingerprinting
<p align="center">
  <img src="images/icon.png" alt="My Image" width="550">
</p>

The code and dataset for "HOLMES and WATSON: A New Perspective on Website Fingerprinting through HTTP Version Parallelism"


**This repository currently provides the core code for H123 fingerprinting, including fingerprint extraction and construction, and website identification using fingerprints. The complete code (including performance evaluation in various scenarios, plotting, etc.) will be open-sourced after the results of the paper are given.**

⚠️ The code is intended for RESEARCH PURPOSES ONLY! ⚠️

## Repositories Organization
*Code* provides the core code of this work, which contains three parts are HOLMES, WATSON and configuration file. 
- *Code-HOLMES* provides a complete series of H123 feature extraction and fingerprinting functions
- *Code-WATSON* provides part of the code used to validate the recognition ability of the website using H123 fingerprints
- *Code-config.yaml* is a global configuration file, mainly used to specify the hyperparameters of such methods

*Dataset* contains the extracted H123 fingerprint data. These data are for the top 300 sites in the tranco list that contain HTTP/3 resources on a stable basis, and H123 fingerprints were extracted 40 times for each site.

*Images* contains images used as an introduction to better understand this work.

## Setup

