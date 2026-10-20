<script setup>
// label = texto da etiqueta
// icon  = caminho "d" de um SVG 24x24 PREENCHIDO (solid). Sem passar nada,
//         usa o ícone de verificado. icon="" esconde o ícone.
// tone  = cor da etiqueta: 'teal' (padrão, verde-água) | 'danger' (vermelho claro)
defineProps({
  label: { type: String, required: true },
  icon: {
    type: String,
    default:
      'M8.603 3.799A4.49 4.49 0 0 1 12 2.25c1.357 0 2.573.6 3.397 1.549a4.49 4.49 0 0 1 3.498 1.307 4.491 4.491 0 0 1 1.307 3.497A4.49 4.49 0 0 1 21.75 12a4.49 4.49 0 0 1-1.549 3.397 4.491 4.491 0 0 1-1.307 3.497 4.491 4.491 0 0 1-3.497 1.307A4.49 4.49 0 0 1 12 21.75a4.49 4.49 0 0 1-3.397-1.549 4.49 4.49 0 0 1-3.498-1.306 4.491 4.491 0 0 1-1.307-3.498A4.49 4.49 0 0 1 2.25 12c0-1.357.6-2.573 1.549-3.397a4.49 4.49 0 0 1 1.307-3.497 4.49 4.49 0 0 1 3.497-1.307Zm7.007 6.387a.75.75 0 1 0-1.22-.872l-3.236 4.53L9.53 12.22a.75.75 0 0 0-1.06 1.06l2.25 2.25a.75.75 0 0 0 1.14-.094l3.75-5.25Z',
  },
  tone: { type: String, default: 'teal', validator: (v) => ['teal', 'danger'].includes(v) },
})

// Classes completas (o Tailwind precisa enxergar o texto inteiro)
const tones = {
  teal: 'bg-[#0a9ba5] text-white',
  danger: 'bg-red-100 text-red-700',
}
</script>

<template>
  <span
    class="flex items-center gap-0.5 rounded-full px-2.5 py-1.5 text-xs font-bold"
    :class="tones[tone]"
  >
    <svg
      v-if="icon"
      class="size-3.5"
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="currentColor"
      aria-hidden="true"
    >
      <path fill-rule="evenodd" clip-rule="evenodd" :d="icon" />
    </svg>
    {{ label }}
  </span>
</template>