# networked_climate_monitor

Source code for all components in the Networked Climate Monitor project created by UP801685.

## Project Description
The Networked Climate Monitor provides regularly updated data about the indoor and outdoor climates in locations such as a house, garden, or office. The system has a website that displays the climate data while providing management of the system's sensor nodes and system settings. The system was designed to be a more flexible and modular alternative to the existing weather station systems currently on the market. Many of the design choices of this system have been influenced by the variety of limitations that affect existing climate monitoring products. These limitations include high initial costs, limited modularity affecting the number of sensor nodes per system, and the lack of modularity in the types of climate data that can be recorded by the sensor nodes. Due to these limitations, the system was designed to improve upon these limitations by being more affordable with low initial costs, multiple sensor nodes, modular sensor nodes, and better data privacy. 

This website displays the most recent climate data from each connected node with charts of the historical climate data from the last 6 months. The system supports up to 20 concurrent sensor nodes; these nodes can be dynamically added and removed from the system. Each node can support different types of sensor hardware so that a variety of climate data types can be recorded. The nodes are battery powered with a battery life of over 6 months and have a communication range of 50 metres with the base station. The nodes are waterproof and can be placed inside and outside; the nodes can also be recharged via a micro USB cable.

## Code Structure
API, website, database, radio manager, and wifi manager code are in the base_station folder.
Sensor node code is in the sensor_node folder.

## Hardware Requirements
### Sensor Node
- Adafruit Feather 32u4 433mhz RFM69HCW microcontroller with the attached radio module.
- Lithium Ion battery (Ideally 3000MaH or above to get long battery life)
- Sensors (A BME280 sensor was used but others will require small changes to the code for their measurements to be recorded)

### Base Station
- Raspberry Pi (A Raspberry Pi 3 A+ was used but any that are more powerful than the Zero are suitable)
- 433mhz RFM69HCW radio module

## Building and running
### Sensor Node
- Connect to the microcontroller via the Ardiuno IDE
- Load the following modules into the IDE
  - LowPower
  - Adafruit_Sensor
  - Adafruit_BME280
  - LowPowerLab RFM69 and RFM69_ATC
- Upload the sensor_node.ino code to the microcontroller

### Base Station
- While the base station systems are independent they should be created in the order shown to ensure that they connect correctly
#### API
To run locally during development
- navigate to the base-station/web-server folder
- pip install
- python3 run.py

To run in a production environment apache or another web-server is required
During the implementation Apache was used with the API running as a WSGI application
#### WiFi Manager
- navigate to web-server
- npm install
- npm run
#### Radio Manager 
- navigate to base-station/radio
- pip install
- python3 radio.py
#### Website
To run during development
- navigate to the base_station/front-end folder
- npm install
- npm run serve

To build for production and end-to-end tests
- npm install
- npm build
- move the files from the dist folder into the correct locations for static file serving in the web-server

## Tests
### Sensor Node
Requires the base station to be running with the radio manager
- Connect to the microcontroller via the Ardiuno IDE
- Load the following modules into the IDE
  - LowPower
  - LowPowerLab RFM69 and RFM69_ATC
- Upload the range_test.ino code to the microcontroller
- The microcontroller LED will then flash when an acknowledgement is received from the base station
#### API
- navigate to the base-station/web-server folder
- pip install
- python3 test_climate_monitor.py
#### Radio Manager 
- navigate to base-station/radio
- pip install
- python3 test_radio.py
#### Website
Unit tests
- navigate to the base_station/front-end folder
- npm install
- npm run test:unit

End-to-end tests
- navigate to the base-station/web-server folder
- pip install
- python3 run_test_server.py
- navigate to the base_station/front-end folder
- npm install
- npm run clear-jest-cache
- npm run test:e2e
