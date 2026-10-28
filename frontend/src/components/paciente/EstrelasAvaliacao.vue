<script setup>
/**
 * EstrelasAvaliacao — estrelas com suporte a meia estrela (4.8, 4.5, 3.2...)
 *
 *   <EstrelasAvaliacao :rating="4.8" size="md" />
 *
 * PROPS
 *   rating  Number  nota (0 até max)
 *   max     Number  quantidade de estrelas (padrão 5)
 *   size    'sm' | 'md' | 'lg'
 */
import { computed } from 'vue'

const props = defineProps({
  rating: { type: Number, default: 0 },
  max: { type: Number, default: 5 },
  size: { type: String, default: 'md', validator: (v) => ['sm', 'md', 'lg'].includes(v) },
})

const STAR =
  'M10.788 3.21c.448-1.077 1.976-1.077 2.424 0l2.082 5.006 5.404.434c1.164.093 1.636 1.545.749 2.305l-4.117 3.527 1.257 5.273c.271 1.136-.964 2.033-1.96 1.425L12 18.354 7.373 21.18c-.996.608-2.231-.29-1.96-1.425l1.257-5.273-4.117-3.527c-.887-.76-.415-2.212.749-2.305l5.404-.434 2.082-5.005Z'

const sizeClass = computed(() => ({ sm: 'size-3.5', md: 'size-5', lg: 'size-6' })[props.size])

// Porcentagem de preenchimento de cada estrela: 4.8 -> [100, 100, 100, 100, 80]
const fills = computed(() =>
  Array.from({ length: props.max }, (_, i) =>
    Math.round(Math.min(Math.max(props.rating - i, 0), 1) * 100),
  ),
)
</script>

<template>
  <span
    class="inline-flex items-center gap-0.5"
    role="img"
    :aria-label="`${rating} de ${max} estrelas`"
  >
    <span v-for="(pct, i) in fills" :key="i" class="relative inline-block shrink-0" :class="sizeClass">
      <!-- estrela vazia (fundo) -->
      <svg
        class="absolute inset-0 size-full text-gray-300"
        viewBox="0 0 24 24"
        fill="currentColor"
        aria-hidden="true"
      >
        <path :d="STAR" />
      </svg>
      <!-- estrela cheia, cortada na porcentagem -->
      <span class="absolute inset-y-0 left-0 overflow-hidden" :style="{ width: pct + '%' }">
        <svg
          class="max-w-none shrink-0 text-[#0b9aa3]"
          :class="sizeClass"
          viewBox="0 0 24 24"
          fill="currentColor"
          aria-hidden="true"
        >
          <path :d="STAR" />
        </svg>
      </span>
    </span>
  </span>
</template>
