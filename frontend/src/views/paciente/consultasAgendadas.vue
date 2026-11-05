<script setup>
/**
 * Meus Agendamentos — lista das consultas do paciente logado
 *
 * API:
 *   GET   /consultas/minhas                                   lista (até 100)
 *   GET   /api/v1/avaliacoes/profissionais/{id}/media         nota média de cada profissional
 *   GET   /api/v1/consultas/{id}/videochamada                 link do Jitsi para entrar
 *   PATCH /api/v1/consultas/{id}/cancelar                     cancela a consulta
 *
 * Situação mostrada no cartão (derivada do status da consulta e do pagamento):
 *   pagamento  agendada, pagamento pendente/recusado/cancelado ou não iniciado -> "Realizar pagamento"
 *   confirmado pagamento aprovado e horário por vir     -> "Entrar na chamada" + cancelar
 *   realizada  consulta realizada                       -> "Avaliar" (se ainda não avaliou)
 *   expirado   horário passou sem a consulta acontecer  -> "Link expirado"
 *   cancelada  consulta cancelada
 */
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/services/api'

const router = useRouter()

const agendamentos = ref([])
const carregando = ref(true)
const erro = ref('')
const aviso = ref('')
const emAcao = ref(null) // id da consulta com ação em andamento
const detalhesAbertos = ref(new Set())

const MESES = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
// Depois deste tempo do início, a consulta não realizada é tratada como expirada
const TOLERANCIA_MS = 60 * 60 * 1000

const formatarData = (iso) => {
  const [ano, mes, dia] = iso.split('-')
  return `${dia} ${MESES[Number(mes) - 1]} ${ano}`
}
const formatarValor = (v) =>
  Number(v).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
const capitalizar = (t) => (t ? t.charAt(0).toUpperCase() + t.slice(1) : '')

function situacao(c) {
  if (c.status === 'cancelada' || c.status === 'cancelado') return 'cancelada'
  if (c.status === 'realizada' || c.status === 'realizado') return 'realizada'
  if (new Date(`${c.data}T${c.hora}`).getTime() + TOLERANCIA_MS < Date.now()) return 'expirado'
  if (c.status === 'confirmada' || c.pagamento_status === 'aprovado') return 'confirmado'
  return 'pagamento'
}

function montar(c, medias) {
  return {
    id: c.id_consulta,
    data: formatarData(c.data),
    horario: c.hora.slice(0, 5),
    tipo: capitalizar(c.tipo),
    valor: formatarValor(c.valor),
    pagamento: c.pagamento_status,
    especialidade: c.profissional.especialidade,
    status: situacao(c),
    podeAvaliar: c.pode_avaliar,
    avaliacao: c.avaliacao,
    profissional: {
      id: c.profissional.id_profissional,
      nome: c.profissional.nome,
      nota: medias.get(c.profissional.id_profissional) ?? null,
    },
  }
}

async function carregar() {
  carregando.value = true
  erro.value = ''
  try {
    const { itens } = await api.get('/consultas/minhas', { limit: 100 })

    // Nota média de cada profissional (uma chamada por profissional; falha não trava a lista)
    const ids = [...new Set(itens.map((c) => c.profissional.id_profissional))]
    const respostas = await Promise.allSettled(
      ids.map((id) => api.get(`/api/v1/avaliacoes/profissionais/${id}/media`)),
    )
    const medias = new Map()
    respostas.forEach((r, i) => {
      if (r.status === 'fulfilled' && r.value?.media != null) medias.set(ids[i], Number(r.value.media))
    })

    agendamentos.value = itens.map((c) => montar(c, medias))
  } catch (e) {
    erro.value = e.message || 'Não foi possível carregar seus agendamentos.'
  } finally {
    carregando.value = false
  }
}

const iniciais = (nome) =>
  nome
    .replace(/^dra?\.?\s+/i, '')
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((p) => p[0].toUpperCase())
    .join('')

async function entrarNaChamada(id) {
  if (emAcao.value) return
  emAcao.value = id
  erro.value = ''
  // Abre a aba já no clique (antes do await) para o navegador não bloquear o pop-up
  const aba = window.open('', '_blank')
  try {
    const dados = await api.get(`/api/v1/consultas/${id}/videochamada`)
    if (!dados.meet_link) throw new Error('A chamada desta consulta ainda não está disponível.')
    if (aba) {
      aba.opener = null
      aba.location.href = dados.meet_link
    } else {
      window.location.href = dados.meet_link
    }
  } catch (e) {
    aba?.close()
    erro.value = e.message || 'Não foi possível abrir a chamada.'
  } finally {
    emAcao.value = null
  }
}

