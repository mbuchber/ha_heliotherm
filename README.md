# HaHeliotherm - Component
<img src="https://github.com/mbuchber/ha_heliotherm/blob/b3bb7d035f186dd6520c8395d5a5111821dac922/heliotherm.png"  width="512">

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration)
![Version](https://img.shields.io/github/v/release/mbuchber/ha_heliotherm?style=plastic)
![Downloads](https://img.shields.io/github/downloads/mbuchber/ha_heliotherm/total)

Home Assistant Custom Component for Heliotherm Heatpumps

![Example screenshot of dashboard](/Screenshot.png)

## Installation

### HACS

This component is easiest installed using [HACS](https://github.com/custom-components/hacs).

To download the component, [the repository URL must be added as custom repository to HACS](https://hacs.xyz/docs/faq/custom_repositories/).

Use the URL: https://github.com/mbuchber/ha_heliotherm

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

## Activating Modbus-TCP using Heliotherm Webinterface
- Go to the default web page of your Heliotherm. (Served on port 80 of HT-IP address)
- 'swipe' left to page 3 of the default UI (the little circles at the bottom represent the page you are looking at and can you also press the 3rd circle)
- Press 'Settings' (cog-wheels icon)
- Now you have two options 1) User, 2) Service. For now choose 'Service' (we will come back later for User part)
- Enter user/pwd (admin/superuser)*
- On new page choose "Main Setting"
- On new page choose "Modbus"
- On new page choose either TCP (modbus over IP) or RTU (modbus over RS485). Only choose 1! Can't both be on. If your HT has and ethernet connection on your local network would recommend to use TCP.
- Choose "Turn On" under TCP in drop down box and leave the default settings (slave means the slave address of the modbus)
- press your browser back button 3 times
- (now you are back to 1)User 2)Service.). Now choose "User"
- Press button "Restart" in the new screen
- Done (take a minute to reboot)

If you have setup HA device already the data should be getting in at this point
Disclaimer: Use at own risk. As super user you can do quite some settings that should not be done if you do not know what you are doing. In other words: Don't change any settings unless you have been instructed to by a HT expert as super user.
