<script setup>
import { computed, onMounted, ref } from 'vue'
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
  } catch (error) {
    erro.value = error.message || 'Dados da consulta: sem informação.'
  } finally {
    carregando.value = false
  }
}

async function finalizar() {
  if (!consulta.value || processando.value) return
  processando.value = true
  erro.value = ''
  try {
    const resposta = await api.post('/api/v1/pagamento/preferencia', { id_consulta: consulta.value.id_consulta })
    window.location.assign(resposta.init_point)
  } catch (error) {
    erro.value = error.message || 'Não foi possível iniciar o pagamento.'
  } finally {
    processando.value = false
  }
}

onMounted(carregar)
</script>

<template>
  <div class="min-h-screen bg-[#f8f8ff] text-[#073b57]">
    <AppHeader :user="usuario && { name: usuario.nome, role: 'Paciente' }" />
    <BackLink label="Voltar" to="/paciente/agendamentos" />
    <main class="mx-auto max-w-[1120px] px-6 pb-12 pt-6">
      <h1 class="text-2xl font-bold sm:text-3xl">Pagamento</h1>
      <p class="mt-1 text-xs text-[#59636d]">Confirme os detalhes da sua consulta e escolha a melhor forma de pagamento.</p>
      <p v-if="carregando" class="mt-5 rounded-xl bg-white p-6 text-sm text-[#59636d]">Carregando os dados da consulta...</p>
      <div v-else class="mt-5 grid items-start gap-4 lg:grid-cols-[minmax(0,1fr)_300px]">
        <MetodoPagamento v-model="metodo" />
        <ResumoConsulta :profissional="consulta?.profissional?.nome" :especialidade="consulta?.profissional?.especialidade" :data="data" :horario="horario" :valor="valor" :imagem="consulta?.profissional?.path_imagem" :disponivel="Boolean(consulta)" :processando="processando" @finalizar="finalizar" />
      </div>
      <p v-if="erro" class="mt-4 rounded-lg bg-[#eef2ff] p-3 text-sm text-[#59636d]" role="status">{{ erro }}</p>
    </main>
  </div>
</template>