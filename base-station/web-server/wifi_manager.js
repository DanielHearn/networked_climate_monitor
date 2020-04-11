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
const searchInterval = 120000
let settings_retrieved = false

function searchNetworks() {
  // List the current wifi connections
  wifi.getCurrentConnections(function(err, currentConnections) {
    if (err) {
      console.log(err);
    }
    var connected_ssid = null
    if(currentConnections && currentConnections.length) {
        connected_ssid = currentConnections[0].ssid
    }
    
    if (connected_ssid) {
      wifi.scan(function(err, networks) {
        if (err) {
          console.log(err);
        } else {
          const storedNetwork = networks.filter((network) => network.ssid === storedWifi.ssid)[0]
          const mobileNetwork = networks.filter((network) => network.ssid === mobileWifi.ssid)[0]
          if(storedNetwork) {
            console.log('Found stored network')
          }
          if(mobileNetwork) {
            console.log('Found mobile network')
          }

          if (storedNetwork && storedWifi.ssid.length && connected_ssid !== storedWifi.ssid) {
            connectToUserNetwork(storedNetwork, mobileNetwork)
          } else if(mobileNetwork && connected_ssid !== storedWifi.ssid && connected_ssid !== mobileWifi.ssid ) {
            connectToMobileNetwork(storedNetwork, mobileNetwork)
          }
        }
      });
    }
  });
}

function connectToUserNetwork(mobileNetwork) {
  console.log('Connecting to user\'s network')
  const connectionData = {
    ssid: storedWifi.ssid
  }
  if (storedWifi.password) {
    connectionData.password = storedWifi.password
  }
  wifi.connect(connectionData, function(err) {
    if (err) {
      console.log(err);
      if(mobileNetwork) {
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
}

function connectToMobileNetwork(storedNetwork) {
  console.log('Connecting to mobile network')
  wifi.connect({ ssid: mobileWifi.ssid, password: mobileWifi.password })
  .then(function() {
    console.log('Connected')
  })
  .catch(function(error) {
    console.log(error)
    if(storedNetwork) {
      const connectionData = {
        ssid: storedWifi.ssid
      }
      if (storedWifi.password) {
        connectionData.password = storedWifi.password
      }
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

async function loadSettings() {
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
  loadSettings()
  setInterval(() => {
    loadSettings()
  }, searchInterval)
}

init()