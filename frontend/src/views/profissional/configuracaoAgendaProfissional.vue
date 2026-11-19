<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'
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
const salvandoFaixas = ref(false)
const sucesso = ref(null)
const erro = ref(null)
const user = ref(null)

const hhmm = (s) => (s ? s.slice(0, 5) : '')
const toISODate = (d) =>
  `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`

// ---------- Especialidade e valor ----------
async function carregarEspecialidades() {
  const { data } = await api.get(`/profissionais/buscar-info-profissional/${user.value.id}`)
  especialidades.value = data.especialidade.map((especialidade) => ({
    id: especialidade.id_especialidade,
    id_esp_prof: especialidade.id_esp_prof,
    nome: especialidade.nome,
    valor_consulta: Number(especialidade.valor),
  }))
  if (especialidades.value.length) especialidadeId.value = especialidades.value[0].id
}

watch(especialidadeId, (id) => {
  const esp = especialidades.value.find((e) => String(e.id) === String(id))
  valor.value = Number(esp?.valor_consulta ?? 0)
})

async function salvarValor() {
  const esp = especialidades.value.find((e) => String(e.id) === String(especialidadeId.value))
  if (!esp) return
  try {
    await api.put('/profissionais/alterar-valor-consulta', {
      id_usuario: user.value.id,
      id_especialidade: esp.id,
      valor_consulta: valor.value,
    })
    esp.valor_consulta = valor.value
    erro.value = null
  } catch (e) {
    erro.value = e.message || 'Não foi possível salvar o valor da consulta.'
  }
}

const gerenciarEspecialidades = () => router.push({ name: 'gerenciarContaDoProfissional', query: { aba: 'perfil' } })

// ---------- Faixas e horários do dia ----------
async function carregarFaixas() {
  const especialidade = especialidades.value.find(
    (item) => String(item.id) === String(especialidadeId.value),
  )
  if (!especialidade) {
    faixas.value = []
    horarios.value = []
    return
  }

  carregandoHorarios.value = true
  try {
    const { data } = await api.get('/profissional/horarios', {
      params: {
        id_esp_prof: especialidade.id_esp_prof,
        data: toISODate(dataSelecionada.value),
      },
    })
    horarios.value = data.map((horario) => ({
      id: horario.id_horario,
      inicio: hhmm(horario.hora_inicio),
      fim: hhmm(horario.hora_fim),
      ocupado: horario.ocupado,
      especialidade: especialidade.nome,
    }))
    faixas.value = horarios.value.map((horario) => ({
      key: String(horario.id),
      inicio: horario.inicio,
      fim: horario.fim,
    }))
    erro.value = null
  } catch (e) {
    erro.value = e.message || 'Não foi possível carregar os horários.'
  } finally {
    carregandoHorarios.value = false
  }
}

async function carregarCalendario() {
  if (!user.value?.id_profissional) return
  try {
    const primeiroDia = new Date(mesVisivel.value.ano, mesVisivel.value.mes - 1, 1)
    const ultimoDia = new Date(mesVisivel.value.ano, mesVisivel.value.mes, 0)
    const { data } = await api.get(
      `/api/v1/consultas_profissionais/${user.value.id_profissional}/consultas`,
      {
        params: {
          status: '',
          data_inicio: toISODate(primeiroDia),
          data_fim: toISODate(ultimoDia),
        },
      },
    )
    diasComConsultas.value = [
      ...new Set(
        data
          .filter((consulta) => !['cancelada', 'cancelado'].includes(consulta.status))
          .map((consulta) => Number(consulta.data.slice(8, 10))),
      ),
    ]
  } catch (e) {
    erro.value = e.message || 'Não foi possível carregar o calendário.'
  }
}

async function adicionarHorario({ inicio, fim, limpar }) {
  const esp = especialidades.value.find(
    (item) => String(item.id) === String(especialidadeId.value),
  )
  if (!esp) return

  if (!inicio || !fim) {
    erro.value = 'Preencha o horário de início e término antes de adicionar.'
    sucesso.value = null
    return
  }

  if (inicio >= fim) {
    erro.value = 'O horário final deve ser depois do horário inicial.'
    sucesso.value = null
    return
  }

  salvandoFaixas.value = true
  erro.value = null
  sucesso.value = null

  try {
    await api.post('/profissional/horarios', {
      id_esp_prof: esp.id_esp_prof,
      datas: [toISODate(dataSelecionada.value)],
      lista_horarios: [
        {
          hora_inicio: inicio,
          hora_fim: fim,
        },
      ],
    })

    erro.value = null
    sucesso.value = 'Horário adicionado com sucesso!'
    setTimeout(() => {
      if (sucesso.value === 'Horário adicionado com sucesso!') sucesso.value = null
    }, 4000)

    if (typeof limpar === 'function') limpar()

    await Promise.all([carregarFaixas(), carregarCalendario()])
  } catch (e) {
    erro.value = e.message || 'Não foi possível adicionar o horário.'
  } finally {
    salvandoFaixas.value = false
  }
}

async function bloquearHorario(h) {
  if (h.ocupado) {
    erro.value = 'Horários já reservados não podem ser bloqueados.'
    return
  }
  try {
    await api.delete(`/profissional/horarios/${h.id}`)
    erro.value = null
    sucesso.value = 'Horário removido com sucesso!'
    setTimeout(() => {
      if (sucesso.value === 'Horário removido com sucesso!') sucesso.value = null
    }, 3000)
    await Promise.all([carregarFaixas(), carregarCalendario()])
  } catch (e) {
    erro.value = e.message || 'Não foi possível bloquear o horário.'
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
})
watch(especialidadeId, carregarFaixas)
watch(mesVisivel, carregarCalendario)


onMounted(async () => {
  try {
    const { data } = await api.get('/api/v1/auth/eu')
    if (data.perfil !== 'profissional' || !data.id_profissional) {
      throw new Error('Esta página está disponível apenas para profissionais.')
    }
    user.value = { ...data, name: data.nome, role: 'Profissional' }
    await carregarEspecialidades()
    await Promise.all([carregarFaixas(), carregarCalendario()])
  } catch (e) {
    erro.value = e.message || 'Não foi possível carregar o perfil.'
  }
})
</script>

<template>
  <div class="flex min-h-screen flex-col bg-[#f8faff]">
    <AppHeader />

    <main class="mx-auto flex w-full max-w-300 flex-1 flex-col gap-6 px-12 pb-12">
      <BackLink />
      <h1 class="text-3xl font-bold tracking-tight text-[#0b2f5b] md:text-4xl">
        Configuração de Agenda e Consultas
      </h1>

      <p v-if="sucesso" class="rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-sm font-medium text-emerald-700">
        {{ sucesso }}
      </p>
      <p v-if="erro" class="rounded-lg border border-red-200 bg-red-50 p-3 text-sm font-medium text-red-700">
        {{ erro }}
      </p>

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
          <FaixasHorario
            :salvando="salvandoFaixas"
            @adicionar="adicionarHorario"
          />
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