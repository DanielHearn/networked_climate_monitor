import { mount } from '@vue/test-utils'
import MainPanel from './../../src/components/MainPanel/MainPanel.vue'

describe('MainPanel.vue', () => {
  let wrapper

  afterEach(() => {
    wrapper.destroy()
  })

  it('Header Slot', () => {
    const content = '<p>Header Content</p>'
    wrapper = mount(MainPanel, {
      slots: {
        header: content
      }
    })

    expect(wrapper.html()).toContain(content)
  })

  it('Main Slot', () => {
    const content = '<p>Main Content</p>'
    wrapper = mount(MainPanel, {
      slots: {
        content: content
      }
    })

    expect(wrapper.html()).toContain(content)
  })

  it('Main and Content Slots', () => {
    const mainContent = '<p>Main Content</p>'
    const headerContent = '<p>Header Content</p>'
    wrapper = mount(MainPanel, {
      slots: {
        content: mainContent,
        header: headerContent
      }
    })

    expect(wrapper.html()).toContain(mainContent)
    expect(wrapper.html()).toContain(headerContent)
  })

  it('has the expected html structure', () => {
    expect(wrapper.element).toMatchSnapshot()
  })
})
