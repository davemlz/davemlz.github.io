import { h } from 'vue'
import DefaultTheme from 'vitepress/theme'
import { useData } from 'vitepress'
import PageBanner from './PageBanner.vue'
import PublicationSearch from './PublicationSearch.vue'
import './custom.css'

export default {
  extends: DefaultTheme,
  Layout() {
    const { frontmatter } = useData()

    return h(DefaultTheme.Layout, null, {
      'home-hero-before': () => frontmatter.value.banner
        ? h(PageBanner, {
            src: frontmatter.value.banner.src,
            alt: frontmatter.value.banner.alt
          })
        : null
    })
  },
  enhanceApp({ app }) {
    app.component('PageBanner', PageBanner)
    app.component('PublicationSearch', PublicationSearch)
  }
}
