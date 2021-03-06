import { mount } from '@vue/test-utils'
import SidePanel from './../../src/components/SidePanel/SidePanel.vue'

describe('SidePanel.vue', () => {
  let wrapper

  afterEach(() => {
    wrapper.destroy()
  })

  it('Header Slot', () => {
    const content = '<p>Header Content</p>'
    wrapper = mount(SidePanel, {
      slots: {
        header: content
      }
    })

    expect(wrapper.html()).toContain(content)
  })

  it('Main Slot', () => {
    const content = '<p>Main Content</p>'
    wrapper = mount(SidePanel, {
      slots: {
        content: content
      }
    })

    expect(wrapper.html()).toContain(content)
  })

  it('Main and Content Slots', () => {
    const mainContent = '<p>Main Content</p>'
    const headerContent = '<p>Header Content</p>'
    wrapper = mount(SidePanel, {
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
