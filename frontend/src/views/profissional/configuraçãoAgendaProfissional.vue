<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api' // ajuste para a sua instância axios
import AppHeader from '@/components/shared/AppHeader.vue'
import BackLink from '@/components/shared/BackLink.vue'
import CardEspecialidadeValor from '@/components/shared/CardespecialidadeValor.vue'
import FaixasHorario from '@/components/shared/Faixashorario.vue'
import HorariosAgendados from '@/components/shared/HorariosAgendados.vue'
import CalendarioMensal from '@/components/shared/calendario.vue'

const router = useRouter()

const hoje = new Date()
const dataSelecionada = ref(hoje)
const mesVisivel = ref({ ano: hoje.getFullYear(), mes: hoje.getMonth() + 1 })

const especialidades = ref([])
const especialidadeId = ref(null)
const valor = ref(0)

const faixas = ref([])
const horarios = ref([])
const diasComConsultas = ref([])

const carregandoHorarios = ref(false)
const erro = ref(null)
const user = ref(null)

const hhmm = (s) => (s ? s.slice(0, 5) : '')
const toISODate = (d) =>
  `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`

const logErro = (e) => console.error(e.response?.status, e.response?.data ?? e.message)

// ---------- Especialidade e valor ----------
async function carregarEspecialidades() {
  try {
    const { data } = await api.get('/profissionais/me/especialidades')
    especialidades.value = data
    if (data.length) especialidadeId.value = data[0].id
  } catch (e) {
    erro.value = 'Não foi possível carregar as especialidades.'
    logErro(e)
  }
}

watch(especialidadeId, (id) => {
  const esp = especialidades.value.find((e) => String(e.id) === String(id))
  valor.value = Number(esp?.valor_consulta ?? 0)
})

async function salvarValor() {
  const esp = especialidades.value.find((e) => String(e.id) === String(especialidadeId.value))
  if (!esp) return
  try {
    await api.patch(`/profissionais/me/especialidades/${esp.id}`, { valor_consulta: valor.value })
    esp.valor_consulta = valor.value
    erro.value = null
  } catch (e) {
    erro.value = 'Não foi possível salvar o valor da consulta.'
    logErro(e)
  }
}

// TODO: criar essa rota (ou trocar pelo nome real)
const gerenciarEspecialidades = () => router.push({ name: 'gerenciarEspecialidadesDoProfissional' })

// ---------- Faixas e horários do dia ----------
async function carregarFaixas() {
  try {
    const { data } = await api.get('/profissionais/me/faixas-horario', {
      params: { data: toISODate(dataSelecionada.value) },
    })
    faixas.value = data.faixas.map((f, i) => ({
      key: f.id ?? `f-${i}`,
      inicio: hhmm(f.inicio),
      fim: hhmm(f.fim),
    }))
  } catch (e) {
    erro.value = 'Não foi possível carregar as faixas de horário.'
    logErro(e)
  }
}

async function carregarHorarios() {
  carregandoHorarios.value = true
  try {
    const { data } = await api.get('/profissionais/me/horarios', {
      params: { data: toISODate(dataSelecionada.value) },
    })
    horarios.value = data.map((h) => ({ ...h, inicio: hhmm(h.inicio), fim: hhmm(h.fim) }))
  } catch (e) {
    erro.value = 'Não foi possível carregar os horários.'
    logErro(e)
  } finally {
    carregandoHorarios.value = false
  }
}

async function carregarCalendario() {
  try {
    const { data } = await api.get('/profissionais/me/calendario', {
      params: { ano: mesVisivel.value.ano, mes: mesVisivel.value.mes },
    })
    diasComConsultas.value = data.dias_com_consultas
  } catch (e) {
    logErro(e)
  }
}

