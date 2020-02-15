import { shallowMount } from '@vue/test-utils'
import NotFound from './../../src/views/NotFound.vue'

describe('NotFound.vue', () => {
  let wrapper

  beforeEach(() => {
    wrapper = shallowMount(NotFound, {
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
