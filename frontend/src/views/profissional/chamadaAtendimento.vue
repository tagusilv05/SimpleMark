<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import api from '@/services/api'
import { useAtendimentoStore } from '@/stores/atendimento'
import AppHeader from '@/components/shared/AppHeader.vue'
import BackLink from '@/components/shared/BackLink.vue'
import UserAvatar from '@/components/shared/UserAvatar.vue'

const route = useRoute()
const router = useRouter()
const atendimento = useAtendimentoStore()
const { paciente, inicio, retorno, retornoData } = storeToRefs(atendimento)

const user = ref(null)

// ---------- Cronômetro ----------
const agora = ref(Date.now())
let relogio = null

const duracao = computed(() => {
  const total = Math.max(0, Math.floor((agora.value - inicio.value.getTime()) / 1000))
  const h = Math.floor(total / 3600)
  const m = String(Math.floor((total % 3600) / 60)).padStart(2, '0')
  const s = String(total % 60).padStart(2, '0')
  return h ? `${h}:${m}:${s}` : `${m}:${s}`
})

// ---------- Vídeo ----------
// Com ?consulta=<id> na URL, a sala do Jitsi da consulta é embutida na tela.
// Sem link, mostra só a prévia da câmera do profissional.
const meetLink = ref(null)

async function carregarVideochamada() {
  const id = route.query.consulta
  if (!id) return false
  try {
    const { data } = await api.get(`/api/v1/consultas/${id}/videochamada`)
    meetLink.value = data.meet_link
  } catch (e) {
    console.error(e)
  }
  return Boolean(meetLink.value)
}

const videoLocal = ref(null)
const microfoneLigado = ref(true)
const cameraLigada = ref(true)
const semCamera = ref(false)
let stream = null

async function iniciarCamera() {
  try {
    stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true })
    if (videoLocal.value) videoLocal.value.srcObject = stream
  } catch (e) {
    semCamera.value = true
    console.error(e)
  }
}

function alternarMicrofone() {
  microfoneLigado.value = !microfoneLigado.value
  stream?.getAudioTracks().forEach((t) => (t.enabled = microfoneLigado.value))
}

function alternarCamera() {
  cameraLigada.value = !cameraLigada.value
  stream?.getVideoTracks().forEach((t) => (t.enabled = cameraLigada.value))
}

function pararCamera() {
  stream?.getTracks().forEach((t) => t.stop())
  stream = null
}

// ---------- Retorno e finalização ----------
const opcoesRetorno = [
  { valor: 'nao', label: 'Não' },
  { valor: 30, label: '30 dias' },
  { valor: 60, label: '60 dias' },
  { valor: 'personalizado', label: 'Personalizado' },
]

const precisaRetorno = computed(() => retorno.value !== 'nao')

function finalizar() {
  if (!confirm('Deseja finalizar o atendimento?')) return
  // TODO: enviar retorno, receita e atestado para o backend
  pararCamera()
  router.push({ name: 'dashboardDoProfissional' })
}

const paths = {
  receita:
    'M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 0 0 2.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 0 0-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 0 0 .75-.75 2.25 2.25 0 0 0-.1-.664m-5.8 0A2.251 2.251 0 0 1 13.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25ZM6.75 12h.008v.008H6.75V12Zm0 3h.008v.008H6.75V15Zm0 3h.008v.008H6.75V18Z',
  atestado:
    'M15 9h3.75M15 12h3.75M15 15h3.75M4.5 19.5h15a2.25 2.25 0 0 0 2.25-2.25V6.75A2.25 2.25 0 0 0 19.5 4.5h-15a2.25 2.25 0 0 0-2.25 2.25v10.5A2.25 2.25 0 0 0 4.5 19.5Zm6-10.125a1.875 1.875 0 1 1-3.75 0 1.875 1.875 0 0 1 3.75 0Zm1.294 6.336a6.721 6.721 0 0 1-3.17.789 6.721 6.721 0 0 1-3.168-.789 3.376 3.376 0 0 1 6.338 0Z',
  desligar:
    'M3.5 14.5c-.3-.9-.1-1.9.6-2.6C6.2 9.8 9 8.7 12 8.7s5.8 1.1 7.9 3.2c.7.7.9 1.7.6 2.6l-.4 1.1c-.2.6-.9 1-1.6.8l-2.7-.7c-.6-.2-1-.7-1-1.3v-1.5c-1.8-.5-3.8-.5-5.6 0v1.5c0 .6-.4 1.1-1 1.3l-2.7.7c-.7.2-1.4-.2-1.6-.8l-.4-1.1Z',
  microfone:
    'M12 18.75a6 6 0 0 0 6-6v-1.5m-6 7.5a6 6 0 0 1-6-6v-1.5m6 7.5v3.75m-3.75 0h7.5M12 15.75a3 3 0 0 1-3-3V4.5a3 3 0 1 1 6 0v8.25a3 3 0 0 1-3 3Z',
  camera:
    'm15.75 10.5 4.72-4.72a.75.75 0 0 1 1.28.53v11.38a.75.75 0 0 1-1.28.53l-4.72-4.72M4.5 18.75h9a2.25 2.25 0 0 0 2.25-2.25v-9a2.25 2.25 0 0 0-2.25-2.25h-9A2.25 2.25 0 0 0 2.25 7.5v9a2.25 2.25 0 0 0 2.25 2.25Z',
  cortar: 'M3 3l18 18',
}

