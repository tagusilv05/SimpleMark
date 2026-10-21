<script setup>
const props = defineProps({
  especialidades: { type: Array, default: () => [] }, // [{ id, nome, valor_consulta }]
  especialidadeId: { type: [String, Number], default: null },
  valor: { type: Number, default: 0 },
})
const emit = defineEmits(['update:especialidadeId', 'update:valor', 'salvar-valor', 'gerenciar'])

const brl = new Intl.NumberFormat('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

// máscara de moeda: os dígitos digitados entram como centavos
function aoDigitar(e) {
  const digitos = e.target.value.replace(/\D/g, '')
  const novo = Number(digitos || 0) / 100
  emit('update:valor', novo)
  e.target.value = brl.format(novo)
}
</script>

<template>
  <section class="rounded-xl bg-white p-6 shadow-[0_2px_12px_rgba(11,47,91,0.08)]">
    <div class="mb-5 flex items-center gap-3 border-b border-[#eef0f6] pb-4">
      <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-[#eef2ff] text-[#0b2f5b]">
        <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M16 20V4a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16" /><rect x="2" y="6" width="20" height="14" rx="2" />
          <path d="M12 10v6M9 13h6" />
        </svg>
      </div>
      <h2 class="text-base text-[#0b2f5b]">Especialidade e Valor da Consulta</h2>
    </div>

    <div class="flex flex-wrap items-end gap-4">
      <div class="w-full sm:w-72">
        <label for="especialidade" class="mb-1.5 block text-xs font-semibold text-[#0b2f5b]">
          Especialidade em Configuração
        </label>
        <div class="relative">
          <span class="pointer-events-none absolute top-1/2 left-3.5 h-2 w-2 -translate-y-1/2 rounded-full bg-[#0b2f5b]" />
          <select
            id="especialidade"
            :value="especialidadeId"
            class="w-full cursor-pointer appearance-none rounded-lg bg-[#eef2ff] py-3 pr-10 pl-8 text-xs font-semibold text-[#0b2f5b] outline-none focus:ring-2 focus:ring-[#0b2f5b]/30"
            @change="emit('update:especialidadeId', $event.target.value)"
          >
            <option v-for="e in especialidades" :key="e.id" :value="e.id">{{ e.nome }}</option>
          </select>
          <svg class="pointer-events-none absolute top-1/2 right-3.5 h-3.5 w-3.5 -translate-y-1/2 text-gray-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="m6 9 6 6 6-6" />
          </svg>
        </div>
      </div>

      <div>
        <label for="valor" class="mb-1.5 block text-xs font-semibold text-[#0b2f5b]">Valor da Consulta</label>
        <div class="flex w-40 items-center gap-2 rounded-lg border border-[#e5e9f2] bg-[#f6f8fe] px-3 py-3 focus-within:ring-2 focus-within:ring-[#0b2f5b]/30">
          <span class="text-[11px] text-gray-500">R$</span>
          <input
            id="valor"
            type="text"
            inputmode="numeric"
            :value="brl.format(valor)"
            class="w-full bg-transparent text-xs font-bold text-[#0b2f5b] outline-none"
            @input="aoDigitar"
            @change="emit('salvar-valor')"
          />
        </div>
      </div>

      <button
        type="button"
        class="ml-auto flex cursor-pointer items-center gap-2 rounded-lg bg-[#e3e9fb] px-4 py-3 text-xs font-semibold text-[#0b2f5b] transition hover:bg-[#d5def7]"
        @click="emit('gerenciar')"
      >
        <svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z" />
        </svg>
        Gerenciar
      </button>
    </div>
  </section>
</template>