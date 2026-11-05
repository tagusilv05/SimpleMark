<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import api from '@/services/api'
import { useAtendimentoStore } from '@/stores/atendimento'
import AppHeader from '@/components/shared/AppHeader.vue'
import BackLink from '@/components/shared/BackLink.vue'
import AcoesEditarExcluir from '@/components/shared/AcoesEditarExcluir.vue'
import BotaoAssinarCertificado from '@/components/shared/BotaoAssinarCertificado.vue'
import DocumentoEmitido from '@/components/shared/DocumentoEmitido.vue'

const route = useRoute()
const atendimento = useAtendimentoStore()
const { idConsulta, atestado, atestadoEmitido } = storeToRefs(atendimento)

const user = ref(null)
const editando = ref(false)
const textoEl = ref(null)
const mensagem = ref(null)
const emitindo = ref(false)

async function alternarEdicao() {
  editando.value = !editando.value
  if (editando.value) {
    await nextTick()
    textoEl.value?.focus()
  }
}

function excluir() {
  atestado.value = ''
  editando.value = true
}

async function emitir() {
  if (emitindo.value) return
  if (!idConsulta.value) {
    mensagem.value = 'Abra o atestado a partir do atendimento de uma consulta.'
    return
  }
  if (!atestado.value.trim()) {
    mensagem.value = 'Escreva o texto do atestado antes de emitir.'
    return
  }
  editando.value = false
  mensagem.value = null
  emitindo.value = true
  try {
    await atendimento.emitirAtestado()
  } catch (e) {
    mensagem.value = e.message || 'Não foi possível emitir o atestado.'
  } finally {
    emitindo.value = false
  }
}

onMounted(async () => {
  if (route.query.consulta) {
    atendimento.carregarConsulta(route.query.consulta).catch((e) => {
      mensagem.value = e.message || 'Não foi possível carregar a consulta.'
    })
  }
  try {
    const { data } = await api.get('/api/v1/auth/eu')
    user.value = { name: data.nome, role: 'Profissional' }
  } catch (e) {
    console.error(e)
  }
})
</script>

<template>
  <div class="flex min-h-screen flex-col bg-[#f8faff]">
    <AppHeader />

    <main class="mx-auto flex w-full max-w-300 flex-1 flex-col gap-6 px-12 pb-12">
      <BackLink class="pl-0! text-[#0a9ba5]!" />

      <section class="mt-6 rounded-xl bg-white px-6 pb-6 pt-10 shadow-[0_2px_12px_rgba(11,47,91,0.06)]">
        <div class="mb-9 flex flex-col items-center gap-3">
          <h1 class="text-xl font-semibold tracking-wide text-[#08283a]">ATESTADO MÉDICO</h1>
          <span class="h-0.5 w-12 rounded-full bg-[#0b6e66]" aria-hidden="true" />
        </div>

        <div class="mx-auto flex min-h-64 max-w-240 gap-6 rounded-xl bg-[#eef2fd] px-4 py-4">
          <textarea
            v-if="editando"
            ref="textoEl"
            v-model="atestado"
            aria-label="Texto do atestado"
            class="min-h-56 flex-1 resize-none bg-transparent text-sm leading-relaxed text-gray-900 outline-none"
          />
          <p v-else class="flex-1 whitespace-pre-line text-sm leading-relaxed text-gray-900">
            {{ atestado }}
          </p>

          <AcoesEditarExcluir class="self-start" :editando="editando" @editar="alternarEdicao" @excluir="excluir" />
        </div>
      </section>

      <p v-if="mensagem" class="text-center text-sm text-red-700">{{ mensagem }}</p>

      <DocumentoEmitido v-if="atestadoEmitido" :documento="atestadoEmitido" titulo="Atestado emitido e assinado" />

      <div class="mt-6 flex justify-center">
        <BotaoAssinarCertificado documento="Atestado" :disabled="emitindo" @click="emitir" />
      </div>
    </main>
  </div>
</template>
