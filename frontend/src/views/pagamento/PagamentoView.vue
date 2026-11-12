<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import AppHeader from '@/components/shared/AppHeader.vue'
import BackLink from '@/components/shared/BackLink.vue'
import MetodoPagamento from '@/components/pagamento/MetodoPagamento.vue'
import ResumoConsulta from '@/components/pagamento/ResumoConsulta.vue'
import { api } from '@/services/api'

const route = useRoute()
const consulta = ref(null)
const usuario = ref(null)
const metodo = ref('pix')
const carregando = ref(false)
const processando = ref(false)
const erro = ref('')
// Aviso mostrado quando o paciente volta do Mercado Pago sem concluir o pagamento
const aviso = ref('')
const pago = ref(false)

// Marca (por aba) que o paciente foi mandado ao checkout desta consulta
const CHAVE_CHECKOUT = 'simplemark:checkout-pendente'
const lerMarca = () => {
  try { return sessionStorage.getItem(CHAVE_CHECKOUT) } catch { return null }
}
const gravarMarca = (id) => {
  try {
    if (id == null) sessionStorage.removeItem(CHAVE_CHECKOUT)
    else sessionStorage.setItem(CHAVE_CHECKOUT, String(id))
  } catch {
    /* sem storage: só não mostra o aviso de retorno */
  }
}
const data = computed(() => consulta.value?.data ? new Intl.DateTimeFormat('pt-BR', { day: '2-digit', month: 'long', year: 'numeric' }).format(new Date(`${consulta.value.data}T00:00:00`)) : 'Sem informação')
const horario = computed(() => consulta.value?.hora?.slice(0, 5) || 'Sem informação')
const valor = computed(() => consulta.value?.valor == null ? 'Sem informação' : new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(Number(consulta.value.valor)))

async function carregar() {
  consulta.value = null
  erro.value = ''
  if (!route.params.idConsulta) return
  carregando.value = true
  try {
    const [detalhe, conta] = await Promise.all([
      api.get(`/consultas/minhas/${route.params.idConsulta}`),
      api.get('/api/v1/auth/eu'),
    ])
    consulta.value = detalhe
    usuario.value = conta
    if (lerMarca() === String(detalhe.id_consulta)) await verificarRetorno()
  } catch (error) {
    erro.value = error.message || 'Dados da consulta: sem informação.'
  } finally {
    carregando.value = false
  }
}

// O paciente voltou do checkout: confere no backend (sincronizado com o Mercado Pago)
// se pagou. Se não pagou, libera de novo as três formas de pagamento.
async function verificarRetorno() {
  gravarMarca(null)
  processando.value = false
  pago.value = false
  aviso.value = ''
  let status = null
  try {
    status = (await api.get(`/api/v1/pagamento/${consulta.value.id_consulta}`)).status
  } catch {
    status = null
  }
  if (status === 'aprovado') {
    pago.value = true
    aviso.value = 'Pagamento aprovado! A consulta está confirmada.'
  } else {
    aviso.value = 'Você saiu do Mercado Pago sem concluir o pagamento. Escolha Pix, cartão ou boleto para tentar novamente.'
  }
}

async function finalizar() {
  if (!consulta.value || processando.value || pago.value) return
  processando.value = true
  erro.value = ''
  aviso.value = ''
  try {
    const resposta = await api.post('/api/v1/pagamento/preferencia', { id_consulta: consulta.value.id_consulta })
    gravarMarca(consulta.value.id_consulta)
    window.location.assign(resposta.init_point)
  } catch (error) {
    erro.value = error.message || 'Não foi possível iniciar o pagamento.'
    processando.value = false
  }
}

// Ao voltar com o botão "voltar" do navegador, a página é restaurada do cache
// (bfcache) sem montar de novo: sem isto ela ficaria travada em "Abrindo pagamento...".
function aoMostrarPagina(evento) {
  if (!evento.persisted) return
  processando.value = false
  if (consulta.value && lerMarca() === String(consulta.value.id_consulta)) verificarRetorno()
}

onMounted(() => {
  window.addEventListener('pageshow', aoMostrarPagina)
  carregar()
})
onBeforeUnmount(() => window.removeEventListener('pageshow', aoMostrarPagina))
</script>

<template>
  <div class="min-h-screen bg-[#f8f8ff] text-[#073b57]">
    <AppHeader :user="usuario && { name: usuario.nome, role: 'Paciente' }" />
    <BackLink label="Voltar" to="/paciente/agendamentos" />
    <main class="mx-auto max-w-[1120px] px-6 pb-12 pt-6">
      <h1 class="text-2xl font-bold sm:text-3xl">Pagamento</h1>
      <p class="mt-1 text-xs text-[#59636d]">Confirme os detalhes da sua consulta e escolha a melhor forma de pagamento.</p>
      <p v-if="aviso && !carregando" class="mt-5 rounded-lg p-3 text-sm" :class="pago ? 'bg-[#e3f7ef] text-[#08805f]' : 'bg-[#fff4de] text-[#a96a05]'" role="status">
        {{ aviso }}
        <RouterLink v-if="pago" to="/paciente/agendamentos" class="font-semibold underline">Ver meus agendamentos</RouterLink>
      </p>
      <p v-if="carregando" class="mt-5 rounded-xl bg-white p-6 text-sm text-[#59636d]">Carregando os dados da consulta...</p>
      <div v-else class="mt-5 grid items-start gap-4 lg:grid-cols-[minmax(0,1fr)_300px]">
        <MetodoPagamento v-model="metodo" />
        <ResumoConsulta :profissional="consulta?.profissional?.nome" :especialidade="consulta?.profissional?.especialidade" :data="data" :horario="horario" :valor="valor" :imagem="consulta?.profissional?.path_imagem" :disponivel="Boolean(consulta) && !pago" :processando="processando" @finalizar="finalizar" />
      </div>
      <p v-if="erro" class="mt-4 rounded-lg bg-[#eef2ff] p-3 text-sm text-[#59636d]" role="status">{{ erro }}</p>
    </main>
  </div>
</template>