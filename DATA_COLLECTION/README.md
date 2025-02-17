# Website Access Sample Data Collection Tool Guide

## Overview
This tool module aims to provide a comprehensive automated data collection solution for website fingerprinting attack research. By leveraging the Selenium framework, it enables automated control of mainstream browsers (Chrome and Firefox) and supports the collection of the following data samples:

1. **Network Traffic Data**: Captures raw network traffic (.pcap files) during website access using tcpdump.

2. **Browser Logs**: Records detailed log information during browser access.

3. **Page Screenshots**: Saves screenshots of the fully rendered website.

4. **DNS Resolution Records**: Collects domain-to-IP mapping information involved during website access.

## Environment Setup

### 1. Browser and Driver Installation
#### 1.1 Install the Latest Browser Environment (Recommended)
The following example demonstrates the installation of the Chrome browser on a Linux system:

```bash
# Create installation directory
mkdir chrome && cd chrome

# Download Chrome browser and driver
wget https://storage.googleapis.com/chrome-for-testing-public/126.0.6478.126/linux64/chromedriver-linux64.zip
wget https://storage.googleapis.com/chrome-for-testing-public/126.0.6478.126/linux64/chrome-linux64.zip

# Unzip the installation packages
unzip chrome-linux64.zip && unzip chromedriver-linux64.zip

# Install dependency libraries
sudo yum install -y libxcb libXcomposite gtk3 libXrandr \
libXrender libXdamage libXcursor libXfixes libXi \
libXinerama libXScrnSaver libXtst alsa-lib cups-libs \
libdrm mesa-libgbm atk at-spi2-atk pango libxkbcommon glibc

# Verify installation
./chrome-linux64/chrome --version
./chromedriver-linux64/chromedriver --version
```

After installation, configure the executable paths of the browser and driver in the config.yaml file.

#### 1.2 Install Additional Browser Environments (For Reproducing Paper Experiments)

**Chrome v104 Version**:

```bash
wget -O chromedriver-linux.zip "https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Linux_x64%2F1012728%2Fchromedriver_linux64.zip?generation=1654813050598651&alt=media"
wget -O chrome-linux.zip "https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Linux_x64%2F1012728%2Fchrome-linux.zip?generation=1654813044687278&alt=media"
```

**Firefox Browser**:

```bash
wget "https://download.mozilla.org/?product=firefox-latest&os=linux64&lang=en-US" -O firefox.tar.bz2
wget https://github.com/mozilla/geckodriver/releases/download/v0.34.0/geckodriver-v0.34.0-linux64.tar.gz
```

### 2. Environment Configuration
#### 2.1 Install Python Dependency Libraries:
```bash
pip install -r requirements.txt
```

#### 2.2 Modify the config.yaml Configuration File:
- Configure the correct network interface name.

- Set the browser executable file paths.


## Data Collection

Use the collect_main.py script for data collection. Key parameters are explained below:

| Parameter       | Description                                     | Example Value                          |
|-------------|-------------------------------------------|---------------------------------|
| --domain    | Path to the target domain list file                    | ./top_1600_domains.csv         |
| --times     | Number of collection cycles                         | 10                             |
| --browser   | Browser type to use (chrome/firefox)   | chrome                         |
| --network   | Network simulation condition (unconstrained/starlink-like/slow) | starlink-like                 |


**Example Command**:

```bash
python3 ./collect_main.py \
    --domain ./top_1600_domains.csv \
    --times 10 \
    --browser chrome \
    --network starlink-like
```