<script setup>
/**
 * RetornoPagamentoView — volta do checkout do Mercado Pago (/pagamento/retorno).
 *
 * O Mercado Pago anexa à URL payment_id / collection_id e external_reference (id da
 * consulta). O status mostrado NUNCA vem da URL: a tela confirma no backend
 * (GET /api/v1/pagamento/retorno), que consulta o Mercado Pago e grava o status local.
 * Sem id de pagamento (ex.: o paciente voltou sem pagar), usa GET /api/v1/pagamento/{id}.
 *
 * Estados: aprovado · pendente · recusado · cancelado.
 */
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import AppHeader from '@/components/shared/AppHeader.vue'
import { api } from '@/services/api'
import { infoStatusPagamento, nomeMetodo } from '@/utils/pagamento'

const route = useRoute()

const carregando = ref(true)
const atualizando = ref(false)
const erro = ref('')
const resultado = ref(null) // { id_consulta, status, metodo, payment_id }

const info = computed(() => infoStatusPagamento(resultado.value?.status))
const idConsulta = computed(() => resultado.value?.id_consulta ?? (Number(route.query.external_reference) || null))

const texto = (valor) => (typeof valor === 'string' && valor && valor !== 'null' ? valor : null)

async function confirmar() {
  const paymentId = texto(route.query.payment_id)
  const collectionId = texto(route.query.collection_id)
  const referencia = texto(route.query.external_reference)

  if (paymentId || collectionId) {
    return api.get('/api/v1/pagamento/retorno', {
      payment_id: paymentId,
      collection_id: collectionId,
      external_reference: referencia,
    })
  }
  if (referencia) {
    const pagamento = await api.get(`/api/v1/pagamento/${referencia}`)
    return { ...pagamento, id_consulta: Number(referencia) }
  }
  throw new Error('Não encontramos os dados do pagamento. Confira o status em Meus Agendamentos.')
}

async function carregar() {
  erro.value = ''
  try {
    resultado.value = await confirmar()
  } catch (e) {
    erro.value = e.message || 'Não foi possível confirmar o pagamento.'
  } finally {
    carregando.value = false
  }
}

async function atualizar() {
  if (!idConsulta.value || atualizando.value) return
  atualizando.value = true
  erro.value = ''
  try {
    const pagamento = await api.get(`/api/v1/pagamento/${idConsulta.value}`)
    resultado.value = { ...resultado.value, ...pagamento }
  } catch (e) {
    erro.value = e.message || 'Não foi possível atualizar o status.'
  } finally {
    atualizando.value = false
  }
}

onMounted(carregar)
</script>

<template>
  <div class="flex min-h-screen flex-col bg-[#f8faff]">
    <AppHeader />

    <main class="mx-auto flex w-full max-w-[640px] flex-1 flex-col items-center px-6 pb-12 pt-10 text-center">
      <p v-if="carregando" class="rounded-xl bg-white p-6 text-sm text-[#59636d]" role="status">
        Confirmando o pagamento com o Mercado Pago...
      </p>

      <template v-else-if="info">
        <div class="flex size-24 items-center justify-center rounded-full" :class="info.fundo">
          <svg class="size-12" :class="info.cor" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" :d="info.icone" />
          </svg>
        </div>
        <h1 class="mt-6 text-3xl font-bold text-[#0b2f5b]">{{ info.titulo }}</h1>
        <p class="mt-3 max-w-[460px] text-gray-600">{{ info.mensagem }}</p>

        <dl class="mt-6 w-full rounded-xl border border-gray-200 bg-white p-5 text-left text-sm shadow-sm">
          <div class="flex justify-between border-b border-gray-100 py-2">
            <dt class="text-gray-500">Status</dt>
            <dd class="font-semibold" :class="info.cor">{{ info.rotulo }}</dd>
          </div>
          <div v-if="resultado.metodo" class="flex justify-between border-b border-gray-100 py-2">
            <dt class="text-gray-500">Forma de pagamento</dt>
            <dd class="font-semibold text-[#0b2f5b]">{{ nomeMetodo(resultado.metodo) }}</dd>
          </div>
          <div v-if="idConsulta" class="flex justify-between border-b border-gray-100 py-2">
            <dt class="text-gray-500">Consulta</dt>
            <dd class="font-semibold text-[#0b2f5b]">#{{ idConsulta }}</dd>
          </div>
          <div v-if="resultado.payment_id" class="flex justify-between py-2">
            <dt class="text-gray-500">Transação Mercado Pago</dt>
            <dd class="font-mono font-semibold text-[#0b2f5b]">{{ resultado.payment_id }}</dd>
          </div>
        </dl>

        <div class="mt-8 grid w-full gap-3 sm:grid-cols-2">
          <button
            v-if="resultado.status === 'pendente'"
            type="button"
            class="flex h-12 items-center justify-center rounded-lg bg-[#00a0b0] font-semibold text-white hover:bg-[#008a98] disabled:opacity-60"
            :disabled="atualizando"
            @click="atualizar"
          >
            {{ atualizando ? 'Verificando...' : 'Verificar novamente' }}
          </button>
          <RouterLink
            v-else-if="(resultado.status === 'recusado' || resultado.status === 'cancelado') && idConsulta"
            :to="{ name: 'pagamento-consulta', params: { idConsulta } }"
            class="flex h-12 items-center justify-center rounded-lg bg-[#00a0b0] font-semibold text-white hover:bg-[#008a98]"
          >
            Tentar novamente
          </RouterLink>
          <RouterLink
            :to="{ name: 'meusAgendamentos' }"
            class="flex h-12 items-center justify-center rounded-lg bg-[#0b2f5b] font-semibold text-white hover:bg-[#0b417d]"
            :class="resultado.status === 'aprovado' ? 'sm:col-span-2' : ''"
          >
            Ver Meus Agendamentos
          </RouterLink>
        </div>
      </template>

      <p v-if="erro" class="mt-6 w-full rounded-lg bg-[#fdecef] p-3 text-sm text-[#c02a46]" role="alert">
        {{ erro }}
        <RouterLink :to="{ name: 'meusAgendamentos' }" class="font-semibold underline">Meus Agendamentos</RouterLink>
      </p>
    </main>
  </div>
</template>
