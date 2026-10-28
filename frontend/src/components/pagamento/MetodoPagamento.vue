<script setup>
defineProps({ modelValue: { type: String, required: true } })
const emit = defineEmits(['update:modelValue'])
const opcoes = [
  { id: 'pix', nome: 'Pix', descricao: 'Pagamento instantâneo com QR Code', simbolo: '▣' },
  { id: 'cartao', nome: 'Cartão de Crédito', descricao: 'Parcele em até 10x sem juros', simbolo: '▰' },
  { id: 'boleto', nome: 'Boleto Bancário', descricao: 'Compensação em até 3 dias úteis', simbolo: '▥' },
]
</script>

<template>
  <section class="rounded-xl bg-white p-5 shadow-[0_4px_18px_rgba(12,48,92,0.08)] sm:p-6">
    <h2 class="mb-3 text-base font-semibold text-[#073b57]">Método de Pagamento</h2>
    <div class="space-y-2.5">
      <button
        v-for="opcao in opcoes"
        :key="opcao.id"
        type="button"
        class="flex w-full items-center gap-3 rounded-lg border px-3 py-2.5 text-left"
        :class="modelValue === opcao.id ? 'border-[#00a9c5] bg-[#eef2ff]' : 'border-[#b9c3cf] bg-white hover:border-[#00a9c5]'"
        @click="emit('update:modelValue', opcao.id)"
      >
        <span class="flex size-8 shrink-0 items-center justify-center rounded-full bg-[#e6eef5] text-sm font-bold text-[#073b57]">{{ opcao.simbolo }}</span>
        <span><strong class="block text-[11px] font-medium text-[#233548]">{{ opcao.nome }}</strong><small class="block text-[9px] text-[#5b6470]">{{ opcao.descricao }}</small></span>
      </button>
    </div>
  </section>
</template>