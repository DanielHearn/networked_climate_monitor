#include <RFM69.h>
#include <RFM69_ATC.h>
#include <SPIFlash.h>
#include <SPI.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>
#include <LowPower.h>
#include <EEPROM.h>

// Radio configuration
#define NETWORKID     100
#define FREQUENCY     RF69_433MHZ
#define ENCRYPTKEY    "pnOvzy105sF5g8Ot"
#define BASESTATIONID 255
#define EMPTYPACKET   "____________________________________________________________"

// Serial configuration
#define SERIAL_BAUD   115200

// Radio pins
#define RF69_RESET    4
#define RF69_SPI_CS   8
#define RF69_IRQ_PIN  7
#define RF69_IRQ_NUM  4

// Sensor pins
#define BME_SCK 13
#define BME_MISO 12
#define BME_MOSI 11
#define BME_CS 10

// Battery pin
#define VBATPIN A9

// Load modules
Adafruit_BME280 bme;
RFM69_ATC radio(RF69_SPI_CS, RF69_IRQ_PIN, false, RF69_IRQ_NUM);

// Define global variables
unsigned bme_status;
boolean initialised = false;
long send_interval = 60000;
long initialisation_interval = 60000;
int target_rssi = -80;
boolean new_node = false;

// Node ID starts 254 until loaded from EEPROM or assigned by base station via initialisation
int node_id = 254;

// Setup
void setup() {
  Serial.begin(SERIAL_BAUD);
  Serial.println("Starting sensor node");

  initSensors();

  // Delay starting loop so that new programs can be easily uploaded
  delay(20000);
}

// Initialise all connected sensors
void initSensors() {
  // Load BME280 sensor
  bme_status = bme.begin();
  if (!bme_status) {
    Serial.println("Could not find a valid BME280 sensor, check wiring, address, sensor ID!");
    while (1);
  }

  // Set sensor to use forced mode
  bme.setSampling(Adafruit_BME280::MODE_FORCED,
                  Adafruit_BME280::SAMPLING_X1, // temperature
                  Adafruit_BME280::SAMPLING_X1, // pressure
                  Adafruit_BME280::SAMPLING_X1, // humidity
                  Adafruit_BME280::FILTER_OFF   );
}

// Initialise the radio module with a node ID
void initRadio(int node_id) {
  Serial.print("Initialising radio with node ID: ");
  Serial.println(node_id);
   
  // Reset the radio
  resetRadio();

  // Initialize the radio
  radio.initialize(FREQUENCY, node_id, NETWORKID);
  radio.promiscuous(false);
  radio.setHighPower();
  radio.encrypt(ENCRYPTKEY);

  // Enable ATC to low battery usage when close to base station
  radio.enableAutoPower(target_rssi);
}

// Read battery level and convert it to voltage
float getBatteryVoltage() {
  return analogRead(VBATPIN) * 2 * 3.3 / 1024;
}

// Retrieve sensor reading with delays before and after to reduce the chance of invalid sensor data
void retryBmeSensorReading() {
  delay(500);
  bme.takeForcedMeasurement();
  delay(500);
}

// Create initialisation packet data
String generateInitPacket() {
  String packet_data = EMPTYPACKET;
  packet_data.setCharAt(0, 'T');
  packet_data.setCharAt(1, '=');
  packet_data.setCharAt(2, 'I');
  packet_data.setCharAt(3, '|');
  return packet_data;
}

