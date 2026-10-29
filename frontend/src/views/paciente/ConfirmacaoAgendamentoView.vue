<script setup>
/**
 * ConfirmacaoAgendamentoView — "Agendamento Confirmado!"
 *
 * Rota /agendamento/confirmacao/:idConsulta. Usa a consulta recém-criada da store
 * de agendamento; se a página for recarregada, busca em GET /consultas/minhas/{id}.
 * Leva ao pagamento da consulta.
 */
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppHeader from '@/components/shared/AppHeader.vue'
import BackLink from '@/components/shared/BackLink.vue'
import { api } from '@/services/api'
import { useAgendamentoStore } from '@/stores/agendamento'
import { MESES, fromISO } from '@/utils/datas'

const route = useRoute()
const router = useRouter()
const agendamento = useAgendamentoStore()

const user = ref(null)
const erro = ref('')

const consulta = computed(() =>
  String(agendamento.consulta?.id_consulta) === String(route.params.idConsulta) ? agendamento.consulta : null,
)
const medico = computed(() => consulta.value?.profissional ?? {})

const dataExtenso = computed(() => {
  if (!consulta.value) return ''
  const d = fromISO(consulta.value.data)
  return `${String(d.getDate()).padStart(2, '0')} de ${MESES[d.getMonth()]} de ${d.getFullYear()}`
})

// A consulta só guarda o início; o fim vem do horário escolhido na tela anterior, quando disponível
const horario = computed(() => {
  if (!consulta.value) return ''
  const inicio = consulta.value.hora.slice(0, 5)
  const fim = agendamento.horario?.inicio === inicio ? agendamento.horario.fim : ''
  return fim ? `${inicio} / ${fim}` : inicio
})

const valor = computed(() =>
  consulta.value
    ? new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(Number(consulta.value.valor))
    : '',
)

const iniciais = computed(() =>
  (medico.value.nome ?? '')
    .replace(/^dra?\.?\s+/i, '')
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((p) => p[0].toUpperCase())
    .join(''),
)

function irParaPagamento() {
  router.push({ name: 'pagamento-consulta', params: { idConsulta: route.params.idConsulta } })
}

// Comprovante: a área de impressão do navegador permite salvar como PDF
function baixarPdf() {
  window.print()
}

onMounted(async () => {
  api.get('/api/v1/auth/eu').then(
    (conta) => (user.value = { name: conta.nome, role: 'Paciente' }),
    () => (user.value = null),
  )
  if (consulta.value) return
  try {
    await agendamento.carregar(route.params.idConsulta)
  } catch (e) {
    erro.value = e.message || 'Não foi possível carregar o agendamento.'
  }
})
</script>

