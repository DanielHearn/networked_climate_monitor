import { shallowMount } from '@vue/test-utils'
import Home from './../../src/views/Home.vue'

describe('Home.vue', () => {
  let wrapper

  beforeEach(() => {
    wrapper = shallowMount(Home, {
      stubs: ['router-link']
    })
  })

  afterEach(() => {
    wrapper.destroy()
    jest.resetAllMocks()
  })

  it('has the expected html structure', () => {
    expect(wrapper.element).toMatchSnapshot()
  })
})
