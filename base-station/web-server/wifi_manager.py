from wifi import Cell, Scheme
interface = 'wlan0'
networks = Cell.all(interface)
mobile_ssid = 'climate-monitor'
mobile_password = '59556eba6766'

for network in networks:
    if network.ssid == mobile_ssid:
        print('Found mobile hotspot')
        existing_scheme = Scheme.find(interface, mobile_ssid)
        if existing_scheme:
            print('Loading existing schema')
            existing_scheme.activate()
        else:
            print('Saving schema')
            scheme = Scheme.for_cell(interface, mobile_ssid, network, mobile_password)
            scheme.save()
            scheme.activate()
            print('Connected to mobile hotspot')
print('Finished')
