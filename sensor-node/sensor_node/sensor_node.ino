#include <RFM69.h>
#include <RFM69_ATC.h>
#include <SPIFlash.h>
#include <SPI.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>

#define NODEID        2
#define NETWORKID     100

// The transmision frequency of the baord. Change as needed.
#define FREQUENCY      RF69_433MHZ

// Uncomment if this board is the RFM69HW/HCW not the RFM69W/CW
#define IS_RFM69HW_HCW

// Serial board rate - just used to print debug messages
#define SERIAL_BAUD   115200

#define RF69_RESET    4
#define RF69_SPI_CS   8
#define RF69_IRQ_PIN  7
#define RF69_IRQ_NUM  4

#define BME_SCK 13
#define BME_MISO 12
#define BME_MOSI 11
#define BME_CS 10

#define SEALEVELPRESSURE_HPA (1013.25)

#define VBATPIN A9

Adafruit_BME280 bme;
RFM69 radio(RF69_SPI_CS, RF69_IRQ_PIN, false, RF69_IRQ_NUM);
unsigned bme_status;

// Setup
void setup() {
  Serial.begin(115200);
  // Reset the radio
  resetRadio();
  // Initialize the radio
  radio.initialize(FREQUENCY, NODEID, NETWORKID);
  radio.promiscuous(true);
  
  radio.setHighPower(); //must include this only for RFM69HW/HCW!
  radio.setPowerLevel(31);
    
  bme_status = bme.begin();  
  if (!bme_status) {
      Serial.println("Could not find a valid BME280 sensor, check wiring, address, sensor ID!");
      while (1);
  }

  #ifdef ENABLE_ATC
    radio.enableAutoPower(ATC_RSSI);
  #endif
}

float getBatteryVoltage() {
  return analogRead(VBATPIN) * 2 * 3.3 / 1024;
}

// Main loop
unsigned long previousMillis = 0;
const long sendInterval = 10000;

void loop() {
    if (Serial) Serial.println("Sending");
    char payload_data[] = "____________________________________________________________";

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
    if(bme_status) {
      float temp = bme.readTemperature();
      char temp_chars[5];   
      dtostrf(temp, 5, 2, temp_chars);
      char t1 = temp_chars[0];
      payload_data[11] = 'T';
      payload_data[12] = '=';
      payload_data[13] = temp_chars[0];
      payload_data[14] = temp_chars[1];
      payload_data[15] = temp_chars[2];
      payload_data[16] = temp_chars[3];
      payload_data[17] = temp_chars[4];
      payload_data[18] = ',';
      
      float hum = bme.readHumidity();
      char hum_chars[5];   
      dtostrf(hum, 5, 2, hum_chars);
      payload_data[19] = 'H';
      payload_data[20] = '=';
      payload_data[21] = hum_chars[0];
      payload_data[22] = hum_chars[1];
      payload_data[23] = hum_chars[2];
      payload_data[24] = hum_chars[3];
      payload_data[25] = hum_chars[4];
    }

    Serial.println(payload_data);

    if (radio.sendWithRetry(1, payload_data, sizeof(payload_data), 3, 200)) {
      if (Serial) Serial.println("ACK received");
    } else {
      if (Serial) Serial.println("No ACK");
    }

    radio.sleep();
    delay(sendInterval);
}

// Reset the Radio
void resetRadio() {
  if (Serial) Serial.print("Resetting radio...");
  pinMode(RF69_RESET, OUTPUT);
  digitalWrite(RF69_RESET, HIGH);
  delay(20);
  digitalWrite(RF69_RESET, LOW);
  delay(500);
}
