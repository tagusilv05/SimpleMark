<script setup>
/**
 * FeatureItem — destaque com ícone redondo, título e descrição (ex.: "Agendamento Rápido")
 *
 * COMO USAR (na página):
 *
 *   import FeatureItem from '@/components/shared/FeatureItem.vue'
 *
 *   <FeatureItem
 *     title="Agendamento Rápido"
 *     text="Marque sua consulta em poucos cliques, sem filas ou espera telefônica."
 *     icon="M6.75 3v2.25M17.25 3v2.25..."
 *   />
 *
 * PROPS
 *   title  String  (obrigatória)  título curto.
 *   text   String  (obrigatória)  descrição de uma ou duas linhas.
 *   icon   String  (obrigatória)  caminho "d" de um SVG 24x24 de contorno (ex.: Heroicons).
 *
 * DEPENDÊNCIAS
 *   - Tailwind CSS
 */

defineProps({
  title: { type: String, required: true },
  text: { type: String, required: true },
  icon: { type: String, required: true },
})
</script>

<template>
  <div class="flex flex-col items-center gap-3 text-center">
    <span class="flex size-11 items-center justify-center rounded-full bg-[#e6e9f2] text-[#0b2f5b]">
      <svg
        class="size-5"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        stroke-width="1.5"
        stroke="currentColor"
        aria-hidden="true"
      >
        <path stroke-linecap="round" stroke-linejoin="round" :d="icon" />
      </svg>
    </span>

    <h3 class="text-sm font-semibold text-[#0b2f5b]">{{ title }}</h3>
    <p class="max-w-64 text-xs leading-relaxed text-gray-500">{{ text }}</p>
  </div>
</template>