// Read sensor values and send to base station
void sendClimateData() {
  Serial.println("Sending climate data");
  char payload_data[] = EMPTYPACKET;
  boolean valid_data = false;

  // Create control data
  char battery_chars[5];
  dtostrf(getBatteryVoltage(), 4, 2, battery_chars);
  payload_data[0] = 'V';
  payload_data[1] = '=';
  payload_data[2] = battery_chars[0];
  payload_data[3] = battery_chars[1];
  payload_data[4] = battery_chars[2];
  payload_data[5] = battery_chars[3];
  payload_data[6] = ',';
  payload_data[7] = 'T';
  payload_data[8] = '=';
  payload_data[9] = 'C';
  payload_data[10] = '|';

  int data_index = 11;

  // Retrieve climate data and put into radio packet payload
  if (bme_status) {
    bme.takeForcedMeasurement();
    boolean valid_temp = false;
    float temp = 0;
    int t_i;
    int t_retries = 3;

    // Attempt to get valid temperature with 3 attempts
    for (t_i = 1; t_i < t_retries; ++t_i) {
      temp = bme.readTemperature();
      if (temp >= -40 && temp <= 85) {
        valid_temp = true;
        t_i = t_retries;
      } else {
        retryBmeSensorReading();
      }
    }
    if (valid_temp) {
      // Place humidity into char array with 2 decimal points
      char temp_chars[5];
      dtostrf(temp, 5, 2, temp_chars);

      // Put temperature data into payload
      payload_data[data_index] = 'T';
      payload_data[data_index+1] = '=';
      payload_data[data_index+2] = temp_chars[0];
      payload_data[data_index+3] = temp_chars[1];
      payload_data[data_index+4] = temp_chars[2];
      payload_data[data_index+5] = temp_chars[3];
      payload_data[data_index+6] = temp_chars[4];
      payload_data[data_index+7] = ',';
      data_index += 8;
      valid_data = true;
    }

    boolean valid_hum = false;
    float hum = 0;
    int h_i;
    int h_retries = 3;

    // Attempt to get valid humditity with 3 attempts
    for (h_i = 1; h_i < h_retries; ++h_i) {
      hum = bme.readHumidity();
      if (hum >= 0 && hum <= 100) {
        valid_hum = true;
        h_i = h_retries;
      } else {
        retryBmeSensorReading();
      }
    }
    if (valid_hum) {
      // Place humidity into char array with 2 decimal points
      char hum_chars[5];
      dtostrf(hum, 5, 2, hum_chars);

      // Put humidity into payload
      payload_data[data_index] = 'H';
      payload_data[data_index+1] = '=';
      payload_data[data_index+2] = hum_chars[0];
      payload_data[data_index+3] = hum_chars[1];
      payload_data[data_index+4] = hum_chars[2];
      payload_data[data_index+5] = hum_chars[3];
      payload_data[data_index+6] = hum_chars[4];
      payload_data[data_index+7] = ',';
      data_index += 8;
      valid_data = true;
    }
    
    boolean valid_pressure = false;
    float pressure = 0;
    int p_i;
    int p_retries = 3;

    // Attempt to get valid humditity with 3 attempts
    for (p_i = 1; p_i < p_retries; ++p_i) {
      pressure = bme.readPressure() / 100.0F;
      if (pressure != null) {
        valid_pressure = true;
        p_i = p_retries;
      } else {
        retryBmeSensorReading();
      }
    }
    if (valid_pressure) {
      // Place pressure into char array with 2 decimal points
      char pressure_chars[7];
      dtostrf(pressure, 7, 2, pressure_chars);

      // Put humidity into payload
      payload_data[data_index] = 'P';
      payload_data[data_index+1] = '=';
      payload_data[data_index+2] = pressure_chars[0];
      payload_data[data_index+3] = pressure_chars[1];
      payload_data[data_index+4] = pressure_chars[2];
      payload_data[data_index+5] = pressure_chars[3];
      payload_data[data_index+6] = pressure_chars[4];
      payload_data[data_index+7] = pressure_chars[5];
      payload_data[data_index+8] = pressure_chars[6];
      data_index += 9;
      valid_data = true;
    }    
  }

  Serial.println(payload_data);

  if (valid_data) {
    // Wake radio
    radio.receiveDone();

    // Send climate data to base station with retries if no ack is receies
    if (radio.sendWithRetry(BASESTATIONID, payload_data, sizeof(payload_data), 3, 500)) {
      Serial.println("Succefully send with ACK");
      processPacket();
    } else {
      Serial.println("Unsucessfull send with no ACK");
    }
  } else {
    Serial.println("Invalid data from sensor");
  }

  // Sleep node until next time period
  if(initialised) {
    radio.sleep();
    long sleep_ms = send_interval;
    micro_sleep(sleep_ms);    
  }
}

// Clears all data in EEPROM
void clearEEPROM() {
  for (int i = 0 ; i < EEPROM.length() ; i++) {
    if(EEPROM.read(i) != 0) {
      EEPROM.write(i, 0);
    }
  }
  Serial.println("EEPROM erased");
}

// Retrieves a stored node ID from EEPROM
int getStoredNodeId() {
  Serial.println("Reading stored node ID");
  if(EEPROM.length()) {
    byte value = EEPROM.read(0);
    if(value != 0) {
      return value;
    }
  }

  // Default to 254 as node ID hasn't been stored
  return 254;
}

// Store node ID into EEPROM
void storeNodeId(int nodeId) {
  clearEEPROM();
  EEPROM.write(0, nodeId);
  Serial.println("Node ID stored");
}

// Handle ACK requests in a packet
void processACK() {
  if (radio.ACKRequested()) {
    radio.sendACK();
  }
}

// Read packet data from radio
void readPacketFromRadio(char packet_data[]) {
  for (byte i = 0; i < radio.DATALEN; i++) {
    char c = radio.DATA[i];
    packet_data[i] = c;
  }
  Serial.println(packet_data);
}

