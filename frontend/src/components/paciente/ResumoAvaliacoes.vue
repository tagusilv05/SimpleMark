<script setup>
/**
 * ResumoAvaliacoes — resumo da nota do profissional, em dois formatos
 *
 *   <ResumoAvaliacoes variant="badge" :rating="4.8" :total="124" />
 *       selo compacto "4.8 de 5.0 | ★★★★★ 124 avaliações totais"
 *
 *   <ResumoAvaliacoes variant="full" :rating="4.8" :total="124" :distribution="[...]" />
 *       card grande com a nota e as barras por estrela
 *
 * PROPS
 *   rating        Number  nota média
 *   total         Number  total de avaliações
 *   distribution  Array   [{ stars: 5, count: 102 }, { stars: 4, count: 15 }, ...] (só no "full")
 *   variant       'full' | 'badge'
 *
 * EVENTOS
 *   @ver-avaliacoes  clique no selo badge (a view/layout decide para onde ir)
 */
import EstrelasAvaliacao from '@/components/paciente/EstrelasAvaliacao.vue'
import BarraAvaliacao from '@/components/paciente/BarraAvaliacao.vue'

defineProps({
  rating: { type: Number, required: true },
  total: { type: Number, required: true },
  distribution: { type: Array, default: () => [] },
  variant: { type: String, default: 'full', validator: (v) => ['full', 'badge'].includes(v) },
})

const emit = defineEmits(['ver-avaliacoes'])
</script>

<template>
  <!-- Selo compacto -->
  <button
    v-if="variant === 'badge'"
    type="button"
    class="flex cursor-pointer items-center gap-4 rounded-xl bg-[#eef2fb] px-5 py-3 transition-opacity hover:opacity-70"
    aria-label="Ver todas as avaliações"
    @click="emit('ver-avaliacoes')"
  >
    <div class="text-center leading-tight">
      <p class="text-4xl font-bold text-[#0b2f5b]">{{ Number(rating || 0).toFixed(1) }}</p>
      <p class="text-sm text-gray-500">de 5.0</p>
    </div>

    <div class="h-10 w-px bg-gray-300" />

    <div class="flex flex-col gap-1">
      <EstrelasAvaliacao :rating="rating" size="md" />
      <p class="text-sm font-semibold text-gray-600">{{ total }} avaliações totais</p>
    </div>
  </button>

  <!-- Card completo com barras -->
  <section
    v-else
    class="rounded-xl bg-white p-8 shadow-[0_2px_12px_rgba(11,47,91,0.08)]"
  >
    <h2 class="text-2xl font-semibold text-[#0b2f5b]">Resumo das Avaliações</h2>

    <div class="mt-4 flex items-end gap-3">
      <span class="text-6xl font-bold leading-none text-[#0b2f5b]">{{ Number(rating || 0).toFixed(1) }}</span>
      <div class="flex flex-col gap-1 pb-1">
        <EstrelasAvaliacao :rating="rating" size="md" />
        <span class="text-sm text-gray-500">{{ total }} avaliações totais</span>
      </div>
    </div>

    <div class="mt-6 flex flex-col gap-4">
      <BarraAvaliacao
        v-for="item in distribution"
        :key="item.stars"
        :stars="item.stars"
        :count="item.count"
        :total="total"
      />
    </div>
  </section>
</template>
