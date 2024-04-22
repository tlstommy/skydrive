<h2 align="center" style="border:none">
  SkyDrive - A Wireless Portable Storage Device
  <h6 align="center" style="color: gray;">
    University of Tennessee - 2024 Senior Design
  </h6>
</h2>

-----

### An open-source, low-cost, portable, wireless storage medium for anyone on the go.

**Features:**
- **Web UI**: A built-in interface to control SkyDrive and manage your data over the network.
- **Drive Reusability**: Instead of having to buy a new external hard drive, pop in any M.2 storage mediums, saving both money and the planet.
- **SMB support**: Allows for the device to function as a miniature Network attached storage device on a network
- **Secure**: Data on the device is secured by a user-defined password
- **Open Source**: SkyDrive is under an open-source license, so modify it as you see fit!

# Table of Contents
* [Overview](#)
* [Installation](#installation)
* [WebUI](#webui)
* [Parts List](#parts-list)
   * [3D Printed Casing](#3d-printed-casing)
* [Assembly](#skydrive-assembly)
* [Issues & Suggestions](#issues--suggestions)


# Installation

To install, clone the repository, run the install script, and follow the on-screen instructions:

```bash
git clone https://github.com/tlstommy/skydrive.git
cd skydrive
sudo bash install.sh

```

Upon completion, SkyDrive will start and be accessible on the web at the Raspberry Pi's IP address or at `SkyDrive.local`.


# WebUI

**SkyDrive can be controlled via the WebUI which can be found at the Raspberry Pi's IP address or at `skydrive.local`**




# Parts List

SkyDrive was designed to work with a Raspberry Pi 5 due to the fast speeds of the PCIe and WIFI adapter and should be compatible with any NVME drive connected over the Pi's PCIe lanes. 

### 3D Printed Casing


#### Recommended Printing Settings
- Layer Height: 0.15mm
- Infill: 10%-15%
- Supports: Baseplate

# SkyDrive Assembly

Assembling SkyDrive is a straightforward process that can be completed in x simple steps.

**You will need the following materials:**
- (2) Standoffs
- (2) Screws
  
### Step 1:

### Step 2: 

### Step 3: 


# Issues & Suggestions
If you encounter any issues or have any suggestions, please submit them through the [GitHub Issues](https://github.com/tlstommy/skydrive/issues) page. Your feedback is greatly appreciated!



