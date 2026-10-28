<script setup>
/**
 * PainelAgendamento — painel azul "Horários Disponíveis" (calendário + horários + valor + botão)
 *
 *   <PainelAgendamento
 *     v-model:date="data"
 *     v-model:time="horario"
 *     :horarios="horarios"
 *     price="R$ 250,00"
 *     @agendar="agendar"
 *   />
 *
 * PROPS
 *   date (v-model:date)  String  dia escolhido, ISO 'YYYY-MM-DD'
 *   time (v-model:time)  String  horário escolhido, 'HH:MM'
 *   horarios             Array   horários livres do dia escolhido (quem usa o painel calcula)
 *   price                String  valor da consulta já formatado
 *
 * EVENTOS
 *   @agendar  clique em "Agendar Consulta" (o botão só habilita com dia e horário escolhidos)
 *
 * OBS: o botão "Agendar Consulta" aqui é um <button> simples com Tailwind.
 *      Se você já tem um componente de botão, troque-o no template.
 */
import { computed } from 'vue'
import SeletorCalendario from '@/components/paciente/SeletorCalendario.vue'
import SeletorHorario from '@/components/paciente/SeletorHorario.vue'
import CaixaValor from '@/components/paciente/CaixaValor.vue'
import { diaPorExtenso } from '@/utils/datas'

const date = defineModel('date', { type: String, default: '' })
const time = defineModel('time', { type: String, default: '' })

defineProps({
  horarios: { type: Array, default: () => [] },
  price: { type: String, required: true },
})

const emit = defineEmits(['agendar'])

const tituloHorarios = computed(() =>
  date.value ? `Horários para ${diaPorExtenso(date.value)}` : 'Selecione uma data',
)
const podeAgendar = computed(() => Boolean(date.value && time.value))
</script>

<template>
  <aside class="overflow-hidden rounded-xl bg-white shadow-[0_2px_12px_rgba(11,47,91,0.08)]">
    <header class="bg-[#042d5c] px-6 py-6 text-white">
      <h2 class="text-2xl font-semibold">Horários Disponíveis</h2>
      <p class="mt-1 text-sm font-semibold text-white/75">Selecione o melhor momento para você</p>
    </header>

    <div class="flex flex-col gap-6 p-6">
      <SeletorCalendario v-model="date" />

      <SeletorHorario v-model="time" :horarios="horarios" :title="tituloHorarios" />

      <CaixaValor :price="price" />

      <div class="flex flex-col gap-3">
        <button
          type="button"
          class="flex w-full cursor-pointer items-center justify-center gap-2 rounded-lg bg-[#042d5c] py-4 font-semibold text-white transition-colors hover:bg-[#0b3f7a] disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:bg-[#042d5c]"
          :disabled="!podeAgendar"
          @click="emit('agendar')"
        >
          <svg
            class="size-5"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="1.5"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 0 1 2.25-2.25h13.5A2.25 2.25 0 0 1 21 7.5v11.25m-18 0A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75m-18 0v-7.5A2.25 2.25 0 0 1 5.25 9h13.5A2.25 2.25 0 0 1 21 11.25v7.5"
            />
          </svg>
          Agendar Consulta
        </button>

        <p class="text-center text-xs text-gray-500">
          Ao agendar, você concorda com nossos termos de privacidade e política de cancelamento.
        </p>
      </div>
    </div>
  </aside>
</template>
