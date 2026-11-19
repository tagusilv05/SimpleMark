<script setup>
import { ref } from 'vue'

defineProps({
  salvando: { type: Boolean, default: false },
})
const emit = defineEmits(['adicionar'])

const inicio = ref('')
const fim = ref('')

function confirmar() {
  emit('adicionar', {
    inicio: inicio.value,
    fim: fim.value,
    limpar: () => {
      inicio.value = ''
      fim.value = ''
    },
  })
}
</script>

<template>
  <div>
    <h3 class="mb-3 text-xs font-bold text-[#0b2f5b]">Horário de Atendimento</h3>

    <!-- Aba de adicionar horário sempre aberta e disponível -->
    <div class="flex flex-wrap items-center gap-3 rounded-lg bg-[#eef2ff] px-4 py-3">
      <span class="flex h-7 w-7 items-center justify-center rounded-full bg-[#dfe6fa] text-[#0b2f5b]">
        <svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10" /><path d="M12 6v6l4 2" />
        </svg>
      </span>
      <span class="mr-auto text-xs font-semibold text-[#0b2f5b]">Define o Horário</span>

      <input
        type="time"
        v-model="inicio"
        aria-label="Início"
        class="w-28 rounded-md border border-[#dfe5f1] bg-white px-2.5 py-1.5 text-xs font-medium text-[#0b2f5b] outline-none focus:ring-2 focus:ring-[#0b2f5b]/30"
      />
      <span class="text-[11px] text-gray-500">até</span>
      <input
        type="time"
        v-model="fim"
        aria-label="Fim"
        class="w-28 rounded-md border border-[#dfe5f1] bg-white px-2.5 py-1.5 text-xs font-medium text-[#0b2f5b] outline-none focus:ring-2 focus:ring-[#0b2f5b]/30"
      />
    </div>

    <!-- Apenas um botão de confirmar/adicionar horário para o banco -->
    <button
      type="button"
      :disabled="salvando"
      class="mt-2.5 flex w-full cursor-pointer items-center justify-center gap-2 rounded-lg bg-[#0b2f5b] py-3 text-xs font-semibold text-white transition hover:bg-[#07254a] disabled:cursor-not-allowed disabled:opacity-50"
      @click="confirmar"
    >
      <svg v-if="salvando" class="h-4 w-4 animate-spin text-white" viewBox="0 0 24 24" fill="none">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
      </svg>
      <span v-else class="text-base leading-none">+</span>
      <span>{{ salvando ? 'Adicionando...' : 'Adicionar Horário' }}</span>
    </button>
  </div>
</template>
