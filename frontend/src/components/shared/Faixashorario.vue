<script setup>
// faixas: [{ key, inicio: 'HH:MM', fim: 'HH:MM' }]
const faixas = defineModel('faixas', { type: Array, required: true })
const emit = defineEmits(['salvar'])

function adicionar() {
  faixas.value = [...faixas.value, { key: `novo-${Date.now()}`, inicio: '', fim: '' }]
}

function remover(i) {
  faixas.value = faixas.value.filter((_, idx) => idx !== i)
  emit('salvar')
}

function atualizar(i, campo, valor) {
  faixas.value = faixas.value.map((f, idx) => (idx === i ? { ...f, [campo]: valor } : f))
  emit('salvar')
}
</script>

<template>
  <div>
    <h3 class="mb-3 text-xs font-bold text-[#0b2f5b]">Horário de Atendimento</h3>

    <ul class="flex flex-col gap-2.5">
      <li
        v-for="(f, i) in faixas"
        :key="f.key"
        class="flex flex-wrap items-center gap-3 rounded-lg bg-[#eef2ff] px-4 py-3"
      >
        <span class="flex h-7 w-7 items-center justify-center rounded-full bg-[#dfe6fa] text-[#0b2f5b]">
          <svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10" /><path d="M12 6v6l4 2" />
          </svg>
        </span>
        <span class="mr-auto text-xs font-semibold text-[#0b2f5b]">Define o Horário</span>

        <input
          type="time"
          :value="f.inicio"
          aria-label="Início"
          class="w-28 rounded-md border border-[#dfe5f1] bg-white px-2.5 py-1.5 text-xs font-medium text-[#0b2f5b] outline-none focus:ring-2 focus:ring-[#0b2f5b]/30"
          @change="atualizar(i, 'inicio', $event.target.value)"
        />
        <span class="text-[11px] text-gray-500">até</span>
        <input
          type="time"
          :value="f.fim"
          aria-label="Fim"
          class="w-28 rounded-md border border-[#dfe5f1] bg-white px-2.5 py-1.5 text-xs font-medium text-[#0b2f5b] outline-none focus:ring-2 focus:ring-[#0b2f5b]/30"
          @change="atualizar(i, 'fim', $event.target.value)"
        />

        <button
          type="button"
          class="cursor-pointer p-1 text-red-500 hover:text-red-700"
          aria-label="Remover faixa de horário"
          @click="remover(i)"
        >
          <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M3 6h18M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6M10 11v6M14 11v6" />
          </svg>
        </button>
      </li>
    </ul>

    <button
      type="button"
      class="mt-2.5 flex w-full cursor-pointer items-center justify-center gap-2 rounded-lg bg-[#eef2ff] py-3 text-xs font-semibold text-[#0b2f5b] transition hover:bg-[#e3e9fb]"
      @click="adicionar"
    >
      <span class="text-base leading-none">+</span> Adicionar Horário
    </button>
  </div>
</template>