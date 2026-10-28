<script setup>
/**
 * SeletorCalendario — calendário mensal para escolher o dia da consulta
 *
 *   <SeletorCalendario v-model="data" />
 *
 * PROPS
 *   modelValue   String   data selecionada em ISO 'YYYY-MM-DD' (v-model)
 *   disablePast  Boolean  bloqueia dias anteriores a hoje (padrão true)
 *
 * Os dias do mês anterior que completam a primeira semana aparecem esmaecidos e não clicáveis.
 */
import { computed, ref } from 'vue'
import { MESES, toISO, fromISO } from '@/utils/datas'

const props = defineProps({
  modelValue: { type: String, default: '' },
  disablePast: { type: Boolean, default: true },
})

const emit = defineEmits(['update:modelValue'])

const hoje = new Date()
const hojeISO = toISO(hoje)

// Mês exibido: começa no mês da data selecionada (ou no mês atual)
const inicial = props.modelValue ? fromISO(props.modelValue) : hoje
const ano = ref(inicial.getFullYear())
const mes = ref(inicial.getMonth())

const titulo = computed(() => `${MESES[mes.value]} ${ano.value}`)
const diasSemana = ['DOM', 'SEG', 'TER', 'QUA', 'QUI', 'SEX', 'SÁB']

const dias = computed(() => {
  const antes = new Date(ano.value, mes.value, 1).getDay() // dias do mês anterior na 1ª semana
  const total = new Date(ano.value, mes.value + 1, 0).getDate()
  const lista = []

  for (let i = 0; i < antes; i++) {
    const d = new Date(ano.value, mes.value, 1 - antes + i)
    lista.push({ iso: toISO(d), dia: d.getDate(), doMes: false, desabilitado: true })
  }

  for (let dia = 1; dia <= total; dia++) {
    const iso = toISO(new Date(ano.value, mes.value, dia))
    lista.push({ iso, dia, doMes: true, desabilitado: props.disablePast && iso < hojeISO })
  }

  return lista
})

const podeVoltar = computed(
  () => !props.disablePast || ano.value * 12 + mes.value > hoje.getFullYear() * 12 + hoje.getMonth(),
)

function mudarMes(delta) {
  const d = new Date(ano.value, mes.value + delta, 1)
  ano.value = d.getFullYear()
  mes.value = d.getMonth()
}

function classeDoDia(d) {
  if (!d.doMes) return 'cursor-default text-gray-300'
  if (d.desabilitado) return 'cursor-not-allowed text-gray-300'
  if (d.iso === props.modelValue) return 'cursor-pointer bg-[#0b2f5b] text-white'
  return 'cursor-pointer text-[#0b2f5b] hover:bg-[#eef2fb]'
}
</script>

<template>
  <div>
    <div class="mb-4 flex items-center justify-between">
      <h3 class="text-sm font-bold text-[#0b2f5b]">{{ titulo }}</h3>

      <div class="flex items-center gap-3 text-[#0b2f5b]">
        <button
          type="button"
          class="cursor-pointer disabled:cursor-not-allowed disabled:opacity-30"
          aria-label="Mês anterior"
          :disabled="!podeVoltar"
          @click="mudarMes(-1)"
        >
          <svg
            class="size-4"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="3"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path stroke-linecap="round" stroke-linejoin="round" d="m15.75 19.5-7.5-7.5 7.5-7.5" />
          </svg>
        </button>

        <button
          type="button"
          class="cursor-pointer"
          aria-label="Próximo mês"
          @click="mudarMes(1)"
        >
          <svg
            class="size-4"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="3"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path stroke-linecap="round" stroke-linejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
          </svg>
        </button>
      </div>
    </div>

    <div class="grid grid-cols-7 gap-y-1 text-center">
      <span
        v-for="d in diasSemana"
        :key="d"
        class="py-2 text-[11px] font-semibold text-gray-500"
      >
        {{ d }}
      </span>

      <button
        v-for="d in dias"
        :key="d.iso"
        type="button"
        class="mx-auto flex size-10 items-center justify-center rounded-lg text-sm font-semibold transition-colors"
        :class="classeDoDia(d)"
        :disabled="d.desabilitado"
        :aria-pressed="d.doMes && d.iso === modelValue"
        :aria-label="d.iso"
        @click="emit('update:modelValue', d.iso)"
      >
        {{ d.dia }}
      </button>
    </div>
  </div>
</template>
