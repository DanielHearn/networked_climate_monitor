const url = 'http://127.0.0.1:5000'
const email = 'email@email.com'
const password = 'newpassword'
const newPassword = 'changedpassword'
let resetToken = ''

describe('Climate Monitor', function() {
  it('Delete all data', function() {
    cy.request(`${url}/api/delete-all`)
  })
  it('mobile version loads', function() {
    cy.viewport(550, 750)
    cy.visit(url)
    cy.title().should('eq', 'Home - Climate Monitor')
    cy.get('.mobile-menu-button').should('be.visible')
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
    cy.visit(`${url}/login`)
    cy.title().should('eq', 'Login - Climate Monitor')
  })
  it('login user', function() {
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
  it('settings loads', function() {
    cy.visit(`${url}/settings`)
    cy.title().should('eq', 'Settings - Climate Monitor')
  })
  it('change password loads', function() {
    cy.visit(`${url}/reset-password`)
    cy.title().should('eq', 'Reset Password - Climate Monitor')
  })
  it('change password', function() {
    cy.visit(`${url}/reset-password`)
    cy.get('#reset-password-form [name="resetToken"]').type(resetToken)
    cy.get('#reset-password-form [name="newPassword"]').type(newPassword)
    cy.get('#reset-password-form [name="confirmPassword"]').type(newPassword)
    cy.get('#reset-password-form [type="submit"]').click()
    cy.get('.new-reset-token').contains('New reset token:')
  })
})
