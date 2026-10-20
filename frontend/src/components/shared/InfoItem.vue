<script setup>
// icon = caminho (atributo "d") de um SVG de 24x24, estilo contorno
defineProps({
  icon: { type: String, required: true },
})
</script>

<template>
  <span class="inline-flex items-center gap-1.5 text-sm font-semibold text-gray-600">
    <svg
      class="size-4 shrink-0"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      stroke-width="1.5"
      stroke="currentColor"
      aria-hidden="true"
    >
      <path stroke-linecap="round" stroke-linejoin="round" :d="icon" />
    </svg>
    <slot />
  </span>
</template>