// Process radio packet
void processPacket() {
  int i;
  int retries = 10;
  boolean packet_received = false;

  // Attempt reading packet multiple times
  for (i = 0; i < retries; ++i) {
    Serial.println("Checking for packet");
    if (radio.receiveDone()) {
      Serial.println("Packet received");

      char packet_data[] = EMPTYPACKET;
      readPacketFromRadio(packet_data);

      String packet_type = "";
      String data = packet_data;
      
      int split_index = data.indexOf('|');
      String control_data = data.substring(0, split_index);
      int str_len = control_data.length() + 1;
      char char_array[str_len];
      control_data.toCharArray(char_array, str_len);
      char *control_token = strtok(char_array, ",");
      
      //Process control data in packet
      while (control_token != NULL)
      {
        String token_string = control_token;
        int part_split_index = token_string.indexOf('=');

        String key_string = token_string.substring(0, part_split_index);
        String value_string = token_string.substring(part_split_index + 1);

        // Track packet type
        if (key_string == "T") {
          packet_type = value_string;
          i = retries;
          packet_received = true;
        }

        control_tokenken = strtok(NULL, ",");
      }

      // 
      String main_data = data.substring(split_index + 1);
      int packet_end_split_index = main_data.indexOf('_');
      main_data = main_data.substring(0, packet_end_split_index);
      int main_str_len = main_data.length() + 1;
      char main_char_array[main_str_len];
      main_data.toCharArray(main_char_array, main_str_len);
      char *main_token = strtok(main_char_array, ",");

      //Process main data in packet
      while (main_token != NULL)
      {
        String token_string = main_token;
        int part_split_index = token_string.indexOf('=');

        String key_string = token_string.substring(0, part_split_index);
        String value_string = token_string.substring(part_split_index + 1);

        // Perform actions based on packet data
        if (packet_type == "I" && key_string == "id" && new_node == true) {
          Serial.println("Initial node ID received");
          node_id = value_string.toInt();
          storeNodeId(node_id);
        } else if (packet_type == "T" && key_string == "next") {
          Serial.println("Time period received");
          send_interval = value_string.toInt();
          if(initialised == false) {
            initialised = true;
          }
        } else if(packet_type == "RI") {
          Serial.println("Re-initialisation request received");
          initialised = false;
        }

        main_token = strtok(NULL, ",");
      }
      
      processACK();
    }
    if (!packet_received) {
      delay(250);
    }
  }
}

void initialise() {
  Serial.println("Attempting initialisation");
  long initial_delay = 0;

  int node_id = getStoredNodeId();
  new_node = node_id == 254;
  Serial.println(node_id);
  initRadio(node_id);

  // Create initialisation packet
  String init_packet = generateInitPacket();
  int init_packet_length = init_packet.length() + 1;
  char payload_data[init_packet_length];
  init_packet.toCharArray(payload_data, init_packet_length);

  // Send initialisation packet
  radio.send(BASESTATIONID,  payload_data, sizeof(payload_data), false);
  processPacket();

  // Re-initialise radio with new node ID
  if(new_node) {
    initRadio(node_id);
    radio.sleep();
  } 

  radio.sleep();

  if (initialised == false) {
    Serial.println("Waiting before attempting initialisation again");
    long sleep_ms = initialisation_interval;
    micro_sleep(sleep_ms);
  } else {
    Serial.println("Waiting before the first sensor reading");
    long sleep_ms = send_interval;
    micro_sleep(sleep_ms);
  }
}

// Run the main program loop
void loop() {
  if (initialised) {
    sendClimateData();
  } else {
    initialise();
  }
}


// Sleeps microcontroller by using the largest available sleep period
void micro_sleep(long sleep_ms) {
 do {
    if (sleep_ms > 8000) {
      LowPower.powerDown(SLEEP_8S, ADC_OFF, BOD_OFF);
      sleep_ms-=8000;
    } else if (sleep_ms > 4000) {
      LowPower.powerDown(SLEEP_4S, ADC_OFF, BOD_OFF);
      sleep_ms-=4000;
    } else if (sleep_ms > 2000) {
      LowPower.powerDown(SLEEP_2S, ADC_OFF, BOD_OFF);
      sleep_ms-=2000;
    } else if (sleep_ms > 1000) {
      LowPower.powerDown(SLEEP_1S, ADC_OFF, BOD_OFF);
      sleep_ms-=1000;
    } else if (sleep_ms > 512) {
      LowPower.powerDown(SLEEP_500MS, ADC_OFF, BOD_OFF);
      sleep_ms-=512;
    } else if (sleep_ms > 256) {
      LowPower.powerDown(SLEEP_250MS, ADC_OFF, BOD_OFF);
      sleep_ms-=256;
    } else if (sleep_ms > 128) {
      LowPower.powerDown(SLEEP_120MS, ADC_OFF, BOD_OFF);
      sleep_ms-=128;
    } else if (sleep_ms > 64) {
      LowPower.powerDown(SLEEP_60MS, ADC_OFF, BOD_OFF);
      sleep_ms-=64;
    } else if (sleep_ms > 32) {
      LowPower.powerDown(SLEEP_30MS, ADC_OFF, BOD_OFF);
      sleep_ms-=32;
    } else if (sleep_ms > 16){
      LowPower.powerDown(SLEEP_15MS, ADC_OFF, BOD_OFF);
      sleep_ms-=16;
    } else {
      sleep_ms=0;
    }
  } while(sleep_ms);
}


// Reset the Radio
void resetRadio() {
  Serial.println("Resetting radio");

  // Activate reset
  pinMode(RF69_RESET, OUTPUT);
  digitalWrite(RF69_RESET, HIGH);
  delay(20);

  // Deactivate reset
  digitalWrite(RF69_RESET, LOW);
  delay(500);
  
  Serial.println("Radio reset");
}
