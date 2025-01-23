# H123-Website-Fingerprinting
<p align="center">
  <img src="images/icon.png" alt="My Image" width="550">
</p>

The code and dataset for "HOLMES & WATSON: A Robust and Lightweight HTTPS Website Fingerprinting through HTTP Version Parallelism"

*Dataset acquisition instructions: TBD*


**This repository currently provides the core code for H123 fingerprinting, including fingerprint extraction and construction, and website identification using fingerprints. The complete code (including performance evaluation in various scenarios, plotting, etc.) will be open-sourced after the results of the paper are given.**

The figure below shows the specific manifestations of the proposed H123 fingerprint on the most popular websites, indicating that compared to traditional website fingerprints (such as using hundreds of statistical features or packet length sequences), the H123 fingerprint is visually concise, information-rich, more powerful, and exhibits clear distinguishability.
<p align="center">
  <img src="images/H123_sample.png" alt="My Image" width="550">
</p>

⚠️ The code is intended for RESEARCH PURPOSES ONLY! ⚠️ 

## Repositories Organization
*Code* provides the core code of this work, which contains three parts are HOLMES, WATSON and configuration file. 
- *Code-HOLMES* provides a complete series of H123 feature extraction and fingerprinting functions
- *Code-WATSON* provides part of the code used to validate the recognition ability of the website using H123 fingerprints
- *Code-config.yaml* is a global configuration file, mainly used to specify the hyperparameters of such methods

*Dataset* contains the extracted H123 fingerprint data. These data are for the top 300 sites in the tranco list that contain HTTP/3 resources on a stable basis, and H123 fingerprints were extracted 40 times for each site.

*Images* contains images used as an introduction to better understand this work.

## Setup
With python3 enviroment, please make sure that you have the necessary libraries installed to run your code, using the following command

```bash
pip install -r requirements.txt
```

Now you can recognize websites based on the built H123 fingerprint dataset, if you wish to collect and extract H123 website fingerprints by yourself, you still need to do the following configurations.
### Setup Browser and Driver
Please download the complete version of Chrome and chromedriver, and then change the program path in *Code-HOLMES-collect_pcap_log.py*.

### Setup Packet Capturer
Just make sure you have tcpdump or tshark installed on your system to run properly, and specify the network card to trap packets if necessary. These you can configure in *Code-HOLMES-collect_pcap_log.py*.

## Website Fingerprinting
Run *Code-WATSON-val_with_dataset.py* to test the effectiveness of the website fingerprinting attack. Meanwhile, you can modify the hyperparameters used by this method in *Code-config.yaml*.

