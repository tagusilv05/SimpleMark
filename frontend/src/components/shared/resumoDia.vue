<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: { type: Date, required: true },
  dataTexto: { type: String, required: true },
  resumo: { type: Object, required: true },
})

const ehHoje = computed(() => props.data.toDateString() === new Date().toDateString())

const seloTotal = computed(() =>
  ehHoje.value
    ? 'Hoje'
    : `${String(props.data.getDate()).padStart(2, '0')}/${String(props.data.getMonth() + 1).padStart(2, '0')}`,
)

const temFaturamento = computed(() => Number(props.resumo.faturamento_previsto) > 0)

const valor = computed(() => {
  const [inteiro, cent] = Number(props.resumo.faturamento_previsto).toFixed(2).split('.')
  return { inteiro: Number(inteiro).toLocaleString('pt-BR'), cent }
})
</script>

<template>
  <section class="rounded-xl border border-[#e5e9f2] bg-white p-5">
    <div class="mb-4 flex items-center justify-between">
      <div class="flex items-center gap-2 text-[11px] font-bold tracking-wide text-[#0b2f5b]">
        <svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="4" width="18" height="18" rx="2" /><path d="M16 2v4M8 2v4M3 10h18" />
        </svg>
        RESUMO DO DIA
      </div>
      <span class="text-[11px] text-gray-500">{{ dataTexto }}</span>
    </div>

    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
      <div class="rounded-lg border border-[#e5e9f2] p-4">
        <div class="flex items-center justify-between">
          <span class="flex items-center gap-1.5 text-[10px] font-semibold tracking-wide text-gray-500">
            <svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="3" y="4" width="18" height="18" rx="2" /><path d="M16 2v4M8 2v4M3 10h18" />
            </svg>
            TOTAL AGENDADOS
          </span>
          <span class="rounded-full border border-[#d9def0] bg-indigo-50 px-2 py-0.5 text-[10px] font-medium text-[#0b2f5b]">
            {{ seloTotal }}
          </span>
        </div>
        <p class="mt-3 text-sm text-gray-600">
          <strong class="mr-1 text-3xl font-bold text-[#0b2f5b]">{{ resumo.total_agendados }}</strong>
          {{ resumo.total_agendados === 1 ? 'consulta marcada' : 'consultas marcadas' }}
        </p>
      </div>

      <div class="rounded-lg border border-[#e5e9f2] p-4">
        <div class="flex items-center justify-between">
          <span class="flex items-center gap-1.5 text-[10px] font-semibold tracking-wide text-gray-500">
            <svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10" /><path d="M16 8h-6a2 2 0 1 0 0 4h4a2 2 0 1 1 0 4H8" /><path d="M12 18V6" />
            </svg>
            FATURAMENTO DO DIA
          </span>
          <span
            class="rounded-full px-2 py-0.5 text-[10px] font-medium"
            :class="temFaturamento ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-500'"
          >
            {{ temFaturamento ? 'Prevista' : 'Sem atendimentos' }}
          </span>
        </div>
        <p class="mt-3 text-3xl font-bold text-[#0b2f5b]">
          R$ {{ valor.inteiro }}<span class="text-xs font-medium text-gray-500">,{{ valor.cent }}</span>
        </p>
      </div>
    </div>
  </section>
</template>