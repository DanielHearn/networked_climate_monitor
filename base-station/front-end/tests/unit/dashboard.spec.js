import Vuex from 'vuex'
import { cloneDeep } from 'lodash'
import { mount, createLocalVue } from '@vue/test-utils'
import Dashboard from './../../src/views/Dashboard.vue'
import { storeConfig } from './../../src/store/index.js'
import {
  getSensors,
  getClimateData,
  deleteSensor,
  deleteClimateData,
  patchSensor,
  getTrends
} from './../../src/static/api.js'
import { sub, startOfYesterday, endOfToday, startOfToday } from 'date-fns'

const localVue = createLocalVue()
localVue.use(Vuex)
jest.mock('./../../src/static/api.js')

const multipleSensors = {
  data: {
    status: 'Success',
    sensors: [
      {
        user_id: 1,
        id: 1,
        name: 'Bedroom Sensor',
        recent_climate_data: {
          date: '2020-01-06 11:20',
          sensor_id: 1,
          battery_voltage: 3.99,
          id: 177,
          climate_data: [
            {
              type: 'Temperature',
              id: 353,
              unit: 'c',
              value: 21.22,
              climate_id: 177,
              formattedText: '21.22°C'
            },
            {
              type: 'Humidity',
              id: 354,
              unit: '%',
              value: 40.71,
              climate_id: 177,
              formattedText: '40.71%'
            }
          ]
        },
        historical_data: [],
        config: false,
        editing: false
      },
      {
        user_id: 1,
        id: 2,
        name: 'Kitchen Sensor',
        recent_climate_data: {
          date: '2020-01-26 19:00',
          sensor_id: 2,
          battery_voltage: 3.7,
          id: 178,
          climate_data: [
            {
              type: 'Temperature',
              id: 355,
              unit: 'c',
              value: 23.11,
              climate_id: 178
            },
            {
              type: 'Humidity',
              id: 356,
              unit: '%',
              value: 30,
              climate_id: 178
            }
          ]
        },
        historical_data: [],
        config: false,
        editing: false
      },
      {
        user_id: 1,
        id: 3,
        name: 'Garden Sensor',
        recent_climate_data: {
          date: '2020-01-26 19:00',
          sensor_id: 3,
          battery_voltage: 4.29,
          id: 179,
          climate_data: [
            {
              type: 'Temperature',
              id: 357,
              unit: 'c',
              value: 23.11,
              climate_id: 179
            },
            {
              type: 'Humidity',
              id: 358,
              unit: '%',
              value: 30,
              climate_id: 179
            }
          ]
        },
        historical_data: [],
        config: false,
        editing: false
      }
    ]
  }
}
const historicalData = {
  data: {
    status: 'Success',
    sensors: [
      {
        date: '2020-01-26 19:00',
        sensor_id: 3,
        battery_voltage: 4.29,
        id: 179,
        climate_data: [
          {
            type: 'Temperature',
            id: 357,
            unit: 'c',
            value: 23.11,
            climate_id: 179
          },
          {
            type: 'Humidity',
            id: 358,
            unit: '%',
            value: 30,
            climate_id: 179
          }
        ]
      }
    ]
  }
}
const deleteSensorData = {
  data: {
    status: 'Success'
  }
}
const deleteClimateResponseData = {
  data: {
    status: 'Success'
  }
}
const patchSensorResponseData = {
  data: {
    status: 'Success'
  }
}
const trendResponseData = {
  data: {
    status: 'Success'
  }
}

let wrapper
let store

const factory = () => {
  store = new Vuex.Store(storeConfig)
  store.state.user.logged_in = true
  store.state.user.access_token = '1234'
  store.state.user.refresh_token = '1234'
  store.state.user.email = 'email@email.com'
  store.state.user.settings = {
    temperature_unit: 'c'
  }

  return mount(Dashboard, {
    mocks: {
      $toasted: {
        show: jest.fn()
      },
      $router: {
        push: jest.fn()
      },
      getSensors,
      getClimateData,
      getTrends
    },
    store,
    localVue
  })
}

