<script setup>
/**
 * BarraAvaliacao — uma linha do resumo: "5 estrelas ▬▬▬▬ 102"
 *
 *   <BarraAvaliacao :stars="5" :count="102" :total="124" />
 */
import { computed } from 'vue'

const props = defineProps({
  stars: { type: Number, required: true },
  count: { type: Number, default: 0 },
  total: { type: Number, default: 0 },
})

const label = computed(() => (props.stars === 1 ? '1 estrela' : `${props.stars} estrelas`))
const pct = computed(() => (props.total > 0 ? Math.round((props.count / props.total) * 100) : 0))
</script>

<template>
  <div class="flex items-center gap-3 text-sm text-gray-700">
    <span class="w-20 shrink-0">{{ label }}</span>

    <div
      class="h-2 flex-1 overflow-hidden rounded-full bg-[#e8effb]"
      role="progressbar"
      :aria-valuenow="pct"
      aria-valuemin="0"
      aria-valuemax="100"
      :aria-label="`${label}: ${count} avaliações`"
    >
      <div class="h-full rounded-full bg-[#0b9aa3]" :style="{ width: pct + '%' }" />
    </div>

    <span class="w-8 text-right font-semibold">{{ count }}</span>
  </div>
</template>
