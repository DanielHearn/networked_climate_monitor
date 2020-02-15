<template>
  <main-panel>
    <template slot="content">
      <div class="content-column">
        <h1 class="title">Climate Monitor</h1>
        <h2 class="heading">Account Registration</h2>
        <template v-if="!$store.state.user.email">
          <p class="text">
            Enter an email and password to register the account.
          </p>
          <register-form />
          <router-link to="/login" class="link"
            >Already registered? Click here to login</router-link
          >
        </template>
        <template v-else>
          <p class="text bold register-success">
            The account has been successfully registered
          </p>
          <p class="text">
            Complete the setup instructions to start using the climate monitor
            system.
          </p>
          <ol class="ordered-list">
            <li>
              <p class="text">
                Save the reset token below into a safe location such as in a
                text file or on paper. This token will be required to change or
                reset the account's password.
              </p>
              <span class="text bold reset-token"
                >Reset token: {{ $store.state.user.reset_token }}</span
              >
            </li>
            <li>
              <p class="text">
                Connect each sensor node to their battery.
              </p>
            </li>
            <li>
              <p class="text">
                Plugin each sensor node's micro usb port to a USB port with a
                USB cable to charge the node's battery until the battery level
                on the dashboard is "High".
              </p>
            </li>
            <li>
              <p class="text">
                Once the sensor nodes have been fully charged place the nodes in
                the areas that will be monitored.
              </p>
            </li>
            <li>
              <p class="text">
                If the sensor nodes or climate data aren't appearing in the
                dashboard move the nodes closer to the base station so that they
                can communicate.
              </p>
            </li>
          </ol>
          <router-link to="/dashboard" class="link"
            >Completed the setup? Click here to view the dashboard</router-link
          >
        </template>
      </div>
    </template>
  </main-panel>
</template>

<script>
import MainPanel from './../components/MainPanel/MainPanel.vue'
import RegisterForm from './../components/RegisterForm/RegisterForm.vue'

export default {
  name: 'register',
  components: {
    MainPanel,
    RegisterForm
  }
}
</script>
