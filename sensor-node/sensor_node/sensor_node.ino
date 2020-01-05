#include <RFM69.h>
#include <RFM69_ATC.h>
#include <SPIFlash.h>
#include <SPI.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>
#include <LowPower.h>

// Define radio configuration
#define NODEID        2
#define NETWORKID     100
#define FREQUENCY      RF69_433MHZ
#define ENCRYPTKEY     "pnOvzy105sF5g8Ot"
#define BASESTATIONID 1

// Serial board rate - just used to print debug messages
#define SERIAL_BAUD   115200

// Define radio pins
#define RF69_RESET    4
#define RF69_SPI_CS   8
#define RF69_IRQ_PIN  7
#define RF69_IRQ_NUM  4

// Define sensor pins
#define BME_SCK 13
#define BME_MISO 12
#define BME_MOSI 11
#define BME_CS 10

// Define battery pin
#define VBATPIN A9

Adafruit_BME280 bme;
RFM69 radio(RF69_SPI_CS, RF69_IRQ_PIN, false, RF69_IRQ_NUM);

// Define global variables
unsigned bme_status;
boolean initialised = false;
long send_interval = 60000;
long initialisation_interval = 60000;
long loop_drift = 0;
int drift = 1000;

// Setup
void setup() {
  Serial.begin(SERIAL_BAUD);
  Serial.println("Starting sensor node");

  // Reset the radio
  resetRadio();

  // Initialize the radio
  radio.initialize(FREQUENCY, NODEID, NETWORKID);
  radio.promiscuous(false);

  radio.setHighPower();

  // Load BME280 sensor
  bme_status = bme.begin();
  if (!bme_status) {
    Serial.println("Could not find a valid BME280 sensor, check wiring, address, sensor ID!");
    while (1);
  }

  // Change radio power to preserve battery if the radio has good signal with the base station
  #ifdef ENABLE_ATC
    radio.enableAutoPower(ATC_RSSI);
  #endif

  radio.encrypt(ENCRYPTKEY);

  // Delay starting loop so that new programs can be easily uploaded
  delay(20000);
}

// Read battery level and convert it to voltage level
float getBatteryVoltage() {
  return analogRead(VBATPIN) * 2 * 3.3 / 1024;
}

// Read sensor values and send to base station
void sendClimateData() {
  Serial.println("Sending climate data");
  char payload_data[] = "____________________________________________________________";
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
        loop_drift += 100;
        micro_sleep(100);
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
        loop_drift += 100;
        micro_sleep(100);
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
      data_index += 7;
      valid_data = true;
    }
  }

  Serial.println(payload_data);

  if (valid_data) {
    // Wake radio
    radio.receiveDone();

    // Send climate data to base station with retries if no ack is receies
    if (radio.sendWithRetry(BASESTATIONID, payload_data, sizeof(payload_data), 3, 200)) {
      Serial.println("Succefully send with ACK");

      loop_drift += 500;
      delay(500);

      // Check if re-initialisation request recieved
      int i;
      int retries = 3;
      for (i = 0; i < retries; ++i) {
        Serial.println("Checking for re-init packet");
        if (radio.receiveDone()) {
          Serial.println("Packet received");
    
          char packet_data[] = "____________________________________________________________";
          for (byte i = 0; i < radio.DATALEN; i++) {
            char c = radio.DATA[i];
            packet_data[i] = c;
          }

          String data = packet_data;
          int split_index = data.indexOf('|');
          String control_data = data.substring(0, split_index);
          int str_len = control_data.length() + 1;
          char char_array[str_len];
          control_data.toCharArray(char_array, str_len);
          char *token = strtok(char_array, ",");

          while (token != NULL)
          {
            String token_string = token;
            int part_split_index = token_string.indexOf('=');

            String key_string = token_string.substring(0, part_split_index);
            String value_string = token_string.substring(part_split_index + 1);

            if (key_string == "T" && value_string == "RI") {
              Serial.println("Re-initialisation request received");
              initialised = false;
              
              i = retries;
            }

            token = strtok(NULL, ",");
          }
          
          if (radio.ACKRequested()) {
            radio.sendACK();
          }
        }
        if (initialised) {
          loop_drift += 1000;
          delay(1000);
        }
      }

    } else {
      Serial.println("Unsucessfull send with no ACK");
    }
  } else {
    Serial.println("Invalid data from sensor");
  }

  if(initialised) {
    radio.sleep();
    long sleep_ms = send_interval - loop_drift - 16500;
    micro_sleep(sleep_ms);    
  }
}

void initialise() {
  // Wake radio
  radio.receiveDone();

  Serial.println("Attempting initialisation");
  long initial_delay = 0;

  char payload_data[] = "____________________________________________________________";
  payload_data[0] = 'T';
  payload_data[1] = '=';
  payload_data[2] = 'I';
  payload_data[3] = '|';

  Serial.println(payload_data);

  radio.send(BASESTATIONID,  payload_data, sizeof(payload_data), false);

  int i;
  int retries = 3;
  for (i = 0; i < retries; ++i) {
    if (radio.receiveDone()) {
      Serial.println("Received time period packet");
      char packet_data[] = "____________________________________________________________";
      for (byte i = 0; i < radio.DATALEN; i++) {
        char c = radio.DATA[i];
        packet_data[i] = c;
      }

      if (radio.ACKRequested())
      {
        radio.sendACK();
      }

      String data = packet_data;
      int split_index = data.indexOf('|');
      String control_data = data.substring(0, split_index);
      String main_data = data.substring(split_index + 1);

      int packet_end_split_index = main_data.indexOf('_');
      main_data = main_data.substring(0, packet_end_split_index);

      int str_len = main_data.length() + 1;
      char char_array[str_len];
      main_data.toCharArray(char_array, str_len);
      char *token = strtok(char_array, ",");

      while (token != NULL)
      {
        String token_string = token;
        int part_split_index = token_string.indexOf('=');

        String key_string = token_string.substring(0, part_split_index);
        String value_string = token_string.substring(part_split_index + 1);

        if (key_string == "initial") {
          initial_delay = value_string.toInt();
        } else if (key_string == "interval") {
          send_interval = value_string.toInt();
        }

        token = strtok(NULL, ",");
      }

      i = retries;
      initialised = true;
    }
    if (initialised == false) {
      loop_drift += 250;
      delay(250);
    }
  }

  radio.sleep();

  if (initialised == false) {
    Serial.println("Waiting before attempting initialisation again");
    long sleep_ms = initialisation_interval - loop_drift;
    micro_sleep(sleep_ms);
  } else {
    Serial.println("Waiting before the first sensor reading");
    long sleep_ms = initial_delay - loop_drift - 4000;
    micro_sleep(sleep_ms);
  }
}

// Run the main program loop
void loop() {
  loop_drift = 0;
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
