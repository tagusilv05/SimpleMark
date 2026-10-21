<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({ atendimento: { type: Object, default: null } })
const emit = defineEmits(['entrar'])

const agora = ref(Date.now())
let timer
onMounted(() => { timer = setInterval(() => (agora.value = Date.now()), 1000) })
onBeforeUnmount(() => clearInterval(timer))

const hora = (iso) => iso.slice(11, 16)

const contagem = computed(() => {
  if (!props.atendimento) return ''
  const diff = Math.floor((new Date(props.atendimento.inicio).getTime() - agora.value) / 1000)
  if (diff <= 0) return 'Em andamento'
  return `Inicia em ${Math.floor(diff / 60)} min ${String(diff % 60).padStart(2, '0')} s`
})
</script>

<template>
  <section
    class="flex flex-col items-start justify-between gap-4 rounded-xl border border-[#e5e9f2] bg-white p-5 sm:flex-row sm:items-center"
  >
    <div class="flex items-center gap-4">
      <div
        class="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl text-[#0b2f5b]"
        :class="atendimento ? 'bg-indigo-50' : 'bg-slate-100'"
      >
        <svg
          v-if="atendimento"
          class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
        >
          <rect x="3" y="4" width="18" height="18" rx="2" /><path d="M16 2v4M8 2v4M3 10h18" />
        </svg>
        <svg
          v-else
          class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
        >
          <circle cx="12" cy="12" r="10" /><path d="M12 6v6l4 2" />
        </svg>
      </div>

      <div>
        <div class="flex items-center gap-2 text-[10px] font-semibold tracking-wide text-gray-500">
          <span>PRÓXIMO ATENDIMENTO</span>

          <span
            v-if="atendimento"
            class="rounded-full bg-teal-600 px-2.5 py-0.5 text-[10px] font-medium text-white"
          >
            {{ contagem }}
          </span>
          <span
            v-else
            class="flex items-center gap-1 rounded-full border border-emerald-200 bg-emerald-50 px-2 py-0.5 text-[10px] font-medium text-emerald-600"
          >
            <i class="h-1.5 w-1.5 rounded-full bg-emerald-500" />
            Agenda livre
          </span>
        </div>

        <template v-if="atendimento">
          <h2 class="mt-1 text-lg font-bold text-[#0b2f5b]">
            {{ atendimento.paciente_nome }}
            <span class="text-sm font-normal text-gray-600">
              • {{ hora(atendimento.inicio) }} - {{ hora(atendimento.fim) }}
              <template v-if="atendimento.especialidade">({{ atendimento.especialidade }})</template>
            </span>
          </h2>
        </template>
        <template v-else>
          <h2 class="mt-1 text-lg font-bold text-[#0b2f5b]">Nenhum atendimento agendado no momento</h2>
          <p class="mt-0.5 text-[11px] text-gray-500">
            Você não tem teleconsultas agendadas para hoje. Aproveite para gerenciar seus horários ou
            disponibilizar novas vagas na agenda
          </p>
        </template>
      </div>
    </div>

    <button
      type="button"
      :disabled="!atendimento"
      class="flex shrink-0 items-center gap-2 rounded-lg bg-[#0b2f5b] px-6 py-3 text-sm font-semibold text-white transition enabled:cursor-pointer enabled:hover:bg-[#12407a] disabled:cursor-not-allowed disabled:bg-[#dfe5f1] disabled:text-[#9aa7bd]"
      @click="atendimento && emit('entrar', atendimento.id)"
    >
      <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="m22 8-6 4 6 4V8Z" /><rect x="2" y="6" width="14" height="12" rx="2" />
      </svg>
      Entrar na Chamada Virtual
    </button>
  </section>
</template>