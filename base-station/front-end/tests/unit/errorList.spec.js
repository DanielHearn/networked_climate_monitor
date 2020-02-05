import { mount } from '@vue/test-utils'
import ErrorList from './../../src/components/ErrorList/ErrorList.vue'

describe('ErrorList.vue', () => {
  it('props', () => {
    const wrapper = mount(ErrorList, {
      propsData: {
        title: 'Errors:',
        errors: ['Error 1', 'Error 2', 'Error 3']
      }
    })

    expect(wrapper.find('.title').exists()).toBe(true)
    expect(wrapper.find('.title').text()).toBe('Errors:')
    const errors = wrapper.findAll('.errors .error')
    expect(errors.length).toBe(3)
    for (let i = 0; i < errors.length; i++) {
      const element = errors.at(i)
      expect(element.text()).toBe(`Error ${i + 1}`)
    }
  })
})
