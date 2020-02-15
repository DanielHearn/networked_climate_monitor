const fs = require('fs-extra')

// Async/Await:
function copyFiles() {
  fs.remove('./../web-server/template/index.html')
    .then(() => {
      console.log('Deleted existing index.html')
      fs.copy('./dist/index.html', './../web-server/templates/index.html')
        .then(() => {
          console.log('Copied index.html')
        })
        .catch(err => {
          console.error(err)
        })
    })
    .catch(err => {
      console.error(err)
    })
  fs.remove('./../web-server/static')
    .then(() => {
      console.log('Deleted existing static')
      fs.copy('./dist/static', './../web-server/static')
        .then(() => {
          console.log('Copied static')
          fs.copy('./dist/favicon.ico', './../web-server/static/favicon.ico')
            .then(() => {
              console.log('Copied favicon')
            })
            .catch(err => {
              console.error(err)
            })
        })
        .catch(err => {
          console.error(err)
        })
    })
    .catch(err => {
      console.error(err)
    })
}

copyFiles()