describe('Dashboard.vue', () => {
  beforeEach(() => {
    wrapper = null
  })

  afterEach(() => {
    wrapper.destroy()
    jest.resetAllMocks()
  })

  it('no sensors', () => {
    const sensorsResponse = {
      status: 'status',
      data: {
        sensors: []
      }
    }
    getSensors.mockResolvedValueOnce(sensorsResponse)
    wrapper = factory()
    expect(wrapper.find('.list').text()).toContain('No sensor nodes created.')
    expect(wrapper.find('.heading').text()).toContain('No sensor selected')
    expect(wrapper.findAll('.list .edit-box').length).toBe(0)
    expect(wrapper.element).toMatchSnapshot()
  })

  it('multiple sensors', async () => {
    const sensorsResponse = cloneDeep(multipleSensors)
    getSensors.mockResolvedValueOnce(sensorsResponse)
    const historicalResponse = cloneDeep(historicalData)
    getClimateData.mockResolvedValueOnce(historicalResponse)
    const trendResponse = cloneDeep(trendResponseData)
    getTrends.mockResolvedValueOnce(trendResponse)

    wrapper = factory()

    await wrapper.vm.$nextTick()

    expect(wrapper.find('.list').text()).not.toContain(
      'No sensor nodes created.'
    )
    expect(wrapper.find('.heading').text()).not.toContain('No sensor selected')
    expect(wrapper.find('.main-panel .sub-heading').text()).toContain(
      'Node 1: Bedroom Sensor'
    )

    const sensorList = wrapper.findAll('.list .edit-box')
    expect(sensorList.length).toBe(3)
    expect(wrapper.element).toMatchSnapshot()
  })

  it('change active sensor', async () => {
    const sensorsResponse = cloneDeep(multipleSensors)
    getSensors.mockResolvedValueOnce(sensorsResponse)
    const historicalResponse = cloneDeep(historicalData)
    getClimateData.mockResolvedValueOnce(historicalResponse)
    const trendResponse = cloneDeep(trendResponseData)
    getTrends.mockResolvedValueOnce(trendResponse)

    wrapper = factory()

    await wrapper.vm.$nextTick()

    expect(wrapper.find('.main-panel .sub-heading').text()).toContain(
      'Node 1: Bedroom Sensor'
    )

    getTrends.mockResolvedValueOnce(trendResponse)
    getClimateData.mockResolvedValueOnce(historicalResponse)
    wrapper
      .findAll('.list .list-item .actions .button--primary')
      .at(1)
      .trigger('click')
    expect(wrapper.find('.main-panel .sub-heading').text()).toContain(
      'Node 2: Kitchen Sensor'
    )

    getTrends.mockResolvedValueOnce(trendResponse)
    getClimateData.mockResolvedValueOnce(historicalResponse)
    wrapper
      .findAll('.list .list-item .actions .button--primary')
      .at(2)
      .trigger('click')
    expect(wrapper.find('.main-panel .sub-heading').text()).toContain(
      'Node 3: Garden Sensor'
    )

    expect(wrapper.element).toMatchSnapshot()
  })

  it('refresh', async () => {
    const sensorsResponse = cloneDeep(multipleSensors)
    getSensors.mockResolvedValueOnce(sensorsResponse)
    const historicalResponse = cloneDeep(historicalData)
    getClimateData.mockResolvedValueOnce(historicalResponse)
    const trendResponse = cloneDeep(trendResponseData)
    getTrends.mockResolvedValueOnce(trendResponse)

    wrapper = factory()

    await wrapper.vm.$nextTick()

    expect(wrapper.find('.main-panel .sub-heading').text()).toContain(
      'Node 1: Bedroom Sensor'
    )

    sensorsResponse.data.sensors.push({
      user_id: 1,
      id: 4,
      name: 'Greenhouse Sensor',
      recent_climate_data: {
        date: '2020-01-06 11:20',
        sensor_id: 1,
        battery_voltage: 3.99,
        id: 177,
        climate_data: [
          {
            type: 'Temperature',
            id: 353,
            unit: 'c',
            value: 21.22,
            climate_id: 177,
            formattedText: '21.22°C'
          },
          {
            type: 'Humidity',
            id: 354,
            unit: '%',
            value: 40.71,
            climate_id: 177,
            formattedText: '40.71%'
          }
        ]
      },
      historical_data: [],
      config: false,
      editing: false
    })
    getSensors.mockResolvedValueOnce(sensorsResponse)
    getClimateData.mockResolvedValueOnce(historicalResponse)
    getTrends.mockResolvedValueOnce(trendResponse)
    wrapper.find('.side-panel .side-panel-header button').trigger('click')

    await wrapper.vm.$nextTick()
    expect(wrapper.find('.main-panel .sub-heading').text()).toContain(
      'Node 1: Bedroom Sensor'
    )

    const sensorList = wrapper.findAll('.list .edit-box')
    expect(sensorList.length).toBe(4)
    expect(wrapper.element).toMatchSnapshot()
  })

  it('delete sensor', async () => {
    const sensorsResponse = cloneDeep(multipleSensors)
    getSensors.mockResolvedValueOnce(sensorsResponse)
    const historicalResponse = cloneDeep(historicalData)
    getClimateData.mockResolvedValueOnce(historicalResponse)
    const deleteResponse = cloneDeep(deleteSensorData)
    deleteSensor.mockResolvedValueOnce(deleteResponse)
    const deleteClimateResponse = cloneDeep(deleteClimateResponseData)
    deleteClimateData.mockResolvedValueOnce(deleteClimateResponse)
    const trendResponse = cloneDeep(trendResponseData)
    getTrends.mockResolvedValueOnce(trendResponse)

    wrapper = factory()

    await wrapper.vm.$nextTick()

    expect(wrapper.findAll('.list .edit-box').length).toBe(3)
    expect(wrapper.find('.main-panel .sub-heading').text()).toContain(
      'Node 1: Bedroom Sensor'
    )

    wrapper
      .find('.list .list-item .actions .button--secondary')
      .trigger('click')
    expect(
      wrapper
        .findAll('.list .list-item .actions')
        .at(1)
        .classes()
    ).toContain('actions--active')
    wrapper
      .findAll('.list .list-item .actions--active .button--tertiary')
      .at(0)
      .trigger('click')

    getClimateData.mockResolvedValueOnce(historicalResponse)
    getTrends.mockResolvedValueOnce(trendResponse)
    await wrapper.vm.$nextTick()

    expect(wrapper.findAll('.list .edit-box').length).toBe(2)
    expect(wrapper.find('.main-panel .sub-heading').text()).toContain(
      'Node 2: Kitchen Sensor'
    )

    expect(wrapper.element).toMatchSnapshot()
  })

  it('delete climate data', async () => {
    const sensorsResponse = cloneDeep(multipleSensors)
    getSensors.mockResolvedValueOnce(sensorsResponse)
    const historicalResponse = cloneDeep(historicalData)
    getClimateData.mockResolvedValueOnce(historicalResponse)
    const deleteResponse = cloneDeep(deleteClimateResponseData)
    deleteClimateData.mockResolvedValueOnce(deleteResponse)
    const trendResponse = cloneDeep(trendResponseData)
    getTrends.mockResolvedValueOnce(trendResponse)

    wrapper = factory()

    await wrapper.vm.$nextTick()

    expect(wrapper.findAll('.list .edit-box').length).toBe(3)
    expect(wrapper.find('.main-panel .sub-heading').text()).toContain(
      'Node 1: Bedroom Sensor'
    )

    wrapper
      .find('.list .list-item .actions .button--secondary')
      .trigger('click')
    expect(
      wrapper
        .findAll('.list .list-item .actions')
        .at(1)
        .classes()
    ).toContain('actions--active')
    wrapper
      .findAll('.list .list-item .actions--active .button--tertiary')
      .at(1)
      .trigger('click')

    getClimateData.mockResolvedValueOnce({ data: { climate_data: [] } })
    getTrends.mockResolvedValueOnce(trendResponse)
    await wrapper.vm.$nextTick()

    expect(wrapper.findAll('.list .edit-box').length).toBe(3)
    expect(wrapper.find('.main-panel .sub-heading').text()).toContain(
      'Node 1: Bedroom Sensor'
    )
    expect(wrapper.find('.main-panel .heading').text()).toContain(
      'Sensor has no climate data.'
    )

    expect(wrapper.element).toMatchSnapshot()
  })

  it('rename sensor', async () => {
    const sensorsResponse = cloneDeep(multipleSensors)
    getSensors.mockResolvedValueOnce(sensorsResponse)
    const historicalResponse = cloneDeep(historicalData)
    getClimateData.mockResolvedValueOnce(historicalResponse)
    const patchSensorResponse = cloneDeep(patchSensorResponseData)
    patchSensor.mockResolvedValueOnce(patchSensorResponse)
    const trendResponse = cloneDeep(trendResponseData)
    getTrends.mockResolvedValueOnce(trendResponse)

    wrapper = factory()

    await wrapper.vm.$nextTick()

    expect(wrapper.findAll('.list .edit-box').length).toBe(3)
    expect(wrapper.find('.main-panel .sub-heading').text()).toContain(
      'Node 1: Bedroom Sensor'
    )

    wrapper
      .find('.list .list-item .edit-box .button--tertiary')
      .trigger('click.native')

    const nameInput = wrapper.find('.list .list-item .edit-box .input--text')
    nameInput.trigger('focus')
    nameInput.setValue('Shed Sensor')
    wrapper.find('.list .list-item .edit-box .button--primary').trigger('click')
    await wrapper.vm.$nextTick()

    expect(wrapper.findAll('.list .edit-box').length).toBe(3)
    expect(wrapper.find('.main-panel .sub-heading').text()).toContain(
      'Node 1: Shed Sensor'
    )
    expect(
      wrapper.find('.side-panel .list .list-item .heading').text()
    ).toContain('Node 1: Shed Sensor')
    expect(wrapper.element).toMatchSnapshot()
  })

  it('historical data time period', async () => {
    const sensorsResponse = cloneDeep(multipleSensors)
    getSensors.mockResolvedValueOnce(sensorsResponse)
    const historicalResponse = cloneDeep(historicalData)
    getClimateData.mockResolvedValueOnce(historicalResponse)
    const trendResponse = cloneDeep(trendResponseData)
    getTrends.mockResolvedValueOnce(trendResponse)

    wrapper = factory()

    await wrapper.vm.$nextTick()

    const periodButtons = wrapper.findAll('.historical-actions .button')
    expect(periodButtons.at(0).classes()).toContain('active')

    expect(wrapper.vm.timePeriod.start).toEqual(startOfToday())
    expect(wrapper.vm.timePeriod.end).toEqual(endOfToday())
    expect(wrapper.vm.historicalRangeType).toBe('1-day')

    getTrends.mockResolvedValueOnce(trendResponse)
    getClimateData.mockResolvedValueOnce(historicalResponse)
    periodButtons.at(1).trigger('click')
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.timePeriod.start).toEqual(startOfYesterday())
    expect(wrapper.vm.timePeriod.end).toEqual(endOfToday())
    expect(wrapper.vm.historicalRangeType).toBe('2-days')
    expect(periodButtons.at(1).classes()).toContain('active')

    getTrends.mockResolvedValueOnce(trendResponse)
    getClimateData.mockResolvedValueOnce(historicalResponse)
    periodButtons.at(2).trigger('click')
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.timePeriod.start).toEqual(
      sub(startOfToday(), { days: 7 })
    )
    expect(wrapper.vm.timePeriod.end).toEqual(endOfToday())
    expect(wrapper.vm.historicalRangeType).toBe('1-week')
    expect(periodButtons.at(2).classes()).toContain('active')

    getTrends.mockResolvedValueOnce(trendResponse)
    getClimateData.mockResolvedValueOnce(historicalResponse)
    periodButtons.at(3).trigger('click')
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.timePeriod.start).toEqual(
      sub(startOfToday(), { months: 1 })
    )
    expect(wrapper.vm.timePeriod.end).toEqual(endOfToday())
    expect(wrapper.vm.historicalRangeType).toBe('1-month')
    expect(periodButtons.at(3).classes()).toContain('active')

    expect(wrapper.element).toMatchSnapshot()
  })
})
