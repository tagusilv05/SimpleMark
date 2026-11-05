<script setup>
/**
 * PagamentoView — pagamento de uma consulta do paciente logado.
 *
 * Rota /pagamento/:idConsulta (só paciente). Todos os dados vêm da API:
 *   GET  /consultas/minhas/{id}            consulta, valor e status do pagamento
 *   GET  /api/v1/pagamento/{id}            status sincronizado com o Mercado Pago
 *   POST /api/v1/pagamento/preferencia     { id_consulta, metodo } -> link do checkout
 *
 * O checkout do Mercado Pago só aceita a forma escolhida aqui (Pix, cartão ou boleto)
 * e devolve o paciente para /pagamento/retorno.
 */
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import AppHeader from '@/components/shared/AppHeader.vue'
import BackLink from '@/components/shared/BackLink.vue'
import MetodoPagamento from '@/components/pagamento/MetodoPagamento.vue'
import ResumoConsulta from '@/components/pagamento/ResumoConsulta.vue'
import { api } from '@/services/api'
import { infoStatusPagamento, nomeMetodo } from '@/utils/pagamento'

const route = useRoute()
const consulta = ref(null)
const pagamento = ref(null) // { status, metodo, data, hora } ou null se ainda não houve tentativa
const metodo = ref('pix')
const carregando = ref(false)
const processando = ref(false)
const atualizando = ref(false)
const erro = ref('')

const CONSULTA_CANCELADA = new Set(['cancelada', 'cancelado'])

const data = computed(() =>
  consulta.value?.data
    ? new Intl.DateTimeFormat('pt-BR', { day: '2-digit', month: 'long', year: 'numeric' }).format(
        new Date(`${consulta.value.data}T00:00:00`),
      )
    : '',
)
const horario = computed(() => consulta.value?.hora?.slice(0, 5) ?? '')
const valor = computed(() =>
  consulta.value?.valor == null
    ? ''
    : new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(Number(consulta.value.valor)),
)
const tipo = computed(() => {
  const t = consulta.value?.tipo ?? ''
  return t ? t.charAt(0).toUpperCase() + t.slice(1) : ''
})

const statusPagamento = computed(() => pagamento.value?.status ?? consulta.value?.pagamento_status ?? null)
const infoStatus = computed(() => infoStatusPagamento(statusPagamento.value))

const consultaPassou = computed(() => {
  if (!consulta.value) return false
  return new Date(`${consulta.value.data}T${consulta.value.hora}`).getTime() <= Date.now()
})

// Motivo para não deixar pagar (null = pode pagar)
const bloqueio = computed(() => {
  if (!consulta.value) return 'Consulta indisponível.'
  if (statusPagamento.value === 'aprovado') return 'Esta consulta já está paga.'
  if (CONSULTA_CANCELADA.has(consulta.value.status)) return 'Esta consulta foi cancelada.'
  if (consulta.value.status === 'realizada') return 'Esta consulta já foi realizada.'
  if (consultaPassou.value) return 'O horário desta consulta já passou.'
  return null
})

const rotuloBotao = computed(() => {
  if (statusPagamento.value === 'pendente') return 'Gerar novo pagamento'
  if (statusPagamento.value === 'recusado' || statusPagamento.value === 'cancelado') return 'Tentar novamente'
  return 'Finalizar Pagamento'
})

async function carregar() {
  consulta.value = null
  pagamento.value = null
  erro.value = ''
  carregando.value = true
  try {
    consulta.value = await api.get(`/consultas/minhas/${route.params.idConsulta}`)
    if (consulta.value.pagamento_status) await atualizarStatus({ silencioso: true })
    if (pagamento.value?.metodo) metodo.value = pagamento.value.metodo
  } catch (error) {
    erro.value = error.message || 'Não foi possível carregar os dados da consulta.'
  } finally {
    carregando.value = false
  }
}

