# ha_heliotherm
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)
![Version](https://img.shields.io/github/v/release/mbuchber/ha_heliotherm?style=plastic)
![Downloads](https://img.shields.io/github/downloads/mbuchber/ha_heliotherm/total)

Home Assistant Custom Component for Heliotherm Heatpumps

![Example screenshot of dashboard](/Screenshot.png)

## Installation

### HACS

This component is easiest installed using [HACS](https://github.com/custom-components/hacs).

### Manual installation

Copy all files from custom_components/ha_heliotherm/ to custom_components/ha_heliotherm/ inside your config Home Assistant directory.

### Prerequisites
- Ownership of a Heliotherm heatpump ;)
- Some network connection to the heatpump (RS-232 to Modbus-TCP or Heliotherm RCG-Interface)
    - For RS232 to Modbus interfaces like these (https://www.antratek.de/rs232-modbus-gateway, https://www.wish.com/product/5fa10f7070a46f003d78e096)
    - The original from Heliotherm is the Remote Control Gateway (RCG) that also has its own Web interface and SD-card slot etc. (see docs folder for more information on RCG)    

## Configuration via UI
When adding the component to the Home Assistant intance, the config dialog will ask for Name, Host/IP-Address of the heatpump interface and the port number (usually 502 for Modbus over TCP)

## Entities

The integration creates multiple entities for recieving that states of the heatpump and for controlling mode of operation, heating room temperature and warm water heating.