<template>
  <div class="flex min-h-screen flex-col bg-[#f8faff]">
    <div class="print:hidden">
      <AppHeader :user="user" />
      <BackLink :to="{ name: 'meusAgendamentos' }" />
    </div>

    <p v-if="erro" class="mx-auto mt-10 max-w-[680px] rounded-lg bg-[#eef2ff] p-4 text-center text-sm text-[#0b2f5b]" role="alert">
      {{ erro }}
      <RouterLink :to="{ name: 'agendamento' }" class="font-semibold underline">Fazer um agendamento</RouterLink>
    </p>

    <main v-else-if="consulta" class="mx-auto flex w-full max-w-[680px] flex-1 flex-col items-center px-6 pb-12 pt-6 text-center">
      <div class="flex size-24 items-center justify-center rounded-full bg-[#0b2f5b] shadow-lg">
        <svg class="size-12 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.2" stroke="currentColor" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
        </svg>
      </div>

      <h1 class="mt-8 text-4xl font-bold text-[#0b2f5b]">Agendamento Confirmado!</h1>
      <p class="mt-3 max-w-[440px] text-lg text-gray-600">
        Seu agendamento foi realizado com sucesso. Um comprovante foi enviado para o seu e-mail.
      </p>

      <article class="mt-8 w-full overflow-hidden rounded-xl border border-gray-200 bg-white text-left shadow-sm">
        <div class="p-8">
          <div class="flex items-center gap-4 border-b border-[#cfe9ee] pb-6">
            <img v-if="medico.path_imagem" :src="medico.path_imagem" :alt="`Foto de ${medico.nome}`" class="size-16 rounded-lg object-cover" />
            <div v-else class="flex size-16 items-center justify-center rounded-lg bg-[#0b2f5b] text-lg font-bold text-white">{{ iniciais }}</div>
            <div>
              <p class="text-2xl text-[#0b2f5b]">{{ medico.nome }}</p>
              <p class="text-sm font-semibold uppercase tracking-wider text-[#00a0b0]">{{ medico.especialidade }}</p>
            </div>
          </div>

          <dl class="mt-6 grid gap-6 sm:grid-cols-2">
            <div class="flex items-center gap-3">
              <svg class="size-6 shrink-0 text-[#0b2f5b]" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 0 1 2.25-2.25h13.5A2.25 2.25 0 0 1 21 7.5v11.25m-18 0A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75m-18 0v-7.5A2.25 2.25 0 0 1 5.25 9h13.5A2.25 2.25 0 0 1 21 11.25v7.5" />
              </svg>
              <div>
                <dt class="text-xs text-gray-500">Data</dt>
                <dd class="text-lg font-semibold text-[#0b2f5b]">{{ dataExtenso }}</dd>
              </div>
            </div>

            <div class="flex items-center gap-3">
              <svg class="size-6 shrink-0 text-[#0b2f5b]" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
              </svg>
              <div>
                <dt class="text-xs text-gray-500">Horário</dt>
                <dd class="text-lg font-semibold text-[#0b2f5b]">{{ horario }}</dd>
              </div>
            </div>

            <div class="flex items-center gap-3">
              <svg class="size-6 shrink-0 text-[#00a0b0]" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" aria-hidden="true">
                <path stroke-linecap="round" d="m15.75 10.5 4.72-4.72a.75.75 0 0 1 1.28.53v11.38a.75.75 0 0 1-1.28.53l-4.72-4.72M4.5 18.75h9a2.25 2.25 0 0 0 2.25-2.25v-9a2.25 2.25 0 0 0-2.25-2.25h-9A2.25 2.25 0 0 0 2.25 7.5v9a2.25 2.25 0 0 0 2.25 2.25Z" />
              </svg>
              <div>
                <dt class="text-xs text-gray-500">Local</dt>
                <dd class="text-lg font-semibold text-[#0b2f5b]">Teleconsulta</dd>
                <dd class="mt-1 inline-block rounded bg-[#ddf5f7] px-1 text-xs text-[#00a0b0]">Link disponível em 15 min</dd>
              </div>
            </div>

            <div class="flex items-center gap-3">
              <svg class="size-6 shrink-0 text-[#0b2f5b]" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 18.75a60.07 60.07 0 0 1 15.797 2.101c.727.198 1.453-.342 1.453-1.096V18.75M3.75 4.5v.75A.75.75 0 0 1 3 6h-.75m0 0v-.375c0-.621.504-1.125 1.125-1.125H20.25M2.25 6v9m18-10.5v.75c0 .414.336.75.75.75h.75m-1.5-1.5h.375c.621 0 1.125.504 1.125 1.125v9.75c0 .621-.504 1.125-1.125 1.125h-.375m1.5-1.5H21a.75.75 0 0 0-.75.75v.75m0 0H3.75m0 0h-.375a1.125 1.125 0 0 1-1.125-1.125V15m1.5 1.5v-.75A.75.75 0 0 0 3 15h-.75M15 10.5a3 3 0 1 1-6 0 3 3 0 0 1 6 0Zm3 0h.008v.008H18V10.5Zm-12 0h.008v.008H6V10.5Z" />
              </svg>
              <div>
                <dt class="text-xs text-gray-500">Valor</dt>
                <dd class="text-lg font-semibold text-[#0b2f5b]">{{ valor }}</dd>
              </div>
            </div>
          </dl>
        </div>

        <div class="flex items-center justify-between bg-[#eef2fb] px-4 py-3 text-xs">
          <span class="text-gray-500">ID: {{ consulta.id_consulta }}</span>
          <button type="button" class="cursor-pointer text-sm font-semibold text-[#0b2f5b] hover:underline print:hidden" @click="baixarPdf">⤓ Baixar PDF</button>
        </div>
      </article>

      <button
        type="button"
        class="mt-8 flex h-14 w-full cursor-pointer items-center justify-center gap-2 rounded-lg bg-[#00a0b0] print:hidden font-semibold text-white transition-colors hover:bg-[#008a98]"
        @click="irParaPagamento"
      >
        Ir para Pagamento <span aria-hidden="true">→</span>
      </button>

      <div class="mt-4 grid w-full gap-4 sm:grid-cols-2 print:hidden">
        <RouterLink
          :to="{ name: 'meusAgendamentos' }"
          class="flex h-14 items-center justify-center rounded-lg bg-[#0b2f5b] font-semibold text-white transition-colors hover:bg-[#0b417d]"
        >
          Ver Meus Agendamentos
        </RouterLink>
        <RouterLink
          :to="{ name: 'home' }"
          class="flex h-14 items-center justify-center rounded-lg border-2 border-[#0b2f5b] font-semibold text-[#0b2f5b] transition-colors hover:bg-[#eef2fb]"
        >
          Voltar para Home
        </RouterLink>
      </div>

      <p class="mt-8 text-sm text-gray-500 print:hidden">
        Alguma dúvida? <RouterLink to="/ouvidoria" class="text-[#0b2f5b] hover:underline">Entre em contato</RouterLink> com o suporte.
      </p>
    </main>
  </div>
</template>
