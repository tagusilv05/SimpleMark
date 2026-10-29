<script setup>
/**
 * AgendamentoView — marcação de consulta em 3 passos (médico, data e horário)
 *
 * Os médicos e os horários livres vêm de GET /api/v1/profissionais/busca.
 * Query string opcional:
 *   ?especialidade=<id>   filtra a lista pela especialidade
 *   ?profissional=<id>    já deixa esse profissional selecionado
 *
 * Ao confirmar, cria a consulta em POST /consultas/agendar (paciente logado)
 * e vai para a tela de confirmação.
 */
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppHeader from '@/components/shared/AppHeader.vue'
import BackLink from '@/components/shared/BackLink.vue'
import SeletorCalendario from '@/components/paciente/SeletorCalendario.vue'
import { api } from '@/services/api'
import { buscarProfissionais } from '@/services/profissionais'
import { useAgendamentoStore } from '@/stores/agendamento'
import { MESES_ABREV, fromISO, toISO } from '@/utils/datas'

const route = useRoute()
const router = useRouter()
const agendamento = useAgendamentoStore()

const user = ref(null)
const medicos = ref([])
const carregando = ref(true)
const enviando = ref(false)
const erro = ref('')
const precisaLogin = ref(false)
const medico = ref(null)
const data = ref(toISO(new Date()))
const horario = ref(null)

const formatarValor = (v) =>
  new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(Number(v))

const iniciais = (nome) =>
  nome
    .replace(/^dra?\.?\s+/i, '')
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((p) => p[0].toUpperCase())
    .join('')

async function carregarUsuario() {
  try {
    const conta = await api.get('/api/v1/auth/eu')
    user.value = { name: conta.nome, role: 'Paciente' }
  } catch {
    user.value = null
  }
}

async function carregarMedicos() {
  carregando.value = true
  erro.value = ''
  try {
    medicos.value = await buscarProfissionais({ id_especialidade: route.query.especialidade })
  } catch (e) {
    medicos.value = []
    erro.value = e.message
  } finally {
    carregando.value = false
  }
  const preferido = medicos.value.find((m) => String(m.id_profissional) === String(route.query.profissional))
  selecionarMedico(preferido ?? medicos.value[0] ?? null)
}

// Ao trocar de médico, o calendário pula para o primeiro dia com horário livre
function selecionarMedico(m) {
  medico.value = m
  const primeiro = m?.horarios_disponiveis[0]?.data_consulta
  if (primeiro) data.value = primeiro
}

// Horários livres do médico escolhido no dia escolhido
const horarios = computed(() =>
  (medico.value?.horarios_disponiveis ?? [])
    .filter((h) => h.data_consulta === data.value)
    .map((h) => ({ id_horario: h.id_horario, inicio: h.hora_inicio.slice(0, 5), fim: h.hora_fim.slice(0, 5) })),
)

// Trocar de médico ou de dia limpa o horário escolhido
watch([medico, data], () => {
  horario.value = null
})

const dataResumo = computed(() => {
  const d = fromISO(data.value)
  return `${String(d.getDate()).padStart(2, '0')} ${MESES_ABREV[d.getMonth()]}, ${d.getFullYear()}`
})

const podeConfirmar = computed(() => Boolean(medico.value && horario.value) && !enviando.value)

async function confirmar() {
  if (!podeConfirmar.value) return
  enviando.value = true
  erro.value = ''
  precisaLogin.value = false
  try {
    const consulta = await agendamento.agendar(horario.value)
    router.push({ name: 'confirmacaoAgendamento', params: { idConsulta: consulta.id_consulta } })
  } catch (e) {
    erro.value = e.message
    if (e.status === 401 || e.status === 403) {
      precisaLogin.value = true
      erro.value = 'Entre com uma conta de paciente para agendar a consulta.'
    } else if (e.status === 409) {
      // O horário foi reservado por outra pessoa: atualiza a agenda
      const atual = medico.value?.id_esp_prof
      await carregarMedicos()
      selecionarMedico(medicos.value.find((m) => m.id_esp_prof === atual) ?? medicos.value[0] ?? null)
    }
  } finally {
    enviando.value = false
  }
}

