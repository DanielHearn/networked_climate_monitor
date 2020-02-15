import Vuex from 'vuex'
import { shallowMount } from '@vue/test-utils'
import RecentClimateData from './../../src/components/RecentClimateData/RecentClimateData.vue'

describe('RecentClimateData.vue', () => {
  let wrapper

  beforeEach(() => {
    wrapper = shallowMount(RecentClimateData, {
      propsData: {
        recentClimateData: [
          {
            type: 'Temperature',
            value: 23.45,
            unit: 'c'
          },
          {
            type: 'Humidity',
            value: 56.34,
            unit: '%'
          }
        ],
        temperatureUnit: 'c'
      }
    })
  })

  afterEach(() => {
    wrapper.destroy()
    jest.resetAllMocks()
  })

  it('climateData', async () => {
    expect(wrapper.vm.climateData[0].formattedText).toBe('23.45°C')
    expect(wrapper.vm.climateData[1].formattedText).toBe('56.34%')

    wrapper.setProps({ climateData: [] })
    expect(wrapper.findAll('li').length).toBe(2)
  })

  it('has the expected html structure', () => {
    expect(wrapper.element).toMatchSnapshot()
  })
})
