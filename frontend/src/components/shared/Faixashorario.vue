<script setup>
import { ref, watch } from 'vue'

// faixas: [{ key, inicio: 'HH:MM', fim: 'HH:MM' }]
const faixas = defineModel('faixas', { type: Array, required: true })
// repeticao: null (só o dia selecionado) ou { diasSemana: [0..6], ate: 'YYYY-MM-DD' }
const repeticao = defineModel('repeticao', { type: Object, default: null })
const props = defineProps({
  // Dia selecionado no calendário: primeiro dia da repetição
  data: { type: Date, default: () => new Date() },
})
const emit = defineEmits(['salvar'])

const DIAS_SEMANA = [
  { valor: 1, rotulo: 'Seg' },
  { valor: 2, rotulo: 'Ter' },
  { valor: 3, rotulo: 'Qua' },
  { valor: 4, rotulo: 'Qui' },
  { valor: 5, rotulo: 'Sex' },
  { valor: 6, rotulo: 'Sáb' },
  { valor: 0, rotulo: 'Dom' },
]
const SEMANAS_PADRAO = 4

const toISODate = (d) =>
  `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`

const repetir = ref(false)
const diasSemana = ref([])
const ate = ref('')

// Ao trocar o dia no calendário, a repetição recomeça a partir dele
watch(
  () => props.data,
  (dia) => {
    diasSemana.value = [dia.getDay()]
    const limite = new Date(dia)
    limite.setDate(limite.getDate() + 7 * SEMANAS_PADRAO)
    ate.value = toISODate(limite)
  },
  { immediate: true },
)

// Mantém o v-model:repeticao em dia com o painel
watch(
  [repetir, diasSemana, ate],
  () => {
    repeticao.value = repetir.value ? { diasSemana: [...diasSemana.value], ate: ate.value } : null
  },
  { immediate: true },
)

function alternarDia(dia) {
  diasSemana.value = diasSemana.value.includes(dia)
    ? diasSemana.value.filter((d) => d !== dia)
    : [...diasSemana.value, dia]
}

function adicionar() {
  faixas.value = [...faixas.value, { key: `novo-${Date.now()}`, inicio: '', fim: '' }]
}

function remover(i) {
  faixas.value = faixas.value.filter((_, idx) => idx !== i)
  emit('salvar')
}

function atualizar(i, campo, valor) {
  faixas.value = faixas.value.map((f, idx) => (idx === i ? { ...f, [campo]: valor } : f))
  const faixa = faixas.value[i]
  if (faixa.inicio && faixa.fim) emit('salvar')
}
</script>

<template>
  <div>
    <h3 class="mb-3 text-xs font-bold text-[#0b2f5b]">Horário de Atendimento</h3>

    <!-- Repetição semanal: as faixas novas entram em todos os dias escolhidos, até a data final -->
    <div class="mb-2.5 rounded-lg border border-[#dfe5f1] bg-white px-4 py-3">
      <label class="flex cursor-pointer items-center gap-2 text-xs font-semibold text-[#0b2f5b]">
        <input v-model="repetir" type="checkbox" class="h-4 w-4 accent-[#0b2f5b]" />
        Repetir toda semana
      </label>

      <div v-if="repetir" class="mt-3 flex flex-col gap-3">
        <div class="flex flex-wrap gap-1.5" role="group" aria-label="Dias da semana">
          <button
            v-for="dia in DIAS_SEMANA"
            :key="dia.valor"
            type="button"
            :aria-pressed="diasSemana.includes(dia.valor)"
            class="w-11 cursor-pointer rounded-md border py-1.5 text-[11px] font-semibold transition"
            :class="
              diasSemana.includes(dia.valor)
                ? 'border-[#0b2f5b] bg-[#0b2f5b] text-white'
                : 'border-[#dfe5f1] bg-white text-[#0b2f5b] hover:bg-[#eef2ff]'
            "
            @click="alternarDia(dia.valor)"
          >
            {{ dia.rotulo }}
          </button>
        </div>

        <label class="flex flex-wrap items-center gap-2 text-[11px] text-gray-500">
          De {{ data.toLocaleDateString('pt-BR') }} até
          <input
            v-model="ate"
            type="date"
            :min="toISODate(data)"
            aria-label="Repetir até"
            class="rounded-md border border-[#dfe5f1] bg-white px-2.5 py-1.5 text-xs font-medium text-[#0b2f5b] outline-none focus:ring-2 focus:ring-[#0b2f5b]/30"
          />
        </label>
        <p class="text-[11px] text-gray-500">
          Os próximos horários adicionados entram em todos esses dias. Editar ou remover vale só para o dia aberto.
        </p>
      </div>
    </div>

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