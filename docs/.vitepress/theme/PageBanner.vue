<script setup lang="ts">
defineProps<{
  src: string
  alt: string
}>()
</script>

<template>
  <figure class="page-banner" aria-hidden="true">
    <img :src="src" :alt="alt" fetchpriority="high" />
  </figure>
</template>
