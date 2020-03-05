#include <RFM69.h>
#include <RFM69_ATC.h>
#include <SPIFlash.h>
#include <SPI.h>
#include <Wire.h>
#include <LowPower.h>

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

// Battery pin
#define VBATPIN A9

// LED pin
#define LEDPIN 13

// Load modules
RFM69_ATC radio(RF69_SPI_CS, RF69_IRQ_PIN, false, RF69_IRQ_NUM);

// Define global variables
int send_interval = 5000;
int target_rssi = -80;
int node_id = 2;

// Setup
void setup() {
  Serial.begin(SERIAL_BAUD);
  Serial.println("Starting sensor node");
  pinMode(LEDPIN, OUTPUT);
  initRadio(node_id);
  // Delay starting loop so that new programs can be easily uploaded
  delay(20000);
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
  //radio.enableAutoPower(target_rssi);
  radio.setPowerLevel(32);
}

// Read battery level and convert it to voltage
float getBatteryVoltage() {
  return analogRead(VBATPIN) * 2 * 3.3 / 1024;
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

// Handle ACK requests in a packet
void processACK() {
  if (radio.ACKRequested()) {
    radio.sendACK();
    digitalWrite(LEDPIN, HIGH);
    delay(500);
    digitalWrite(LEDPIN, LOW);
  }
}

// Process radio packet
void processPacket() {
  int i;
  int retries = 4;
  boolean packet_received = false;

  // Attempt reading packet multiple times
  for (i = 0; i < retries; ++i) {
    Serial.println("Checking for packet");
    if (radio.receiveDone()) {
      Serial.println("Packet received");
      processACK();
      packet_received = true;
    }
    if (!packet_received) {
      delay(250);
    }
  }
}

// Run the main program loop
void loop() {
  // Create initialisation packet
  String init_packet = generateInitPacket();
  int init_packet_length = init_packet.length() + 1;
  char payload_data[init_packet_length];
  init_packet.toCharArray(payload_data, init_packet_length);

  // Send initialisation packet
  radio.send(BASESTATIONID,  payload_data, sizeof(payload_data), false);
  
  processPacket();
  delay(send_interval);
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