onMounted(() => {
  carregarUsuario()
  carregarMedicos()
})
</script>

<template>
  <div class="flex min-h-screen flex-col bg-[#f8faff]">
    <AppHeader :user="user" />
    <BackLink />

    <main class="mx-auto w-full max-w-[1120px] flex-1 px-6 pb-12 pt-8">
      <h1 class="text-4xl font-bold text-[#0b2f5b]">AGENDAMENTO</h1>
      <p class="mt-2 text-gray-600">Siga os passos abaixo para realizar sua marcação de forma rápida e segura.</p>

      <div class="mt-8 grid items-start gap-6 lg:grid-cols-3">
        <!-- 1. Médico -->
        <section class="rounded-xl bg-white p-6 shadow-sm">
          <h2 class="mb-5 flex items-center gap-3 text-2xl text-[#0b2f5b]">
            <span class="flex size-8 items-center justify-center rounded-full bg-[#0b2f5b] text-sm font-semibold text-white">1</span>
            Escolha o Médico
          </h2>

          <p v-if="carregando" class="text-sm text-gray-500">Carregando profissionais...</p>
          <p v-else-if="!medicos.length" class="text-sm text-gray-500">Nenhum profissional com horário livre no momento.</p>

          <div v-else class="flex flex-col gap-4" role="radiogroup" aria-label="Médicos">
            <div
              v-for="m in medicos"
              :key="m.id_esp_prof"
              role="radio"
              tabindex="0"
              :aria-checked="medico === m"
              class="flex cursor-pointer items-center gap-4 rounded-xl border p-4 transition-colors"
              :class="medico === m ? 'border-[#04263f] bg-[#04263f] text-white' : 'border-gray-300 bg-white text-[#0b2f5b] hover:border-[#0b2f5b]'"
              @click="selecionarMedico(m)"
              @keydown.enter.space.prevent="selecionarMedico(m)"
            >
              <img v-if="m.path_imagem" :src="m.path_imagem" :alt="`Foto de ${m.nome}`" class="size-16 shrink-0 rounded-full object-cover" />
              <div
                v-else
                class="flex size-16 shrink-0 items-center justify-center rounded-full text-lg font-bold"
                :class="medico === m ? 'bg-white text-[#04263f]' : 'bg-[#0b2f5b] text-white'"
              >
                {{ iniciais(m.nome) }}
              </div>

              <div class="min-w-0 flex-1">
                <p class="truncate text-lg font-semibold">{{ m.nome }}</p>
                <p class="text-sm" :class="medico === m ? 'text-gray-200' : 'text-gray-600'">{{ m.especialidade }}</p>
                <div class="mt-1 flex items-center justify-between gap-2 border-b pb-1" :class="medico === m ? 'border-transparent' : 'border-gray-200'">
                  <span class="font-mono text-xs">CRM: {{ m.conselho || '—' }}</span>
                  <span class="font-semibold">{{ formatarValor(m.valor_consulta) }}</span>
                </div>
                <RouterLink
                  :to="{ name: 'perfil-profissional', params: m.id_profissional ? { id: m.id_profissional } : {} }"
                  class="mt-2 inline-block text-xs hover:underline"
                  :class="medico === m ? 'text-[#5ee0f0]' : 'text-[#0b2f5b]'"
                  @click.stop
                >
                  Ver mais informações →
                </RouterLink>
              </div>
            </div>
          </div>
        </section>

        <div class="flex flex-col gap-6">
          <!-- 2. Data -->
          <section class="rounded-xl bg-white p-6 shadow-sm">
            <h2 class="mb-5 flex items-center gap-3 text-2xl text-[#0b2f5b]">
              <span class="flex size-8 items-center justify-center rounded-full bg-[#0b2f5b] text-sm font-semibold text-white">2</span>
              Data
            </h2>
            <SeletorCalendario v-model="data" />
          </section>

          <!-- 3. Horário -->
          <section class="rounded-xl bg-white p-6 shadow-sm">
            <h2 class="mb-5 flex items-center gap-3 text-2xl text-[#0b2f5b]">
              <span class="flex size-8 items-center justify-center rounded-full bg-[#0b2f5b] text-sm font-semibold text-white">3</span>
              Horário
            </h2>

            <div v-if="horarios.length" class="grid grid-cols-2 gap-3" role="radiogroup" aria-label="Horários">
              <button
                v-for="h in horarios"
                :key="h.id_horario"
                type="button"
                role="radio"
                :aria-checked="horario?.id_horario === h.id_horario"
                class="cursor-pointer rounded-lg border py-3 text-base font-bold transition-colors"
                :class="horario?.id_horario === h.id_horario ? 'border-[#0b2f5b] bg-[#0b2f5b] text-white' : 'border-gray-300 text-[#0b2f5b] hover:border-[#0b2f5b]'"
                @click="horario = h"
              >
                {{ h.inicio }} - {{ h.fim }}
              </button>
            </div>
            <p v-else class="text-sm text-gray-500">Não há horários disponíveis neste dia.</p>
          </section>
        </div>

        <!-- Resumo -->
        <aside class="rounded-xl bg-white p-6 shadow-sm">
          <h2 class="mb-6 text-2xl text-[#0b2f5b]">Resumo do Agendamento</h2>

          <dl class="text-[#0b2f5b]">
            <div class="flex justify-between gap-4 border-b border-gray-300 py-3">
              <dt class="text-gray-700">Médico</dt>
              <dd class="text-right font-bold">{{ medico?.nome ?? '—' }}</dd>
            </div>
            <div class="flex justify-between gap-4 border-b border-gray-300 py-3">
              <dt class="text-gray-700">Data</dt>
              <dd class="font-bold">{{ dataResumo }}</dd>
            </div>
            <div class="flex justify-between gap-4 border-b border-gray-300 py-3">
              <dt class="text-gray-700">Horário</dt>
              <dd class="font-bold">{{ horario ? `${horario.inicio} / ${horario.fim}` : '—' }}</dd>
            </div>
            <div class="flex items-center justify-between gap-4 py-4">
              <dt class="text-gray-700">Total</dt>
              <dd class="text-2xl font-bold">{{ medico ? formatarValor(medico.valor_consulta) : '—' }}</dd>
            </div>
          </dl>

          <button
            type="button"
            class="mt-4 flex h-14 w-full cursor-pointer items-center justify-center gap-3 rounded-lg bg-[#0b2f5b] text-lg text-white transition-colors hover:bg-[#0b417d] disabled:cursor-not-allowed disabled:opacity-50"
            :disabled="!podeConfirmar"
            @click="confirmar"
          >
            {{ enviando ? 'Agendando...' : 'Confirmar Agendamento' }}
            <svg class="size-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 0 1 2.25-2.25h13.5A2.25 2.25 0 0 1 21 7.5v11.25m-18 0A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75m-18 0v-7.5A2.25 2.25 0 0 1 5.25 9h13.5A2.25 2.25 0 0 1 21 11.25v7.5m-12-3 2 2 4-4" />
            </svg>
          </button>

          <p v-if="erro" class="mt-4 rounded-lg bg-[#eef2ff] p-3 text-sm text-[#0b2f5b]" role="alert">
            {{ erro }}
            <RouterLink v-if="precisaLogin" :to="{ name: 'login/paciente' }" class="font-semibold underline">Entrar</RouterLink>
          </p>

          <p class="mt-4 flex gap-2 rounded-lg bg-[#fff4f4] p-3 text-xs text-[#b00020]">
            <span aria-hidden="true">ⓘ</span>
            O cancelamento deve ser feito com até 24h de antecedência para reembolso total do valor.
          </p>
        </aside>
      </div>
    </main>
  </div>
</template>
