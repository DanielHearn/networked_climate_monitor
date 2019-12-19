from RFM69 import Radio, FREQ_433MHZ
import datetime
import time

node_id = 1
network_id = 100

def ascii_to_string(ascii_array):
  converted_string = ''

  for x in ascii_array:
    converted_string += chr(x)

  return converted_string


with Radio(FREQ_433MHZ, node_id, network_id, isHighPower=True, verbose=False) as radio:
    print ("Starting loop...")
    radio.setPowerLevel(31)
    while True:

        for packet in radio.get_packets():
            print ('-----------------------')
            print ('Packet From: Node: ' + str(packet.sender))
            print ('Signal: ' + str(packet.RSSI))
            print ('Date: ' + str(packet.received))
            print ('Data: ' + ascii_to_string(packet.data))

        delay = 0.1
        time.sleep(delay)