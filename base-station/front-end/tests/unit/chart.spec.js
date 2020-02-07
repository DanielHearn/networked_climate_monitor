import { mount } from '@vue/test-utils'
import Chart from './../../src/components/Chart/Chart.js'

describe('Chart.vue', () => {
  it('props', () => {
    const wrapper = mount(Chart, {
      propsData: {
        chartData: {
          labels: ['January', 'February'],
          datasets: [
            {
              label: 'Data One',
              backgroundColor: '#f87979',
              data: [40, 20]
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false
        }
      }
    })
    expect(wrapper.find('#line-chart').exists()).toBe(true)
  })
})
