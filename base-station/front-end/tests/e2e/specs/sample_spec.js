const url = 'http://127.0.0.1:5000'
const email = 'email@email.com'
const password = 'newpassword'
const newPassword = 'changedpassword'
let resetToken = ''

describe('Climate Monitor', function() {
  before(function() {
    cy.clearLocalStorageCache()
  })

  beforeEach(() => {
    cy.restoreLocalStorageCache()
  })

  afterEach(() => {
    cy.saveLocalStorageCache()
  })

  it('Delete all data', function() {
    cy.request(`${url}/api/delete-all`)
  })
  it('mobile version loads', function() {
    cy.viewport(550, 750)
    cy.visit(url)
    cy.title().should('eq', 'Home - Climate Monitor')
    cy.get('.mobile-menu-button').should('be.visible')
  })
  it('mobile menu toggles', function() {
    cy.viewport(550, 750)
    cy.visit(url)
    cy.get('.mobile-menu-button').click()
    cy.get('.mobile-menu').should('be.visible')
    cy.get('.mobile-menu-button').click()
    cy.get('.mobile-menu').should('not.be.visible')
    cy.get('.mobile-menu-button').click()
    cy.get('.mobile-menu').should('be.visible')
    cy.get('.mobile-menu .link[href="/login"]').click()
    cy.get('.mobile-menu').should('not.be.visible')
    cy.url().should('eq', `${url}/login`)
    cy.title().should('eq', 'Login - Climate Monitor')
  })
  it('desktop version loads', function() {
    cy.viewport(1920, 1080)
    cy.visit(url)
    cy.title().should('eq', 'Home - Climate Monitor')
    cy.get('.mobile-menu-button').should('not.be.visible')
  })
  it('home loads', function() {
    cy.visit(url)
    cy.title().should('eq', 'Home - Climate Monitor')
  })
  it('register loads', function() {
    cy.visit(`${url}/register`)
    cy.title().should('eq', 'Register - Climate Monitor')
  })
  it('register error', function() {
    cy.clearLocalStorageCache()
    cy.visit(`${url}/register`)
    cy.get('#register [name="email"]').type(email)
    cy.get('#register [name="password"]').type('password')
    cy.get('#register [name="confirmPassword"]').type('wrongpassword')
    cy.get('#register [type="submit"]').click()
    cy.get('.error-list').contains(
      'Password and confirm password should be identical.'
    )
    cy.url().should('eq', `${url}/register`)
  })
  it('register user', function() {
    cy.visit(`${url}/register`)
    cy.get('#register [name="email"]').type(email)
    cy.get('#register [name="password"]').type(password)
    cy.get('#register [name="confirmPassword"]').type(password)
    cy.get('#register [type="submit"]').click()
    cy.get('.register-success').should(
      'contain',
      'The account has been successfully registered'
    )
    cy.get('.reset-token').then($element => {
      resetToken = $element.text().split(': ')[1]
    })
  })
  it('login loads', function() {
    cy.clearLocalStorageCache()
    cy.visit(`${url}/login`)
    cy.title().should('eq', 'Login - Climate Monitor')
  })
  it('login error', function() {
    cy.clearLocalStorageCache()
    cy.visit(`${url}/login`)
    cy.get('#login [name="email"]').type('wrongemail@email.com')
    cy.get('#login [name="password"]').type('wrongpassword')
    cy.get('#login [type="submit"]').click()
    cy.get('.error-list').contains('Email or password is incorrect')
    cy.url().should('eq', `${url}/login`)
  })
  it('login user', function() {
    cy.clearLocalStorageCache()
    cy.visit(`${url}/login`)
    cy.get('#login [name="email"]').type(email)
    cy.get('#login [name="password"]').type(password)
    cy.get('#login [type="submit"]').click()
    cy.url().should('eq', `${url}/dashboard`)
  })
  it('dashboard loads', function() {
    cy.visit(`${url}/dashboard`)
    cy.title().should('eq', 'Dashboard - Climate Monitor')
  })
  it('dashboard climate data', function() {
    cy.visit(`${url}/dashboard`)
    cy.title().should('eq', 'Dashboard - Climate Monitor')
    cy.get('.side-panel .list .list-item').should('have.length', 3)
    cy.get('.side-panel .list .list-item.active').contains('Node 1: Sensor 1')
    cy.get('.side-panel .list .list-item.active').contains(
      'Temperature: 23.24°C'
    )
    cy.get('.side-panel .list .list-item.active').contains(
      'Date received: 2020-01-17 16:30'
    )
    cy.get('.main-panel .sub-heading').contains('Node 1: Sensor 1')
    cy.get('.main-panel .recent-data-list').contains('Temperature')
    cy.get('.main-panel .recent-data-list').contains('23.24°C')
    cy.get('.main-panel .historical-chart').should('have.length', 2)
    cy.get('.main-panel .historical-chart').contains('Battery Level')
    cy.get('.main-panel .historical-chart').contains('Temperature')

    cy.get('.historical-actions button')
      .eq(1)
      .click()
    cy.get('.main-panel .historical-chart').should('have.length', 2)
    cy.get('.main-panel .historical-chart').contains('Battery Level')
    cy.get('.main-panel .historical-chart').contains('Temperature')

    cy.get('.historical-actions button')
      .eq(2)
      .click()
    cy.get('.main-panel .historical-chart').should('have.length', 2)
    cy.get('.main-panel .historical-chart').contains('Battery Level')
    cy.get('.main-panel .historical-chart').contains('Temperature')

    cy.get('.historical-actions button')
      .eq(3)
      .click()
    cy.get('.main-panel .historical-chart').should('have.length', 2)
    cy.get('.main-panel .historical-chart').contains('Battery Level')
    cy.get('.main-panel .historical-chart').contains('Temperature')

    cy.get('.side-panel .list .list-item')
      .eq(1)
      .find('.button--primary')
      .click()
    cy.get('.side-panel .list .list-item.active').contains('Node 2: Sensor 2')
    cy.get('.side-panel .list .list-item.active').contains(
      'No climate data for this sensor'
    )
    cy.get('.main-panel .sub-heading').contains('Node 2: Sensor 2')
    cy.get('.main-panel').contains('Sensor has no climate data.')
  })
  it('dashboard mobile climate data', function() {
    cy.viewport(550, 750)
    cy.visit(`${url}/dashboard`)
    cy.title().should('eq', 'Dashboard - Climate Monitor')
    cy.get('.side-panel .list .list-item').should('have.length', 3)

    cy.get('.side-panel .list .list-item').contains('Node 1: Sensor 1')
    cy.get('.side-panel .list .list-item').contains('Temperature: 23.24°C')
    cy.get('.side-panel .list .list-item').contains(
      'Date received: 2020-01-17 16:30'
    )

    cy.get('.side-panel .list .list-item')
      .eq(0)
      .find('.button--primary')
      .click()

    cy.get('.main-panel .sub-heading').contains('Node 1: Sensor 1')
    cy.get('.main-panel .recent-data-list').contains('Temperature')
    cy.get('.main-panel .recent-data-list').contains('23.24°C')
    cy.get('.main-panel .historical-chart').should('have.length', 2)
    cy.get('.main-panel .historical-chart').contains('Battery Level')
    cy.get('.main-panel .historical-chart').contains('Temperature')

    cy.get('.main-panel .back-button').click()
    cy.get('.side-panel .list .list-item')
      .eq(1)
      .find('.button--primary')
      .click()
    cy.get('.main-panel .sub-heading').contains('Node 2: Sensor 2')
    cy.get('.main-panel').contains('Sensor has no climate data.')
  })
  it('dashboard rename sensor', function() {
    cy.visit(`${url}/dashboard`)
    cy.get('.side-panel .list .list-item').should('have.length', 3)
    cy.get('.side-panel .list .list-item.active .edit-box .button').click()
    const nameInput = cy.get(
      '.side-panel .list .list-item.active .edit-box .input--text'
    )
    nameInput
      .clear()
      .type('Garden Sensor')
      .blur()
    cy.get('.side-panel .list .list-item').should('have.length', 3)
    cy.get('.side-panel .list .list-item.active').contains(
      'Node 1: Garden Sensor'
    )
    cy.get('.main-panel .sub-heading').contains('Node 1: Garden Sensor')
  })
  it('settings loads', function() {
    cy.visit(`${url}/settings`)
    cy.title().should('eq', 'Settings - Climate Monitor')
    cy.wait(200)
    cy.get('.input-box').contains('Temperature Unit:')
  })
  it('settings change category', function() {
    cy.visit(`${url}/settings`)
    cy.get('.side-panel .list .list-item.active').contains(
      'Measurement Settings'
    )
    cy.get('.side-panel .list .list-item')
      .eq(1)
      .find('.button--primary')
      .click()
    cy.get('.side-panel .list .list-item.active').contains('Account Management')
    cy.get('.main-panel').contains(`Reset Token: ${resetToken}`)
  })
  it('settings mobile', function() {
    cy.viewport(550, 750)
    cy.visit(`${url}/settings`)
    cy.get('.side-panel .list .list-item').contains('Measurement Settings')
    cy.get('.side-panel .list .list-item')
      .eq(0)
      .find('.button--primary')
      .click()
    cy.get('.radio-option.active label[for="temp_unit_c"]').should('be.visible')
    cy.get('.main-panel').contains(
      'Temperatures are stored in celsius and will be displayed in celsius'
    )
    cy.get('.back-button').click()
    cy.get('.side-panel .list .list-item')
      .eq(1)
      .find('.button--primary')
      .click()
    cy.get('.main-panel').contains(`Reset Token: ${resetToken}`)
  })
  it('change temperature unit', function() {
    cy.visit(`${url}/settings`)
    cy.get('.radio-option.active label[for="temp_unit_c"]').should('be.visible')
    cy.get('label[for="temp_unit_f"]').click()
    cy.get('.radio-option.active label[for="temp_unit_f"]').should('be.visible')
    cy.get('.main-panel').contains(
      'Temperatures are stored in celsius and will be displayed in farenheit'
    )
  })
  it('fahrenheit temperature data', function() {
    cy.visit(`${url}/dashboard`)
    cy.title().should('eq', 'Dashboard - Climate Monitor')
    cy.get('.side-panel .list .list-item').should('have.length', 3)
    cy.get('.side-panel .list .list-item.active').contains(
      'Node 1: Garden Sensor'
    )
    cy.get('.side-panel .list .list-item.active').contains(
      'Temperature: 73.83°F'
    )
    cy.get('.side-panel .list .list-item.active').contains(
      'Date received: 2020-01-17 16:30'
    )
    cy.get('.main-panel .sub-heading').contains('Node 1: Garden Sensor')
    cy.get('.main-panel .recent-data-list').contains('Temperature')
    cy.get('.main-panel .recent-data-list').contains('73.83°F')
  })
  it('dashboard delete data', function() {
    cy.visit(`${url}/dashboard`)
    cy.get('.side-panel .list .list-item').should('have.length', 3)
    cy.get(
      '.side-panel .list .list-item.active .actions .button--secondary'
    ).click()
    cy.get(
      '.side-panel .list .list-item.active .actions--active .button--tertiary'
    )
      .eq(1)
      .click()
    cy.get('.side-panel .list .list-item').should('have.length', 3)
    cy.get('.side-panel .list .list-item.active').contains(
      'No climate data for this sensor'
    )
    cy.get('.main-panel').contains('Sensor has no climate data.')
  })
  it('dashboard delete sensor', function() {
    cy.visit(`${url}/dashboard`)
    cy.get('.side-panel .list .list-item').should('have.length', 3)
    cy.get(
      '.side-panel .list .list-item.active .actions .button--secondary'
    ).click()
    cy.get(
      '.side-panel .list .list-item.active .actions--active .button--tertiary'
    )
      .eq(0)
      .click()
    cy.get('.side-panel .list .list-item').should('have.length', 2)
    cy.get('.side-panel .list .list-item.active').contains('Node 2: Sensor 2')
  })
  it('change password loads', function() {
    cy.visit(`${url}/reset-password`)
    cy.title().should('eq', 'Reset Password - Climate Monitor')
  })
  it('logout', function() {
    cy.visit(`${url}/dashboard`)
    cy.get('.logout-button').click()
    cy.url().should('eq', `${url}/`)
  })
  it('change password', function() {
    cy.visit(`${url}/reset-password`)
    cy.get('#reset-password-form [name="resetToken"]').type(resetToken)
    cy.get('#reset-password-form [name="newPassword"]').type(newPassword)
    cy.get('#reset-password-form [name="confirmPassword"]').type(newPassword)
    cy.get('#reset-password-form [type="submit"]').click()
    cy.get('.new-reset-token').contains('New reset token:')
  })
  it('change password error', function() {
    cy.visit(`${url}/reset-password`)
    cy.get('#reset-password-form [name="resetToken"]').type('wrongtoken')
    cy.get('#reset-password-form [name="newPassword"]').type(newPassword)
    cy.get('#reset-password-form [name="confirmPassword"]').type(newPassword)
    cy.get('#reset-password-form [type="submit"]').click()
    cy.get('.error-list').contains('Reset token: Length must be 20')
    cy.get('.new-reset-token').should('not.be.visible')
  })
})
