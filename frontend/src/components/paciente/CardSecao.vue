<script setup>
/**
 * CardSecao — card branco com ícone + título (usado em "Sobre o Médico" e "Avaliações")
 *
 *   <CardSecao title="Sobre o Médico" :icon="ICONE">
 *     <p>conteúdo...</p>
 *     <template #aside>algo alinhado à direita do título</template>
 *   </CardSecao>
 *
 * PROPS
 *   title  String  título da seção
 *   icon   String  caminho "d" de um SVG 24x24 de contorno (opcional)
 *
 * SLOTS
 *   default  conteúdo do card
 *   aside    área à direita do título (opcional)
 */
defineProps({
  title: { type: String, required: true },
  icon: { type: String, default: '' },
})
</script>

<template>
  <section class="rounded-xl bg-white p-8 shadow-[0_2px_12px_rgba(11,47,91,0.08)]">
    <header class="mb-5 flex flex-wrap items-center justify-between gap-4">
      <h2 class="flex items-center gap-3 text-xl font-semibold text-[#0b2f5b]">
        <svg
          v-if="icon"
          class="size-6 text-[#0b9aa3]"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke-width="1.5"
          stroke="currentColor"
          aria-hidden="true"
        >
          <path stroke-linecap="round" stroke-linejoin="round" :d="icon" />
        </svg>
        {{ title }}
      </h2>

      <slot name="aside" />
    </header>

    <slot />
  </section>
</template>
