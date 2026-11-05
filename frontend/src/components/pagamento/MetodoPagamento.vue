<script setup>
/**
 * MetodoPagamento — escolha da forma de pagamento (v-model: 'pix' | 'cartao' | 'boleto').
 *
 * A forma escolhida vai para POST /api/v1/pagamento/preferencia e o checkout do
 * Mercado Pago passa a aceitar só ela.
 */
import { METODOS_PAGAMENTO } from '@/utils/pagamento'

defineProps({
  modelValue: { type: String, required: true },
  desabilitado: { type: Boolean, default: false },
})
const emit = defineEmits(['update:modelValue'])
</script>

<template>
  <section class="rounded-xl bg-white p-5 shadow-[0_4px_18px_rgba(12,48,92,0.08)] sm:p-6">
    <h2 class="mb-3 text-base font-semibold text-[#073b57]">Método de Pagamento</h2>
    <div class="space-y-2.5" role="radiogroup" aria-label="Método de pagamento">
      <button
        v-for="opcao in METODOS_PAGAMENTO"
        :key="opcao.id"
        type="button"
        role="radio"
        :aria-checked="modelValue === opcao.id"
        :disabled="desabilitado"
        class="flex w-full items-center gap-3 rounded-lg border px-3 py-2.5 text-left disabled:cursor-not-allowed disabled:opacity-60"
        :class="modelValue === opcao.id ? 'border-[#00a9c5] bg-[#eef2ff]' : 'border-[#b9c3cf] bg-white hover:border-[#00a9c5]'"
        @click="emit('update:modelValue', opcao.id)"
      >
        <span class="flex size-8 shrink-0 items-center justify-center rounded-full bg-[#e6eef5] text-sm font-bold text-[#073b57]">{{ opcao.simbolo }}</span>
        <span><strong class="block text-[11px] font-medium text-[#233548]">{{ opcao.nome }}</strong><small class="block text-[9px] text-[#5b6470]">{{ opcao.descricao }}</small></span>
      </button>
    </div>
  </section>
</template>
