// For authoring Nightwatch tests, see
// https://nightwatchjs.org/guide
const baseUrl = 'http://127.0.0.1:5000'
const email = 'email@email.com'
const password = 'newpassword'
const newPassword = 'changedpassword'

module.exports = {
  'delete all data': browser => {
    browser
      .url(`${baseUrl}/api/delete-all`)
      .waitForElementVisible('body')
      .end()
  },
  'mobile version loads': browser => {
    browser
      .resizeWindow(600, 800)
      .url(baseUrl)
      .waitForElementVisible('body')
      .assert.title('Home - Climate Monitor')
      .waitForElementPresent('.mobile-menu-button', 5000)
      .end()
  },
  'desktop version loads': browser => {
    browser
      .resizeWindow(1200, 1800)
      .url(baseUrl)
      .waitForElementVisible('body')
      .assert.title('Home - Climate Monitor')
      .waitForElementNotPresent('.mobile-menu-button', 5000)
      .end()
  },
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
  'register user': browser => {
    browser
      .url(`${baseUrl}/register`)
      .waitForElementVisible('body')
      .waitForElementPresent('#register', 5000)
      .setValue('#register [name="email"]', email)
      .setValue('#register [name="password"]', password)
      .setValue('#register [name="confirmPassword"]', password)
      .click('#register [type="submit"]')
      .waitForElementPresent('.register-success', 5000)
      .assert.containsText(
        '.register-success',
        'The account has been successfully registered'
      )
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
  },
  'change password': browser => {
    browser
      .url(`${baseUrl}/reset-password`)
      .waitForElementVisible('body')
      .assert.title('Reset Password - Climate Monitor')
      .waitForElementPresent('#reset-password-form', 5000)
      .setValue('#reset-password-form [name="newPassword"]', newPassword)
      .setValue('#reset-password-form [name="confirmPassword"]', newPassword)
      .click('#reset-password-form [type="submit"]')
      .waitForElementPresent('.new-reset-token', 5000)
      .assert.containsText('New reset token:')
      .end()
  }
}