// salva automaticamente a cada alteração; faixas incompletas esperam o preenchimento
async function salvarFaixas() {
  const preenchidas = faixas.value.filter((f) => f.inicio && f.fim)
  if (preenchidas.some((f) => f.inicio >= f.fim)) {
    erro.value = 'O horário final deve ser depois do horário inicial.'
    return
  }
  try {
    await api.put('/profissionais/me/faixas-horario', {
      data: toISODate(dataSelecionada.value),
      faixas: preenchidas.map(({ inicio, fim }) => ({ inicio, fim })),
    })
    erro.value = null
    await Promise.all([carregarHorarios(), carregarCalendario()])
  } catch (e) {
    erro.value = 'Não foi possível salvar as faixas de horário.'
    logErro(e)
  }
}

async function bloquearHorario(h) {
  const anterior = horarios.value
  horarios.value = anterior.filter((x) => x.id !== h.id) // otimista
  try {
    await api.post(`/profissionais/me/horarios/${h.id}/bloquear`)
    carregarCalendario()
  } catch (e) {
    horarios.value = anterior
    erro.value = 'Não foi possível bloquear o horário.'
    logErro(e)
  }
}

// ---------- Calendário ----------
function mudarMes(delta) {
  let { ano, mes } = mesVisivel.value
  mes += delta
  if (mes < 1) { mes = 12; ano-- }
  if (mes > 12) { mes = 1; ano++ }
  mesVisivel.value = { ano, mes }
}

function irParaHoje() {
  const h = new Date()
  mesVisivel.value = { ano: h.getFullYear(), mes: h.getMonth() + 1 }
  dataSelecionada.value = h
}

watch(dataSelecionada, () => {
  carregarFaixas()
  carregarHorarios()
})
watch(mesVisivel, carregarCalendario)

function logout() {
  api.clearAccessToken()
  user.value = null
}

onMounted(async () => {
  try {
    const { data } = await api.get('/api/v1/auth/eu')
    user.value = { name: data.nome, role: 'Profissional' }
  } catch (e) {
    erro.value = `Não foi possível carregar o perfil: ${e.message}`
  }

  carregarEspecialidades()
  carregarFaixas()
  carregarHorarios()
  carregarCalendario()
})
</script>

<template>
  <div class="flex min-h-screen flex-col bg-[#f8faff]">
    <AppHeader :user="user" @logout="logout" />

    <main class="mx-auto flex w-full max-w-300 flex-1 flex-col gap-6 px-12 pb-12">
      <BackLink />
      <h1 class="text-3xl font-bold tracking-tight text-[#0b2f5b] md:text-4xl">
        Configuração de Agenda e Consultas
      </h1>

      <p v-if="erro" class="text-sm text-red-700">{{ erro }}</p>

      <CardEspecialidadeValor
        v-model:especialidade-id="especialidadeId"
        v-model:valor="valor"
        :especialidades="especialidades"
        @salvar-valor="salvarValor"
        @gerenciar="gerenciarEspecialidades"
      />

    <section class="rounded-xl bg-white p-6 shadow-[0_2px_12px_rgba(11,47,91,0.08)]">
      <div class="mb-6 flex items-center gap-3 border-b border-[#eef0f6] pb-4">
        <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-[#eef2ff] text-[#0b2f5b]">
          <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="4" width="18" height="18" rx="2" /><path d="M16 2v4M8 2v4M3 10h18" />
          </svg>
        </div>
        <div>
          <h2 class="text-base text-[#0b2f5b]">Dias de Atendimento e Faixas de Horário</h2>
          <p class="text-[11px] text-gray-500">Selecione sua disponibilidade</p>
        </div>
      </div>

      <div class="grid grid-cols-1 items-start gap-8 lg:grid-cols-[1.45fr_1fr]">
        <div class="flex flex-col gap-6">
          <FaixasHorario v-model:faixas="faixas" @salvar="salvarFaixas" />
          <HorariosAgendados
            :horarios="horarios"
            :carregando="carregandoHorarios"
            @bloquear="bloquearHorario"
          />
        </div>

        <CalendarioMensal
          v-model:data="dataSelecionada"
          variante="suave"
          :ano="mesVisivel.ano"
          :mes="mesVisivel.mes"
          :dias-marcados="diasComConsultas"
          @mes-anterior="mudarMes(-1)"
          @mes-seguinte="mudarMes(1)"
          @hoje="irParaHoje"
        />
      </div>
      </section>
    </main>
  </div>
</template>