function logout() {
  api.clearAccessToken()
  user.value = null
}

onMounted(async () => {
  relogio = setInterval(() => (agora.value = Date.now()), 1000)
  if (!(await carregarVideochamada())) iniciarCamera()

  try {
    const { data } = await api.get('/api/v1/auth/eu')
    user.value = { name: data.nome, role: 'Profissional' }
  } catch (e) {
    console.error(e)
  }
})

onBeforeUnmount(() => {
  clearInterval(relogio)
  pararCamera()
})
</script>

<template>
  <div class="flex min-h-screen flex-col bg-[#f8faff]">
    <AppHeader :user="user" @logout="logout" />

    <main class="mx-auto flex w-full max-w-300 flex-1 flex-col gap-6 px-12 pb-12">
      <BackLink class="pl-0! text-[#0a9ba5]!" />

      <!-- Status + paciente -->
      <div class="mt-4 flex flex-wrap items-center justify-center gap-5">
        <span class="inline-flex h-8 items-center gap-3 rounded-full bg-[#dceeed] px-4 text-sm font-bold text-[#0b6e66]">
          <span class="size-2.5 animate-pulse rounded-full bg-[#0b6e66]" aria-hidden="true" />
          EM ATENDIMENTO AO VIVO
          <span class="ml-2 tabular-nums text-[#08283a]">{{ duracao }}</span>
        </span>

        <div class="flex items-center gap-3">
          <UserAvatar :name="paciente.nome" class="size-10 bg-[#08283a]! text-sm font-semibold" />
          <span class="text-base font-medium text-[#08283a]">{{ paciente.nome }}</span>
          <span class="rounded-full bg-[#e3e9fb] px-2 py-1 text-[11px] text-gray-700">
            {{ paciente.idade }} anos • CPF {{ paciente.cpf }}
          </span>
        </div>
      </div>

      <!-- Vídeo -->
      <div class="relative mx-auto mt-6 aspect-4/3 w-full max-w-185 overflow-hidden rounded-xl bg-linear-to-br from-[#1d3a4d] to-[#08283a] shadow-[0_4px_16px_rgba(8,40,58,0.18)]">
        <iframe
          v-if="meetLink"
          :src="meetLink"
          title="Videochamada"
          allow="camera; microphone; fullscreen; display-capture; autoplay"
          class="absolute inset-0 size-full border-0"
        />

        <!-- Paciente (remoto) -->
        <div v-else class="absolute inset-0 flex flex-col items-center justify-center gap-4 text-white/80">
          <UserAvatar :name="paciente.nome" class="size-28 bg-white/10! text-4xl font-semibold" />
          <p class="text-sm">Aguardando vídeo de {{ paciente.nome }}...</p>
        </div>

        <!-- Profissional (local) -->
        <div v-if="!meetLink" class="absolute right-0 top-6 aspect-video w-[39%] overflow-hidden bg-[#2a3f4d]">
          <video
            v-show="!semCamera && cameraLigada"
            ref="videoLocal"
            autoplay
            muted
            playsinline
            class="size-full -scale-x-100 object-cover"
          />
          <div
            v-if="semCamera || !cameraLigada"
            class="flex size-full items-center justify-center"
          >
            <UserAvatar :name="user?.name || 'Você'" class="size-14 bg-white/10! text-lg font-semibold" />
          </div>

          <div class="absolute inset-x-0 bottom-0 flex h-6 items-center justify-center gap-1.5 bg-black/40">
            <button
              type="button"
              class="flex size-4 cursor-pointer items-center justify-center rounded-full bg-white text-gray-900"
              :aria-label="microfoneLigado ? 'Desligar microfone' : 'Ligar microfone'"
              @click="alternarMicrofone"
            >
              <svg class="size-2.5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" :d="paths.microfone" />
                <path v-if="!microfoneLigado" stroke-linecap="round" :d="paths.cortar" class="text-red-600" />
              </svg>
            </button>
            <button
              type="button"
              class="flex size-4 cursor-pointer items-center justify-center rounded-full bg-white text-gray-900"
              :aria-label="cameraLigada ? 'Desligar câmera' : 'Ligar câmera'"
              @click="alternarCamera"
            >
              <svg class="size-2.5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" :d="paths.camera" />
                <path v-if="!cameraLigada" stroke-linecap="round" :d="paths.cortar" class="text-red-600" />
              </svg>
            </button>
            <button
              type="button"
              class="flex size-4 cursor-pointer items-center justify-center rounded-full bg-red-600 text-white"
              aria-label="Encerrar chamada"
              @click="finalizar"
            >
              <svg class="size-3" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                <path :d="paths.desligar" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Ações do atendimento -->
      <section class="mx-auto mt-8 flex w-full max-w-109 flex-col gap-6 rounded-2xl bg-white p-5 shadow-[0_2px_12px_rgba(11,47,91,0.06)]">
        <div class="flex flex-col gap-4 rounded-xl bg-[#eef2fd] p-4">
          <label class="flex cursor-pointer items-center gap-3 text-sm font-bold text-[#08283a]">
            <input
              type="checkbox"
              :checked="precisaRetorno"
              class="size-4 cursor-pointer appearance-none rounded-[3px] border-2 border-[#0b6e66] checked:bg-[#0b6e66]"
              @change="retorno = $event.target.checked ? 30 : 'nao'"
            />
            Necessita de Retorno Clínico?
          </label>

          <div class="flex flex-wrap gap-2" role="radiogroup" aria-label="Retorno clínico">
            <button
              v-for="o in opcoesRetorno"
              :key="o.valor"
              type="button"
              role="radio"
              :aria-checked="retorno === o.valor"
              class="h-7 cursor-pointer rounded-md px-3 text-xs transition-colors"
              :class="
                retorno === o.valor
                  ? 'bg-[#08283a] font-semibold text-white'
                  : 'bg-white text-gray-700 hover:bg-[#e3e9fb]'
              "
              @click="retorno = o.valor"
            >
              {{ o.label }}
            </button>
          </div>

          <input
            v-if="retorno === 'personalizado'"
            v-model="retornoData"
            type="date"
            aria-label="Data do retorno"
            class="h-9 rounded-md border border-gray-200 bg-white px-3 text-sm text-gray-800 outline-none focus:ring-2 focus:ring-[#0a9ba5]"
          />
        </div>

        <nav class="flex items-center justify-center gap-4" aria-label="Documentos do atendimento">
          <RouterLink
            :to="{ name: 'receitaDoAtendimento' }"
            class="inline-flex h-10 w-40 items-center justify-center gap-2 rounded-md bg-[#08283a] text-sm font-semibold text-white transition-colors hover:bg-[#0d3a52]"
          >
            <svg class="size-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" :d="paths.receita" />
            </svg>
            Receita
          </RouterLink>
          <RouterLink
            :to="{ name: 'atestadoDoAtendimento' }"
            class="inline-flex h-10 items-center justify-center gap-2 rounded-md px-4 text-sm font-semibold text-gray-700 transition-colors hover:bg-[#eef2fd]"
          >
            <svg class="size-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" :d="paths.atestado" />
            </svg>
            Atestado Médico
          </RouterLink>
        </nav>

        <button
          type="button"
          class="flex h-11 cursor-pointer items-center justify-center gap-2 rounded-lg bg-[#b81c1c] text-sm font-semibold text-white transition-colors hover:bg-red-800"
          @click="finalizar"
        >
          <svg class="size-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
            <path :d="paths.desligar" />
          </svg>
          Finalizar Atendimento
        </button>
      </section>
    </main>
  </div>
</template>