async function cancelar(id) {
  if (emAcao.value || !window.confirm('Deseja realmente cancelar esta consulta?')) return
  emAcao.value = id
  erro.value = ''
  aviso.value = ''
  try {
    await api.patch(`/api/v1/consultas/${id}/cancelar`)
    const ag = agendamentos.value.find((a) => a.id === id)
    if (ag) {
      ag.status = 'cancelada'
      // Pagamento não aprovado é cancelado junto com a consulta (regra do backend)
      if (ag.pagamento && ag.pagamento !== 'aprovado') ag.pagamento = 'cancelado'
    }
    aviso.value = 'Consulta cancelada.'
  } catch (e) {
    erro.value = e.message || 'Não foi possível cancelar a consulta.'
  } finally {
    emAcao.value = null
  }
}

function alternarDetalhes(id) {
  const abertos = new Set(detalhesAbertos.value)
  abertos.has(id) ? abertos.delete(id) : abertos.add(id)
  detalhesAbertos.value = abertos
  if (abertos.has(id)) carregarDocumentos(id)
}

// Receitas e atestados emitidos na consulta: { [idConsulta]: lista | 'carregando' | 'erro' }
const documentos = ref({})

async function carregarDocumentos(id) {
  if (Array.isArray(documentos.value[id])) return
  documentos.value = { ...documentos.value, [id]: 'carregando' }
  try {
    const lista = await api.get(`/api/v1/consultas/${id}/documentos`)
    documentos.value = { ...documentos.value, [id]: lista }
  } catch {
    documentos.value = { ...documentos.value, [id]: 'erro' }
  }
}

const ROTULO_DOCUMENTO = { RECEITA: 'Receita médica', ATESTADO: 'Atestado médico' }
const dataDocumento = (iso) => (iso ? new Date(iso).toLocaleDateString('pt-BR') : '')

const ROTULO_PAGAMENTO = { aprovado: 'Aprovado', pendente: 'Pendente' }

const verMedico = (id) => router.push({ name: 'perfil-profissional', params: { id } })
const pagar = (id) => router.push({ name: 'pagamento-consulta', params: { idConsulta: id } })
const avaliar = (id) => router.push({ name: 'avaliarConsulta', params: { id } })

onMounted(carregar)
</script>

