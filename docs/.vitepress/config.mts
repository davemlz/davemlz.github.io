import { defineConfig, type DefaultTheme } from 'vitepress'

const scholarIcon = {
  svg: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3 1.5 8.5 12 14l8-4.2V16h2V8.5L12 3Zm-6 9.1V17c2.6 2.7 9.4 2.7 12 0v-4.9L12 15.2 6 12.1Z"/></svg>'
}

const researchGateIcon = {
  svg: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 3h7.2c4.1 0 6.6 2 6.6 5.6 0 2.5-1.3 4.2-3.5 5.1L20 21h-4.6l-4.1-6.5H9V21H5V3Zm4 3.4v4.8h3c1.8 0 2.8-.8 2.8-2.4s-1-2.4-2.8-2.4H9Z"/></svg>'
}

const socialLinks: DefaultTheme.SocialLink[] = [
  { icon: 'github', link: 'https://github.com/davemlz', ariaLabel: 'GitHub' },
  { icon: 'x', link: 'https://x.com/dmlmont', ariaLabel: 'X / Twitter' },
  {
    icon: scholarIcon,
    link: 'https://scholar.google.com/citations?user=-wTpOdsAAAAJ&hl=en',
    ariaLabel: 'Google Scholar'
  },
  {
    icon: researchGateIcon,
    link: 'https://www.researchgate.net/profile/David-Loaiza-2',
    ariaLabel: 'ResearchGate'
  }
]

const englishTheme: DefaultTheme.Config = {
  logo: { src: '/logo.svg', alt: 'David Montero Loaiza' },
  nav: [
    { text: 'Home', link: '/' },
    { text: 'Software', link: '/software' },
    { text: 'Publications', link: '/publications' },
    { text: 'Events', link: '/events' },
    { text: 'Media', link: '/media' }
  ],
  socialLinks,
  search: { provider: 'local' },
  outline: { level: [2, 3], label: 'On this page' },
  docFooter: { prev: 'Previous page', next: 'Next page' },
  lastUpdated: { text: 'Last updated', formatOptions: { dateStyle: 'medium' } },
  footer: {
    message: 'Science, software, and ideas for a changing planet.',
    copyright: 'Built in the open by David Montero Loaiza.'
  }
}

const spanishTheme: DefaultTheme.Config = {
  logo: { src: '/logo.svg', alt: 'David Montero Loaiza' },
  nav: [
    { text: 'Inicio', link: '/es/' },
    { text: 'Software', link: '/es/software' },
    { text: 'Publicaciones', link: '/es/publications' },
    { text: 'Eventos', link: '/es/events' },
    { text: 'Medios', link: '/es/media' }
  ],
  socialLinks,
  search: {
    provider: 'local',
    options: {
      locales: {
        es: {
          translations: {
            button: { buttonText: 'Buscar', buttonAriaLabel: 'Buscar' },
            modal: {
              noResultsText: 'No se encontraron resultados para',
              resetButtonTitle: 'Limpiar búsqueda',
              footer: {
                selectText: 'seleccionar',
                navigateText: 'navegar',
                closeText: 'cerrar'
              }
            }
          }
        }
      }
    }
  },
  outline: { level: [2, 3], label: 'En esta página' },
  docFooter: { prev: 'Página anterior', next: 'Página siguiente' },
  lastUpdated: { text: 'Última actualización', formatOptions: { dateStyle: 'medium' } },
  returnToTopLabel: 'Volver arriba',
  sidebarMenuLabel: 'Menú',
  darkModeSwitchLabel: 'Apariencia',
  langMenuLabel: 'Cambiar idioma',
  footer: {
    message: 'Ciencia, software e ideas para un planeta cambiante.',
    copyright: 'Creado de forma abierta por David Montero Loaiza.'
  }
}

export default defineConfig({
  title: 'David Montero Loaiza',
  description: 'Earth system scientist and open-source software creator.',
  appearance: 'dark',
  cleanUrls: true,
  lastUpdated: true,
  sitemap: { hostname: 'https://davemlz.github.io' },
  head: [
    ['link', { rel: 'icon', type: 'image/svg+xml', href: '/logo.svg' }],
    ['meta', { name: 'theme-color', content: '#000000' }],
    ['meta', { property: 'og:type', content: 'website' }],
    ['meta', { property: 'og:title', content: 'David Montero Loaiza' }],
    ['meta', {
      property: 'og:description',
      content: 'Earth system science, open-source geospatial software, and ideas for a changing planet.'
    }]
  ],
  locales: {
    root: {
      label: 'English',
      lang: 'en',
      themeConfig: englishTheme
    },
    es: {
      label: 'Español',
      lang: 'es',
      title: 'David Montero Loaiza',
      description: 'Científico del sistema Tierra y creador de software de código abierto.',
      themeConfig: spanishTheme
    }
  },
  themeConfig: englishTheme
})
