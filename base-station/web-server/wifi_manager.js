const wifi = require("node-wifi");
const fetch = require("node-fetch");
 
const storedWifi = {
  ssid: '',
  password: ''
}

const mobileWifi = {
  ssid: 'climate-monitor',
  password: '59556eba6766'
}

const apiRoot = 'http://0.0.0.0/api/'
const apiKey = 'xgLxTX7Nkem5qc9jllg2'
const searchInterval = 30000
let settings_retrieved = false

function searchNetworks() {
  wifi.scan(function(err, networks) {
    if (err) {
      console.log(err);
    } else {
      //console.log(networks)
      const stored_network = networks.filter((network) => network.ssid === storedWifi.ssid)[0]
      const mobile_network = networks.filter((network) => network.ssid === mobileWifi.ssid)[0]
      if(stored_network) {
        console.log('Found stored network')
      }
      if(mobile_network) {
        console.log('Found mobile network')
      }

      // List the current wifi connections
      wifi.getCurrentConnections(function(err, currentConnections) {
        if (err) {
          console.log(err);
        }
        var connected_ssid = null
        if(currentConnections && currentConnections.length) {
            connected_ssid = currentConnections[0].ssid
        }
        console.log(connected_ssid)
        if (stored_network && storedWifi.ssid.length && connected_ssid !== storedWifi.ssid) {
          console.log('Connecting to user\'s network')
          const connectionData = {
            ssid: storedWifi.ssid
          }
          if (storedWifi.password) {
            connectionData.password = storedWifi.password
          }
          console.log(connectionData)
          wifi.connect(connectionData, function(err) {
            if (err) {
              console.log(err);
              if(mobile_network) {
                wifi.connect({ ssid: mobileWifi.ssid, password: mobileWifi.password })
                .then(function() {
                  console.log('Connected')
                })
                .catch(function(error) {
                  console.log(error)
                });
              }
            } else {
              console.log("Connected to user's network");
            }
          });
        } else if(mobile_network && connected_ssid !== storedWifi.ssid && connected_ssid !== mobileWifi.ssid ) {
          console.log('Connecting to mobile network')
          wifi.connect({ ssid: mobileWifi.ssid, password: mobileWifi.password })
              .then(function() {
                console.log('Connected')
              })
              .catch(function(error) {
                console.log(error)
                if(stored_network) {
                  const connectionData = {
                    ssid: storedWifi.ssid
                  }
                  if (storedWifi.password) {
                    connectionData.password = storedWifi.password
                  }
                  console.log(connectionData)
                  wifi.connect(connectionData, function(err) {
                    if (err) {
                      console.log(err);
                    } else {
                      console.log("Connected to user's network");
                    }
                  });
                }
              });
        }
      });
    }
  });
  setTimeout(searchNetworks, searchInterval)
}

async function setupSettingsReloading() {
    setInterval(async ()=> {
      const url = `${apiRoot}base-station-settings?api_key=${apiKey}`
      try {
        const response = await fetch(url)
        const data = await response.json()
        if (data && data.status && data.settings) {
          const settings = JSON.parse(data.settings.replace(/'/g, '"'))
          if (settings.wifi) {
            storedWifi.ssid = settings.wifi.ssid
            storedWifi.password = settings.wifi.password
          }
          console.log(storedWifi)
        } else {
          console.log('Bad response for settings retrieval')
        }
      } catch(e) {
        console.log(e)
      }
    }, 60000)
}

async function loadInitialSettings() {
  const url = `${apiRoot}base-station-settings?api_key=${apiKey}`
  try {
    const response = await fetch(url)
    const data = await response.json()
    if (data && data.status && data.settings) {
      const settings = JSON.parse(data.settings.replace(/'/g, '"'))
      if (settings.wifi) {
        storedWifi.ssid = settings.wifi.ssid
        storedWifi.password = settings.wifi.password
        settings_retrieved = true
        console.log(storedWifi)
        searchNetworks()
        setupSettingsReloading()
      }
    } else {
      console.log('Bad response for settings retrieval')
    }
  } catch(e) {
    console.log(e)
  }
}

function init() {
  wifi.init({
    iface: 'wlan0'
  });
  loadInitialSettings()
  setInterval(() => {
    if(!settings_retrieved) {
      loadInitialSettings()
    }
  }, 60000)
}

init()