// Confere o status no Mercado Pago (útil para Pix e boleto, que compensam depois)
async function atualizarStatus({ silencioso = false } = {}) {
  if (!consulta.value || atualizando.value) return
  atualizando.value = true
  if (!silencioso) erro.value = ''
  try {
    pagamento.value = await api.get(`/api/v1/pagamento/${consulta.value.id_consulta}`)
  } catch (error) {
    if (!silencioso && error.status !== 404) erro.value = error.message || 'Não foi possível atualizar o status.'
  } finally {
    atualizando.value = false
  }
}

async function finalizar() {
  if (!consulta.value || processando.value || bloqueio.value) return
  processando.value = true
  erro.value = ''
  try {
    const resposta = await api.post('/api/v1/pagamento/preferencia', {
      id_consulta: consulta.value.id_consulta,
      metodo: metodo.value,
    })
    window.location.assign(resposta.init_point)
  } catch (error) {
    erro.value = error.message || 'Não foi possível iniciar o pagamento.'
    processando.value = false
  }
}

onMounted(carregar)
</script>

<template>
  <div class="min-h-screen bg-[#f8f8ff] text-[#073b57]">
    <AppHeader />
    <BackLink label="Voltar" to="/paciente/agendamentos" />
    <main class="mx-auto max-w-[1120px] px-6 pb-12 pt-6">
      <h1 class="text-2xl font-bold sm:text-3xl">Pagamento</h1>
      <p class="mt-1 text-xs text-[#59636d]">Confirme os detalhes da sua consulta e escolha a melhor forma de pagamento.</p>

      <p v-if="carregando" class="mt-5 rounded-xl bg-white p-6 text-sm text-[#59636d]">Carregando os dados da consulta...</p>

      <template v-else-if="consulta">
        <div
          v-if="infoStatus"
          class="mt-5 flex flex-col gap-3 rounded-xl p-4 sm:flex-row sm:items-center sm:justify-between"
          :class="infoStatus.fundo"
          role="status"
        >
          <div class="flex items-start gap-3">
            <svg class="size-6 shrink-0" :class="infoStatus.cor" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" :d="infoStatus.icone" />
            </svg>
            <div>
              <p class="text-sm font-semibold" :class="infoStatus.cor">
                Pagamento {{ infoStatus.rotulo.toLowerCase() }}<span v-if="pagamento?.metodo"> · {{ nomeMetodo(pagamento.metodo) }}</span>
              </p>
              <p class="text-xs text-[#59636d]">{{ infoStatus.mensagem }}</p>
            </div>
          </div>
          <button
            v-if="statusPagamento === 'pendente'"
            type="button"
            class="shrink-0 rounded-lg border border-[#073b57] px-3 py-2 text-xs font-semibold text-[#073b57] hover:bg-white disabled:opacity-60"
            :disabled="atualizando"
            @click="atualizarStatus()"
          >
            {{ atualizando ? 'Verificando...' : 'Verificar status' }}
          </button>
        </div>

        <div class="mt-5 grid items-start gap-4 lg:grid-cols-[minmax(0,1fr)_300px]">
          <MetodoPagamento v-model="metodo" :desabilitado="Boolean(bloqueio) || processando" />
          <ResumoConsulta
            :profissional="consulta.profissional?.nome"
            :especialidade="consulta.profissional?.especialidade"
            :data="data"
            :horario="horario"
            :tipo="tipo"
            :valor="valor"
            :metodo="nomeMetodo(metodo)"
            :imagem="consulta.profissional?.path_imagem || ''"
            :disponivel="!bloqueio"
            :processando="processando"
            :rotulo-botao="rotuloBotao"
            @finalizar="finalizar"
          />
        </div>
        <p v-if="bloqueio" class="mt-4 rounded-lg bg-[#eef2ff] p-3 text-sm text-[#59636d]" role="status">
          {{ bloqueio }}
          <RouterLink :to="{ name: 'meusAgendamentos' }" class="font-semibold underline">Ver meus agendamentos</RouterLink>
        </p>
      </template>

      <p v-if="erro" class="mt-4 rounded-lg bg-[#fdecef] p-3 text-sm text-[#c02a46]" role="alert">{{ erro }}</p>
    </main>
  </div>
</template>
