<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'
import AppHeader from '@/components/shared/AppHeader.vue'
import ResumoDia from '@/components/shared/resumoDia.vue'
import ProximoAtendimento from '@/components/shared/proximoAtendimento.vue'
import AgendaHoje from '@/components/shared/agendaHoje.vue'
import CalendarioMensal from '@/components/shared/calendario.vue'

const router = useRouter()

const hoje = new Date()
const dataSelecionada = ref(hoje)
const mesVisivel = ref({ ano: hoje.getFullYear(), mes: hoje.getMonth() + 1 })

const profissional = ref(null)
const usuario = ref(null)
const headerUser = computed(() =>
  usuario.value ? { name: usuario.value.nome, role: 'Profissional' } : null,
)
const valoresPorEspecialidade = ref({})
const resumo = ref({ total_agendados: 0, faturamento_previsto: 0 })
const proximo = ref(null)
const agenda = ref([])
const diasComConsultas = ref([])
const consultasDoMes = ref([])
const fotoComErro = ref(false)
const carregando = ref(false)
const erro = ref(null)
const erroValores = ref(null)
const erroHorarios = ref(null)

const DIAS = ['Domingo', 'Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado']
const MESES = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

// "Segunda-feira, 18 de Novembro"
const dataTexto = computed(() => {
  const d = dataSelecionada.value
  return `${DIAS[d.getDay()]}, ${d.getDate()} de ${MESES[d.getMonth()]}`
})

const iniciais = computed(() =>
  (profissional.value?.nome ?? '')
    .replace(/^dra?\.?\s+/i, '')
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((p) => p[0].toUpperCase())
    .join(''),
)

const toISODate = (d) =>
  `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`

function normalizarConsulta(consulta, horarios) {
  const inicio = new Date(`${consulta.data}T${consulta.hora}`)
  const horaFim = horarios.get(`${consulta.id_esp_prof}:${consulta.hora}`)
  const fim = horaFim
    ? new Date(`${consulta.data}T${horaFim}`)
    : new Date(inicio.getTime() + 30 * 60 * 1000)

  return {
    id: consulta.id_consulta,
    id_esp_prof: consulta.id_esp_prof,
    inicio: `${consulta.data}T${consulta.hora}`,
    fim: `${toISODate(fim)}T${String(fim.getHours()).padStart(2, '0')}:${String(fim.getMinutes()).padStart(2, '0')}:00`,
    paciente_nome: consulta.paciente.nome,
    tipo: consulta.tipo,
    status: consulta.status,
    especialidade: consulta.especialidade,
  }
}

async function atualizarDia() {
  erroHorarios.value = null
  const dataAlvo = toISODate(dataSelecionada.value)
  const consultas = consultasDoMes.value.filter(
    (consulta) => consulta.data === dataAlvo && !['cancelada', 'cancelado'].includes(consulta.status),
  )
  const vinculos = [...new Set(consultas.map((consulta) => consulta.id_esp_prof))]
  const respostasHorarios = await Promise.allSettled(
    vinculos.map((id) =>
      api.get('/profissional/horarios', {
        params: { id_esp_prof: id, data: dataAlvo },
      }),
    ),
  )
  const horarios = new Map()
  respostasHorarios.forEach((resultado, indice) => {
    if (resultado.status === 'rejected') {
      erroHorarios.value =
        resultado.reason.message || 'Não foi possível carregar os horários cadastrados.'
      return
    }
    for (const horario of resultado.value.data) {
      horarios.set(`${vinculos[indice]}:${horario.hora_inicio}`, horario.hora_fim)
    }
  })
  const atendimentos = consultas.map((consulta) => normalizarConsulta(consulta, horarios))
  const finalizados = ['realizada', 'realizado']
  const agora = new Date()

  agenda.value = atendimentos
  resumo.value = {
    total_agendados: atendimentos.length,
    faturamento_previsto: consultas.reduce((total, consulta) => {
      if (finalizados.includes(consulta.status)) return total
      return total + (valoresPorEspecialidade.value[consulta.especialidade] ?? 0)
    }, 0),
  }
  const indiceProximo = consultas.findIndex(
    (consulta) =>
      !finalizados.includes(consulta.status) &&
      new Date(`${consulta.data}T${consulta.hora}`) >= agora,
  )
  proximo.value = indiceProximo >= 0 ? atendimentos[indiceProximo] : null
}

