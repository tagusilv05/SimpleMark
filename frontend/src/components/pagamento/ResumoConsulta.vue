<script setup>
/**
 * ResumoConsulta — resumo da consulta na tela de pagamento (dados vindos de
 * GET /consultas/minhas/{id}) e o botão que abre o checkout.
 */
defineProps({
  profissional: { type: String, default: '' },
  especialidade: { type: String, default: '' },
  data: { type: String, default: '' },
  horario: { type: String, default: '' },
  tipo: { type: String, default: '' },
  valor: { type: String, default: '' },
  metodo: { type: String, default: '' },
  imagem: { type: String, default: '' },
  disponivel: { type: Boolean, default: false },
  processando: { type: Boolean, default: false },
  rotuloBotao: { type: String, default: 'Finalizar Pagamento' },
})
const emit = defineEmits(['finalizar'])

const iniciais = (nome) =>
  (nome ?? '')
    .replace(/^dra?\.?\s+/i, '')
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((p) => p[0].toUpperCase())
    .join('')
</script>

<template>
  <section class="min-h-[310px] rounded-xl bg-white p-6 shadow-[0_4px_18px_rgba(12,48,92,0.08)]">
    <h2 class="border-b border-[#d1d7de] pb-2 text-lg font-semibold text-[#073b57]">Resumo da Consulta</h2>
    <div class="mt-4 flex items-center gap-3">
      <div class="flex size-12 shrink-0 items-center justify-center rounded-md bg-[#0b2f5b] text-sm font-bold text-white">
        <img v-if="imagem" :src="imagem" :alt="`Foto de ${profissional}`" class="size-full rounded-md object-cover" />
        <span v-else>{{ iniciais(profissional) }}</span>
      </div>
      <div class="text-xs"><p class="font-medium text-[#173c5b]">{{ profissional || '—' }}</p><p class="text-[#59636d]">{{ especialidade }}</p></div>
    </div>
    <dl class="mt-4 space-y-3 text-xs text-[#59636d]">
      <div class="flex gap-2"><dt class="text-[#00a9c5]" aria-label="Data">▣</dt><dd>{{ data || '—' }}</dd></div>
      <div class="flex gap-2"><dt class="text-[#00a9c5]" aria-label="Horário">◷</dt><dd>{{ horario || '—' }}</dd></div>
      <div class="flex gap-2"><dt class="text-[#00a9c5]" aria-label="Local">⌖</dt><dd>Teleconsulta por vídeo<span v-if="tipo"> · {{ tipo }}</span></dd></div>
      <div v-if="metodo" class="flex gap-2"><dt class="text-[#00a9c5]" aria-label="Forma de pagamento">$</dt><dd>{{ metodo }}</dd></div>
    </dl>
    <div class="mt-6 flex items-center justify-between border-t border-dashed border-[#d1d7de] pt-3"><span class="text-xs text-[#59636d]">Valor Total</span><strong class="text-lg text-[#073b57]">{{ valor || '—' }}</strong></div>
    <button type="button" class="mt-6 flex h-11 w-full items-center justify-center gap-2 rounded-lg bg-[#042d5c] text-xs font-semibold text-white hover:bg-[#0b417d] disabled:cursor-not-allowed disabled:opacity-60" :disabled="processando || !disponivel" @click="emit('finalizar')">
      {{ processando ? 'Abrindo pagamento...' : rotuloBotao }}<span v-if="disponivel && !processando" class="text-base">→</span>
    </button>
    <p class="mt-3 text-center text-[9px] text-[#59636d]">Ao finalizar, você concorda com nossos <RouterLink to="/termos" class="underline">Termos de Uso</RouterLink>. O pagamento é processado pelo Mercado Pago.</p>
  </section>
</template>
