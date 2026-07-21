<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = withDefaults(defineProps<{ lang?: 'en' | 'es' }>(), {
  lang: 'en'
})

const root = ref<HTMLElement | null>(null)
const query = ref('')
const visibleCount = ref(0)
const totalCount = ref(0)

const copy = computed(() => props.lang === 'es'
  ? {
      label: 'Buscar publicaciones',
      placeholder: 'Buscar por título, autor, año, revista o tipo…',
      empty: 'No hay publicaciones que coincidan con la búsqueda.',
      count: (visible: number, total: number) => `${visible} de ${total} publicaciones`
    }
  : {
      label: 'Search publications',
      placeholder: 'Search by title, author, year, journal, or type…',
      empty: 'No publications match your search.',
      count: (visible: number, total: number) => `${visible} of ${total} publications`
    })

function normalize(value: string) {
  return value
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLocaleLowerCase(props.lang)
    .trim()
}

function publicationScope() {
  return root.value?.closest('.VPDoc') ?? root.value?.parentElement ?? null
}

function applyFilter() {
  const scope = publicationScope()
  if (!scope) return

  const needle = normalize(query.value)
  const items = Array.from(scope.querySelectorAll<HTMLElement>('.publication-item'))
  let matches = 0

  for (const item of items) {
    const matchesQuery = !needle || normalize(item.textContent ?? '').includes(needle)
    item.hidden = !matchesQuery
    if (matchesQuery) matches += 1
  }

  for (const list of scope.querySelectorAll<HTMLElement>('.publication-list')) {
    const hasMatches = Array.from(list.querySelectorAll<HTMLElement>('.publication-item'))
      .some(item => !item.hidden)
    list.hidden = !hasMatches
    const heading = list.previousElementSibling
    if (heading instanceof HTMLElement && heading.tagName === 'H2') {
      heading.hidden = !hasMatches
    }
  }

  visibleCount.value = matches
  totalCount.value = items.length
}

watch(query, () => nextTick(applyFilter))
onMounted(applyFilter)
onBeforeUnmount(() => {
  query.value = ''
  applyFilter()
})
</script>

<template>
  <div ref="root" class="publication-search" role="search">
    <label for="publication-search-input">{{ copy.label }}</label>
    <input
      id="publication-search-input"
      v-model="query"
      type="search"
      :placeholder="copy.placeholder"
      :aria-label="copy.label"
      autocomplete="off"
      spellcheck="false"
    >
    <p class="publication-search__status" aria-live="polite">
      {{ visibleCount ? copy.count(visibleCount, totalCount) : copy.empty }}
    </p>
  </div>
</template>
