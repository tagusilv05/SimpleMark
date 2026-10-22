<script setup>
/**
 * StarRating — nota em estrelas (somente leitura) com o valor e o total de avaliações
 *
 * COMO USAR (na página):
 *
 *   import StarRating from '@/components/shared/StarRating.vue'
 *
 *   <StarRating :value="4.9" />                  // ★★★★★ 4.9
 *   <StarRating :value="4.8" :count="82" />      // ★★★★☆ 4.8 (82)
 *   <StarRating :value="null" />                 // sem nota: mostra "Sem avaliações"
 *
 * PROPS
 *   value  Number | null  (padrão: null)
 *            nota de 0 a 5. As estrelas são preenchidas pelo arredondamento
 *            (4.8 -> 5 cheias, 4.4 -> 4 cheias). null/undefined = ainda não avaliado.
 *   count  Number | null  (padrão: null)
 *            total de avaliações, exibido entre parênteses. Sem valor, não aparece.
 *
 * ESTILO
 *   Estrelas na cor turquesa da marca. Tamanho do texto herdado do pai.
 *
 * DEPENDÊNCIAS
 *   - Tailwind CSS
 */

import { computed } from 'vue'

const props = defineProps({
  value: { type: Number, default: null },
  count: { type: Number, default: null },
})

const STAR =
  'M11.48 3.499a.562.562 0 0 1 1.04 0l2.125 5.111a.563.563 0 0 0 .475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 0 0-.182.557l1.285 5.385a.562.562 0 0 1-.84.61l-4.725-2.885a.562.562 0 0 0-.586 0L6.982 20.54a.562.562 0 0 1-.84-.61l1.285-5.386a.562.562 0 0 0-.182-.557l-4.204-3.602a.562.562 0 0 1 .321-.988l5.518-.442a.563.563 0 0 0 .475-.345L11.48 3.5Z'

const hasValue = computed(() => typeof props.value === 'number')
const filled = computed(() => Math.min(5, Math.max(0, Math.round(props.value ?? 0))))
</script>

<template>
  <div
    class="flex items-center justify-center gap-1.5 text-xs"
    :aria-label="hasValue ? `Nota ${value} de 5` : 'Sem avaliações'"
  >
    <template v-if="hasValue">
      <span class="flex items-center gap-0.5" aria-hidden="true">
        <svg
          v-for="n in 5"
          :key="n"
          class="size-3.5 text-[#3f9aa6]"
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          :fill="n <= filled ? 'currentColor' : 'none'"
          stroke="currentColor"
          stroke-width="1.5"
        >
          <path stroke-linejoin="round" :d="STAR" />
        </svg>
      </span>
      <span class="font-bold text-gray-700">{{ value.toFixed(1) }}</span>
      <span v-if="count !== null" class="text-gray-500">({{ count }})</span>
    </template>

    <span v-else class="text-gray-500">Sem avaliações</span>
  </div>
</template>