async function carregarPerfil() {
  carregando.value = true
  erro.value = null
  try {
    const { data: conta } = await api.get('/api/v1/auth/eu')
    if (conta.perfil !== 'profissional' || !conta.id_profissional) {
      throw new Error('Esta página está disponível apenas para profissionais.')
    }
    usuario.value = conta
    profissional.value = {
      nome: conta.nome,
      foto_url: api.url(`/profissionais/buscar-imagem-profissional/${conta.id}`),
    }

    try {
      const { data: perfil } = await api.get(
        `/profissionais/buscar-info-profissional/${conta.id}`,
      )
      valoresPorEspecialidade.value = Object.fromEntries(
        perfil.especialidade.map((item) => [item.nome, Number(item.valor)]),
      )
    } catch (e) {
      valoresPorEspecialidade.value = {}
      erroValores.value = `Não foi possível carregar os valores das especialidades: ${e.message}`
    }
    await carregarMes()
  } catch (e) {
    erro.value = e.message || 'Não foi possível carregar o perfil do profissional.'
  } finally {
    carregando.value = false
  }
}

async function carregarMes() {
  if (!usuario.value?.id_profissional) return
  carregando.value = true
  erro.value = null
  try {
    const ano = mesVisivel.value.ano
    const mes = mesVisivel.value.mes
    const primeiroDia = new Date(ano, mes - 1, 1)
    const ultimoDia = new Date(ano, mes, 0)
    const { data } = await api.get(
      `/api/v1/consultas_profissionais/${usuario.value.id_profissional}/consultas`,
      {
        params: {
          status: '',
          data_inicio: toISODate(primeiroDia),
          data_fim: toISODate(ultimoDia),
        },
      },
    )
    consultasDoMes.value = data
    diasComConsultas.value = [
      ...new Set(
        data
          .filter((consulta) => !['cancelada', 'cancelado'].includes(consulta.status))
          .map((consulta) => Number(consulta.data.slice(8, 10))),
      ),
    ]
    await atualizarDia()
  } catch (e) {
    erro.value = e.message || 'Não foi possível carregar os horários e consultas.'
  } finally {
    carregando.value = false
  }
}

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

async function entrarNaChamada(id) {
  try {
    const { data } = await api.get(`/api/v1/consultas/${id}/videochamada`)
    if (!data.meet_link) {
      erro.value = 'Esta consulta não possui uma chamada virtual disponível.'
      return
    }
    window.open(data.meet_link, '_blank', 'noopener,noreferrer')
  } catch (e) {
    erro.value = e.message || 'Não foi possível abrir a chamada virtual.'
  }
}

const adicionarConsulta = () => router.push({ name: 'adicionarConsultaDoProfissional' })

function logout() {
  api.clearAccessToken()
  usuario.value = null
}

watch(dataSelecionada, atualizarDia)
watch(mesVisivel, carregarMes)

onMounted(carregarPerfil)
</script>

<template>
  <div class="flex min-h-screen flex-col bg-[#f8faff]">
    <AppHeader :user="headerUser" @logout="logout" />

    <main class="mx-auto flex w-full max-w-300 flex-1 flex-col gap-6 px-12 pb-12">
      <header class="flex items-center justify-between gap-4">
        <div class="flex items-center gap-3">
          <div class="relative h-12 w-12 shrink-0">
            <img
              v-if="profissional?.foto_url && !fotoComErro"
              :src="api.url(profissional.foto_url)"
              alt=""
              class="h-full w-full rounded-full bg-gray-200 object-cover"
              @error="fotoComErro = true"
            />
            <div
              v-else
              class="flex h-full w-full items-center justify-center rounded-full bg-[#0b2f5b] text-sm font-bold text-white"
            >
              {{ iniciais }}
            </div>
          </div>
          <div>
            <p class="text-[10px] font-semibold tracking-wider text-gray-500">PORTAL DO MÉDICO</p>
            <h1 class="text-2xl font-bold text-[#0b2f5b]">{{ profissional?.nome }}</h1>
          </div>
        </div>

        <button
          type="button"
          class="flex cursor-pointer items-center gap-2 rounded-lg bg-[#0b2f5b] px-5 py-3 text-sm font-semibold text-white transition hover:bg-[#12407a]"
          @click="adicionarConsulta"
        >
          <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10" /><path d="M8 12h8M12 8v8" />
          </svg>
          Adicionar Consulta
        </button>
      </header>

      <p
        v-if="erro || erroValores || erroHorarios"
        class="text-sm text-red-700"
        role="alert"
      >
        {{ erro || erroValores || erroHorarios }}
      </p>

      <ResumoDia :data="dataSelecionada" :data-texto="dataTexto" :resumo="resumo" />

      <ProximoAtendimento :atendimento="proximo" @entrar="entrarNaChamada" />

      <div class="grid grid-cols-1 items-start gap-6 lg:grid-cols-[1.6fr_1fr]">
        <AgendaHoje :data-texto="dataTexto" :agenda="agenda" :carregando="carregando" />
        <CalendarioMensal
          v-model:data="dataSelecionada"
          :ano="mesVisivel.ano"
          :mes="mesVisivel.mes"
          :dias-marcados="diasComConsultas"
          @mes-anterior="mudarMes(-1)"
          @mes-seguinte="mudarMes(1)"
          @hoje="irParaHoje"
        />
      </div>
    </main>
  </div>
</template>