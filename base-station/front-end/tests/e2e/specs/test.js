// For authoring Nightwatch tests, see
// https://nightwatchjs.org/guide
const baseUrl = 'http://100.89.161.91'
const email = 'email@email.com'
const password = 'newpassword'

module.exports = {
  'home loads': browser => {
    browser
      .url(baseUrl)
      .waitForElementVisible('body')
      .assert.title('Home - Climate Monitor')
      .end()
  },
  'register loads': browser => {
    browser
      .url(`${baseUrl}/register`)
      .waitForElementVisible('body')
      .assert.title('Register - Climate Monitor')
      .end()
  },
  'login loads': browser => {
    browser
      .url(`${baseUrl}/login`)
      .waitForElementVisible('body')
      .assert.title('Login - Climate Monitor')
      .end()
  },
  'login user': browser => {
    browser
      .url(`${baseUrl}/login`)
      .waitForElementVisible('body')
      .waitForElementPresent('#login', 5000)
      .setValue('[name="email"]', email)
      .setValue('[name="password"]', password)
      .click('[type="submit"]')
      .assert.urlEquals(`${baseUrl}/dashboard`)
      .end()
  },
  'dashboard loads': browser => {
    browser
      .url(`${baseUrl}/dashboard`)
      .waitForElementVisible('body')
      .assert.title('Dashboard - Climate Monitor')
      .end()
  },
  'settings loads': browser => {
    browser
      .url(`${baseUrl}/settings`)
      .waitForElementVisible('body')
      .assert.title('Settings - Climate Monitor')
      .end()
  },
  'change password loads': browser => {
    browser
      .url(`${baseUrl}/reset-password`)
      .waitForElementVisible('body')
      .assert.title('Reset Password - Climate Monitor')
      .end()
  }
}
