import { mount } from '@vue/test-utils'
import vButton from './../../src/components/vButton/vButton.vue'

describe('vButton.vue', () => {
  let wrapper

  afterEach(() => {
    wrapper.destroy()
  })

  it('Text Button', () => {
    let hierachyLevel = 'primary'
    const text = 'Click me'
    wrapper = mount(vButton, {
      propsData: {
        hierachyLevel: hierachyLevel,
        text: text
      }
    })

    expect(wrapper.text()).toBe(text)
    expect(wrapper.classes()).toContain(`button--${hierachyLevel}`)

    hierachyLevel = 'secondary'
    wrapper.setProps({ hierachyLevel: hierachyLevel })
    expect(wrapper.classes()).toContain(`button--${hierachyLevel}`)

    hierachyLevel = 'tertiary'
    wrapper.setProps({ hierachyLevel: hierachyLevel })
    expect(wrapper.classes()).toContain(`button--${hierachyLevel}`)
  })

  it('Icon Button', () => {
    let hierachyLevel = 'primary'
    const text = 'close'
    wrapper = mount(vButton, {
      propsData: {
        hierachyLevel: hierachyLevel,
        text: text,
        isIcon: true
      }
    })

    expect(wrapper.find('i').text()).toBe(text)
    expect(wrapper.classes()).toContain(`button--${hierachyLevel}`)

    hierachyLevel = 'secondary'
    wrapper.setProps({ hierachyLevel: hierachyLevel })
    expect(wrapper.classes()).toContain(`button--${hierachyLevel}`)

    hierachyLevel = 'tertiary'
    wrapper.setProps({ hierachyLevel: hierachyLevel })
    expect(wrapper.classes()).toContain(`button--${hierachyLevel}`)
  })

  it('has the expected html structure', () => {
    expect(wrapper.element).toMatchSnapshot()
  })
})
