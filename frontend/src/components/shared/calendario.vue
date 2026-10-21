<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: { type: Date, required: true }, // v-model:data
  ano: { type: Number, required: true },
  mes: { type: Number, required: true }, // 1-12
  diasMarcados: { type: Array, default: () => [] },
  variante: { type: String, default: 'card' },
})
const emit = defineEmits(['update:data', 'mes-anterior', 'mes-seguinte', 'hoje'])

const MESES = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
const semana = ['DOM', 'SEG', 'TER', 'QUA', 'QUI', 'SEX', 'SÁB']

// "Novembro 2024"
const titulo = computed(() => `${MESES[props.mes - 1]} ${props.ano}`)

const celulas = computed(() => {
  const primeiro = new Date(props.ano, props.mes - 1, 1).getDay()
  const total = new Date(props.ano, props.mes, 0).getDate()
  const diasMesAnterior = new Date(props.ano, props.mes - 1, 0).getDate()
  const lista = []
  for (let i = primeiro - 1; i >= 0; i--) lista.push({ dia: diasMesAnterior - i, fora: true })
  for (let d = 1; d <= total; d++) lista.push({ dia: d, fora: false })
  while (lista.length % 7 !== 0) lista.push({ dia: lista.length - total - primeiro + 1, fora: true })
  return lista
})

const selecionado = (c) =>
  !c.fora &&
  props.data.getFullYear() === props.ano &&
  props.data.getMonth() + 1 === props.mes &&
  props.data.getDate() === c.dia

const marcado = (c) => !c.fora && props.diasMarcados.includes(c.dia)

const selecionar = (c) => {
  if (c.fora) return
  emit('update:data', new Date(props.ano, props.mes - 1, c.dia))
}
</script>

<template>
  <section class="rounded-xl border border-[#e5e9f2] bg-white p-5">
    <div class="mb-4 flex items-center justify-between text-[#0b2f5b]">
      <strong class="flex items-center gap-2 text-sm">
        <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="4" width="18" height="18" rx="2" /><path d="M16 2v4M8 2v4M3 10h18" />
        </svg>
        {{ titulo }}
      </strong>
      <div class="flex items-center gap-3 text-xs text-gray-500">
        <button type="button" class="cursor-pointer text-base leading-none hover:text-[#0b2f5b]" @click="emit('mes-anterior')">‹</button>
        <button type="button" class="cursor-pointer hover:text-[#0b2f5b]" @click="emit('hoje')">Hoje</button>
        <button type="button" class="cursor-pointer text-base leading-none hover:text-[#0b2f5b]" @click="emit('mes-seguinte')">›</button>
      </div>
    </div>

    <div class="grid grid-cols-7 gap-y-1.5 text-center">
      <span v-for="s in semana" :key="s" class="pb-1 text-[10px] font-medium text-gray-400">{{ s }}</span>

      <button
        v-for="(c, i) in celulas"
        :key="i"
        type="button"
        :disabled="c.fora"
        class="mx-auto h-8 w-8 rounded-lg border-2 border-transparent text-xs"
        :class="[
          c.fora ? 'cursor-default text-slate-300' : 'cursor-pointer',
          marcado(c) ? 'bg-[#0b2f5b] font-semibold text-white' : '',
          !c.fora && !marcado(c) ? 'text-slate-600 hover:bg-slate-100' : '',
          selecionado(c) ? 'border-[#0b2f5b]! font-semibold' : '',
          selecionado(c) && !marcado(c) ? 'bg-white text-[#0b2f5b]' : '',
        ]"
        @click="selecionar(c)"
      >
        {{ c.dia }}
      </button>
    </div>

    <ul class="mt-4 flex flex-col gap-2 border-t border-[#e5e9f2] pt-4 text-[11px] text-slate-600">
      <li class="flex items-center gap-2">
        <i class="inline-block h-2 w-2 rounded-full bg-[#0b2f5b]" />
        Com consultas marcadas
      </li>
      <li class="flex items-center gap-2">
        <i class="inline-block h-2 w-2 rounded-full border border-gray-400" />
        Livre / Sem agendamento
      </li>
    </ul>
  </section>
</template>