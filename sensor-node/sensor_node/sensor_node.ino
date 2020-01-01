
#include <RFM69.h>
#include <RFM69_ATC.h>
#include <SPIFlash.h>
#include <SPI.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>
#include <Adafruit_SleepyDog.h>

// Define radio configuration
#define NODEID        1
#define NETWORKID     100
#define FREQUENCY      RF69_433MHZ
#define ENCRYPTKEY     "pnOvzy105sF5g8Ot"

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
int drift = 760;

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
}

// Read battery level and convert it to voltage level
float getBatteryVoltage() {
  return analogRead(VBATPIN) * 2 * 3.3 / 1024;
}

void loop() {
  loop_drift = 0;
  if (initialised) {
    // Wake radio
    //radio.receiveDone();

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

    // Create main data
    payload_data[10] = '|';
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
          delay(100);
        }
      }
      if (valid_temp) {
        // Place humidity into char array with 2 decimal points
        char temp_chars[5];
        dtostrf(temp, 5, 2, temp_chars);

        // Put temperature data into payload
        payload_data[11] = 'T';
        payload_data[12] = '=';
        payload_data[13] = temp_chars[0];
        payload_data[14] = temp_chars[1];
        payload_data[15] = temp_chars[2];
        payload_data[16] = temp_chars[3];
        payload_data[17] = temp_chars[4];
        payload_data[18] = ',';
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
          delay(100);
        }
      }
      if (valid_hum) {
        // Place humidity into char array with 2 decimal points
        char hum_chars[5];
        dtostrf(hum, 5, 2, hum_chars);

        // Put humidity into payload
        payload_data[19] = 'H';
        payload_data[20] = '=';
        payload_data[21] = hum_chars[0];
        payload_data[22] = hum_chars[1];
        payload_data[23] = hum_chars[2];
        payload_data[24] = hum_chars[3];
        payload_data[25] = hum_chars[4];
        valid_data = true;
      }
    }

    Serial.println(payload_data);

    if (valid_data) {
      // Send climate data to base station with retries if no ack is receies
      if (radio.sendWithRetry(1, payload_data, sizeof(payload_data), 3, 200)) {
        Serial.println("Succefully send with ACK");

        loop_drift += 500;
        delay(500);

        // Check if re-initialisation request recieved
        int i;
        int retries = 3;
        for (i = 0; i < retries; ++i) {
          Serial.println("Checking for re-init packet");
          if (radio.receiveDone()) {
            Serial.println("Received re-init packet");
        
            Serial.println(radio.DATALEN);
            char packet_data[] = "____________________________________________________________";
            for (byte i = 0; i < radio.DATALEN; i++) {
              char c = radio.DATA[i];
              packet_data[i] = c;
            }

            String data = packet_data;
            Serial.println(data);
            int split_index = data.indexOf('|');
            String control_data = data.substring(0, split_index);
            Serial.println(control_data);
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
                Serial.println("Re-initialisation request");
                initialised = false;
                
                i = retries;
              }

              token = strtok(NULL, ",");
            }
            
            if (radio.ACKRequested())
            {
              radio.sendACK();
            }
          }
          if (initialised) {
            Serial.println("Waiting to check for re-initialisation again");
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
      //radio.sleep();
      delay(send_interval - drift - loop_drift);      
    }


  } else {
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

    radio.send(1,  payload_data, sizeof(payload_data), false);

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
        delay(100);
      }
    }

    //radio.sleep();

    if (initialised == false) {
      Serial.println("Waiting before attempting initialisation again");
      delay(initialisation_interval - drift - loop_drift);
    } else {
      Serial.println("Waiting before the first sensor reading");
      Serial.println(initial_delay - drift - loop_drift);
      delay(initial_delay - (drift/2) - loop_drift);
    }
  }
}

// Reset the Radio
void resetRadio() {
  Serial.println("Resetting radio");
  pinMode(RF69_RESET, OUTPUT);
  digitalWrite(RF69_RESET, HIGH);
  delay(20);
  digitalWrite(RF69_RESET, LOW);
  delay(500);
  Serial.println("Radio reset");
}