<template>
  <div class="flex max-w-215 flex-wrap items-center justify-between gap-4">
    <h1 class="text-4xl font-bold text-[#0b2f5b]">Meus Agendamentos</h1>
    <RouterLink
      :to="{ name: 'agendamento' }"
      class="rounded-lg bg-[#0b2f5b] px-5 py-3 text-sm font-semibold text-white transition-colors hover:bg-[#0b417d]"
    >
      + Agendar nova consulta
    </RouterLink>
  </div>

  <p v-if="erro" class="text-sm font-medium text-red-700" role="alert">{{ erro }}</p>
  <p v-if="aviso" class="text-sm font-medium text-green-700" role="status">{{ aviso }}</p>

  <p v-if="carregando" class="text-sm text-gray-500">Carregando seus agendamentos...</p>
  <p v-else-if="!agendamentos.length && !erro" class="text-sm text-gray-500">
    Você ainda não possui agendamentos.
    <RouterLink :to="{ name: 'agendamento' }" class="font-semibold text-[#0b2f5b] underline">Agende sua primeira consulta</RouterLink>
  </p>

  <div class="flex max-w-215 flex-col gap-4">
    <article
      v-for="ag in agendamentos"
      :key="ag.id"
      class="rounded-xl bg-white px-4 py-5 shadow-sm"
    >
      <div class="flex items-start justify-between gap-4">
        <div class="flex items-start gap-3">
          <div
            class="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-[#0b2f5b] text-sm font-bold text-white"
          >
            {{ iniciais(ag.profissional.nome) }}
          </div>

          <div class="flex flex-col gap-1">
            <div class="flex items-center gap-2">
              <h2 class="text-xl font-semibold text-[#0b2f5b]">{{ ag.profissional.nome }}</h2>
              <div
                v-if="ag.profissional.nota !== null"
                class="flex items-center gap-1 text-xs font-semibold text-gray-700"
              >
                <span class="flex text-[#1a9aa6]">
                  <svg
                    v-for="i in 5"
                    :key="i"
                    class="h-3 w-3"
                    :class="i <= Math.round(ag.profissional.nota) ? 'opacity-100' : 'opacity-25'"
                    viewBox="0 0 24 24"
                    fill="currentColor"
                  >
                    <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
                  </svg>
                </span>
                {{ ag.profissional.nota.toFixed(1) }}
              </div>
              <span v-else class="text-xs text-gray-400">Sem avaliações</span>
            </div>

            <p class="text-sm text-gray-500">{{ ag.especialidade }}</p>

            <div class="flex items-center gap-2">
              <span class="rounded bg-[#1a9aa6] px-2 py-0.5 text-[10px] font-bold uppercase text-white">
                {{ ag.tipo }}
              </span>

              <span
                v-if="ag.status === 'confirmado'"
                class="flex items-center gap-1 rounded bg-green-100 px-2 py-0.5 text-[10px] font-semibold text-green-700"
              >
                <svg class="h-3 w-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="12" cy="12" r="10" /><path d="M8 12l3 3 5-6" />
                </svg>
                Confirmado
              </span>
              <span
                v-else-if="ag.status === 'realizada'"
                class="flex items-center gap-1 rounded bg-blue-50 px-2 py-0.5 text-[10px] font-semibold text-[#0b2f5b]"
              >
                <svg class="h-3 w-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="12" cy="12" r="10" /><path d="M8 12l3 3 5-6" />
                </svg>
                Realizada
              </span>
              <span
                v-else-if="ag.status === 'pagamento'"
                class="flex items-center gap-1 rounded bg-amber-100 px-2 py-0.5 text-[10px] font-semibold text-amber-800"
              >
                <svg class="h-3 w-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="12" cy="12" r="10" /><path d="M12 6v6l4 2" />
                </svg>
                {{ ag.pagamento === 'recusado' ? 'Pagamento Recusado' : ag.pagamento === 'pendente' ? 'Pagamento Pendente' : 'Aguardando Pagamento' }}
              </span>
              <span
                v-else-if="ag.status === 'cancelada'"
                class="flex items-center gap-1 rounded bg-gray-200 px-2 py-0.5 text-[10px] font-semibold text-gray-600"
              >
                <svg class="h-3 w-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="12" cy="12" r="10" /><path d="M15 9l-6 6M9 9l6 6" />
                </svg>
                Cancelada
              </span>
              <span
                v-else
                class="flex items-center gap-1 rounded bg-red-100 px-2 py-0.5 text-[10px] font-semibold text-red-700"
              >
                <svg class="h-3 w-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="12" cy="12" r="10" /><path d="M12 8v4M12 16h.01" />
                </svg>
                Prazo Expirado
              </span>
            </div>
          </div>
        </div>

        <div class="flex flex-col gap-2 text-sm font-medium text-[#0b2f5b]">
          <div class="flex items-center gap-2">
            <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="3" y="4" width="18" height="18" rx="2" /><path d="M16 2v4M8 2v4M3 10h18" />
            </svg>
            {{ ag.data }}
          </div>
          <div class="flex items-center gap-2">
            <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10" /><path d="M12 6v6l4 2" />
            </svg>
            {{ ag.horario }}
          </div>
        </div>
      </div>

      <hr class="my-4 border-gray-100" />

      <div class="grid grid-cols-3 gap-4">
        <button
          type="button"
          class="flex cursor-pointer items-center justify-center gap-2 rounded-lg border border-[#0b2f5b] bg-white px-4 py-2 text-xs font-semibold text-[#0b2f5b] transition hover:bg-blue-50"
          @click="verMedico(ag.profissional.id)"
        >
          <svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="8" r="4" /><path d="M4 21c0-4 4-6 8-6s8 2 8 6" />
          </svg>
          Ver informações do médico
        </button>

        <button
          type="button"
          class="flex cursor-pointer items-center justify-center gap-2 rounded-lg border border-[#0b2f5b] bg-white px-4 py-2 text-xs font-semibold text-[#0b2f5b] transition hover:bg-blue-50"
          :aria-expanded="detalhesAbertos.has(ag.id)"
          @click="alternarDetalhes(ag.id)"
        >
          <svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10" /><path d="M12 16v-4M12 8h.01" />
          </svg>
          Detalhes da consulta
        </button>

        <button
          v-if="ag.status === 'pagamento'"
          type="button"
          class="flex cursor-pointer items-center justify-center gap-2 rounded-lg bg-[#0b2f5b] px-4 py-2 text-xs font-semibold text-white transition hover:bg-[#12407a]"
          @click="pagar(ag.id)"
        >
          <svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="2" y="5" width="20" height="14" rx="2" /><path d="M2 10h20" />
          </svg>
          {{ ag.pagamento === 'recusado' || ag.pagamento === 'cancelado' ? 'Tentar Novamente' : ag.pagamento === 'pendente' ? 'Acompanhar Pagamento' : 'Realizar Pagamento' }}
        </button>
        <button
          v-else-if="ag.status === 'confirmado'"
          type="button"
          :disabled="emAcao === ag.id"
          class="flex cursor-pointer items-center justify-center gap-2 rounded-lg bg-[#0b2f5b] px-4 py-2 text-xs font-semibold text-white transition hover:bg-[#12407a] disabled:cursor-wait disabled:opacity-60"
          @click="entrarNaChamada(ag.id)"
        >
          <svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="2" y="6" width="14" height="12" rx="2" /><path d="M16 10l6-3v10l-6-3z" />
          </svg>
          Entrar na Chamada
        </button>
        <button
          v-else-if="ag.status === 'realizada' && ag.podeAvaliar"
          type="button"
          class="flex cursor-pointer items-center justify-center gap-2 rounded-lg bg-[#0b2f5b] px-4 py-2 text-xs font-semibold text-white transition hover:bg-[#12407a]"
          @click="avaliar(ag.id)"
        >
          <svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
          </svg>
          Avaliar Atendimento
        </button>
        <button
          v-else-if="ag.status === 'realizada'"
          type="button"
          disabled
          class="flex cursor-default items-center justify-center gap-2 rounded-lg bg-[#eef2fb] px-4 py-2 text-xs font-semibold text-[#0b2f5b]"
        >
          <svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10" /><path d="M8 12l3 3 5-6" />
          </svg>
          Atendimento Avaliado
        </button>
        <button
          v-else-if="ag.status === 'cancelada'"
          type="button"
          disabled
          class="flex cursor-not-allowed items-center justify-center gap-2 rounded-lg bg-[#eef2fb] px-4 py-2 text-xs font-semibold text-gray-400"
        >
          Consulta Cancelada
        </button>
        <button
          v-else
          type="button"
          disabled
          class="flex cursor-not-allowed items-center justify-center gap-2 rounded-lg bg-[#eef2fb] px-4 py-2 text-xs font-semibold text-gray-400"
        >
          <svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M10 13a5 5 0 007 0l3-3a5 5 0 00-7-7l-1 1M14 11a5 5 0 00-7 0l-3 3a5 5 0 007 7l1-1M3 3l18 18" />
          </svg>
          Link Expirado
        </button>
      </div>

      <dl
        v-if="detalhesAbertos.has(ag.id)"
        class="mt-4 grid grid-cols-2 gap-x-6 gap-y-2 rounded-lg bg-[#f8faff] p-4 text-xs sm:grid-cols-4"
      >
        <div>
          <dt class="font-semibold text-gray-500">Código</dt>
          <dd class="text-[#0b2f5b]">#{{ ag.id }}</dd>
        </div>
        <div>
          <dt class="font-semibold text-gray-500">Valor</dt>
          <dd class="text-[#0b2f5b]">{{ ag.valor }}</dd>
        </div>
        <div>
          <dt class="font-semibold text-gray-500">Pagamento</dt>
          <dd class="text-[#0b2f5b]">{{ ROTULO_PAGAMENTO[ag.pagamento] ?? 'Não iniciado' }}</dd>
        </div>
        <div v-if="ag.avaliacao">
          <dt class="font-semibold text-gray-500">Sua avaliação</dt>
          <dd class="text-[#0b2f5b]">
            {{ ag.avaliacao.avaliacao ? `${ag.avaliacao.avaliacao} de 5 estrelas` : 'Somente comentário' }}
          </dd>
        </div>
      </dl>

      <div v-if="detalhesAbertos.has(ag.id)" class="mt-4 border-t border-gray-100 pt-3 text-xs">
        <p class="mb-2 font-semibold text-gray-500">Documentos da consulta</p>
        <p v-if="documentos[ag.id] === 'carregando'" class="text-gray-500">Carregando documentos...</p>
        <p v-else-if="documentos[ag.id] === 'erro'" class="text-red-700">Não foi possível carregar os documentos.</p>
        <p v-else-if="!documentos[ag.id]?.length" class="text-gray-500">Nenhuma receita ou atestado emitido.</p>
        <ul v-else class="flex flex-col gap-2">
          <li v-for="doc in documentos[ag.id]" :key="doc.documento_id">
            <RouterLink
              :to="{ name: 'documentoDoPaciente', params: { id: doc.documento_id } }"
              class="inline-flex items-center gap-2 font-semibold text-[#0b2f5b] hover:underline"
            >
              📄 {{ ROTULO_DOCUMENTO[doc.tipo] ?? doc.tipo }} · {{ dataDocumento(doc.data_emissao) }} — Abrir / Baixar PDF
            </RouterLink>
          </li>
        </ul>
      </div>

      <div v-if="['confirmado', 'pagamento'].includes(ag.status)" class="mt-4 text-center">
        <button
          type="button"
          :disabled="emAcao === ag.id"
          class="cursor-pointer text-xs font-semibold text-red-700 hover:underline disabled:cursor-wait disabled:opacity-60"
          @click="cancelar(ag.id)"
        >
          Cancelar
        </button>
      </div>
    </article>
  </div>
</template>