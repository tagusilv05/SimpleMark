<script setup>
import { ref, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import api from '@/services/api'
import { useAtendimentoStore } from '@/stores/atendimento'
import AppHeader from '@/components/shared/AppHeader.vue'
import BackLink from '@/components/shared/BackLink.vue'
import AcoesEditarExcluir from '@/components/shared/AcoesEditarExcluir.vue'
import BotaoAssinarCertificado from '@/components/shared/BotaoAssinarCertificado.vue'

const atendimento = useAtendimentoStore()
const { medicamentos, recomendacoes, validadeReceita } = storeToRefs(atendimento)

const user = ref(null)
const busca = ref('')
const editandoId = ref(null)
const mensagem = ref(null)

// TODO: buscar sugestões no backend
const sugestoes = ['Sertralina 100mg', 'Venlafaxina 75mg', 'Clonazepam 20mg']

const validades = [
  { valor: 30, label: '30 dias' },
  { valor: 60, label: '60 dias' },
  { valor: 90, label: '90 dias' },
  { valor: 180, label: '180 dias / Contínuo' },
]

const paths = {
  busca: 'm21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z',
  mais: 'M12 9v6m3-3H9m12 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z',
  escudo:
    'M12 3 4.5 6v5.25c0 4.556 3.204 8.69 7.5 9.75 4.296-1.06 7.5-5.194 7.5-9.75V6L12 3Zm0 6v6m-3-3h6',
}

function adicionar(nome = '') {
  const medicamento = atendimento.adicionarMedicamento(nome)
  editandoId.value = medicamento.id
  busca.value = ''
}

function buscar() {
  if (busca.value.trim()) adicionar(busca.value.trim())
}

function alternarEdicao(id) {
  editandoId.value = editandoId.value === id ? null : id
}

function emitir() {
  if (!medicamentos.value.length) {
    mensagem.value = 'Adicione pelo menos um medicamento antes de emitir a receita.'
    return
  }
  // TODO: integrar com a assinatura digital / emissão no backend
  editandoId.value = null
  mensagem.value = null
}

function logout() {
  api.clearAccessToken()
  user.value = null
}

onMounted(async () => {
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
    <AppHeader :user="user" @logout="logout" />

    <main class="mx-auto flex w-full max-w-300 flex-1 flex-col gap-6 px-12 pb-12">
      <BackLink class="pl-0! text-[#0a9ba5]!" />

      <!-- Medicamentos -->
      <section class="mt-6 flex flex-col rounded-xl bg-white p-6 shadow-[0_2px_12px_rgba(11,47,91,0.06)]">
        <h2 class="mb-2 text-sm font-bold text-[#08283a]">Buscar Medicamento</h2>

        <form class="flex h-13 items-center gap-3 rounded-lg bg-[#eef1fe] pl-4 pr-2" @submit.prevent="buscar">
          <svg class="size-5 text-gray-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" :d="paths.busca" />
          </svg>
          <label for="busca-medicamento" class="sr-only">Nome do medicamento</label>
          <input
            id="busca-medicamento"
            v-model="busca"
            type="text"
            placeholder="Digite nome"
            class="flex-1 bg-transparent text-base text-gray-800 outline-none placeholder:text-gray-500"
          />
          <button
            type="submit"
            class="h-9 cursor-pointer rounded-md bg-[#08283a] px-3 text-sm text-white transition-colors hover:bg-[#0d3a52]"
          >
            Buscar
          </button>
        </form>

        <div class="mt-4 flex flex-wrap items-center gap-2">
          <span class="text-xs text-gray-800">Sugestões rápidas:</span>
          <button
            v-for="s in sugestoes"
            :key="s"
            type="button"
            class="cursor-pointer rounded bg-[#e3e9fb] px-2.5 py-1 text-xs text-gray-800 transition-colors hover:bg-[#d3ddf8]"
            @click="adicionar(s)"
          >
            {{ s }}
          </button>
        </div>

        <h2 class="mb-4 mt-8 text-sm font-bold text-[#08283a]">
          Medicamentos Configurados na Receita ({{ medicamentos.length }})
        </h2>

        <ul class="flex flex-col gap-4">
          <li
            v-for="(m, i) in medicamentos"
            :key="m.id"
            class="flex gap-4 rounded-xl bg-[#eef1fe] px-4 pb-8 pt-4"
          >
            <span class="flex size-7 shrink-0 items-center justify-center rounded-md bg-[#dfe5f1] text-xs font-semibold text-[#08283a]">
              {{ i + 1 }}
            </span>

            <div class="flex min-w-0 flex-1 flex-col gap-4">
              <!-- Edição -->
              <template v-if="editandoId === m.id">
                <input
                  v-model="m.nome"
                  type="text"
                  placeholder="Medicamento (ex.: Sertralina 100mg - Comprimido)"
                  aria-label="Medicamento"
                  class="h-9 rounded-md border border-gray-200 bg-white px-3 text-sm font-bold text-[#08283a] outline-none focus:ring-2 focus:ring-[#0a9ba5]"
                />
                <div class="flex flex-col gap-3 md:flex-row">
                  <input
                    v-model="m.posologia"
                    type="text"
                    placeholder="Posologia"
                    aria-label="Posologia"
                    class="h-9 flex-1 rounded-md border border-gray-200 bg-white px-3 text-sm outline-none focus:ring-2 focus:ring-[#0a9ba5]"
                  />
                  <input
                    v-model="m.quantidade"
                    type="text"
                    placeholder="Quantidade prescrita"
                    aria-label="Quantidade prescrita"
                    class="h-9 rounded-md border border-gray-200 bg-white px-3 text-sm outline-none focus:ring-2 focus:ring-[#0a9ba5] md:w-64"
                  />
                </div>
              </template>

              <!-- Visualização -->
              <template v-else>
                <p class="pt-1 text-sm font-bold text-[#08283a]">{{ m.nome || 'Medicamento sem nome' }}</p>
                <div class="flex flex-wrap justify-between gap-2 text-sm text-gray-900">
                  <p><span class="text-gray-700">Posologia:</span> {{ m.posologia || '—' }}</p>
                  <p><span class="text-gray-700">Quantidade prescrita:</span> {{ m.quantidade || '—' }}</p>
                </div>
              </template>
            </div>

            <AcoesEditarExcluir
              class="self-start"
              :editando="editandoId === m.id"
              @editar="alternarEdicao(m.id)"
              @excluir="atendimento.removerMedicamento(m.id)"
            />
          </li>
        </ul>

        <button
          type="button"
          class="mt-4 flex h-11 cursor-pointer items-center justify-center gap-2 rounded-lg bg-[#dde7fb] text-sm font-semibold text-[#08283a] transition-colors hover:bg-[#cfdcf8]"
          @click="adicionar()"
        >
          <svg class="size-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" :d="paths.mais" />
          </svg>
          Adicionar Outro Medicamento
        </button>
      </section>

      <!-- Recomendações e validade -->
      <section class="flex flex-col rounded-xl bg-white p-6 shadow-[0_2px_12px_rgba(11,47,91,0.06)]">
        <label for="recomendacoes" class="mb-2 flex items-center gap-2 text-sm font-semibold text-[#08283a]">
          <svg class="size-4 text-[#0b6e66]" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" :d="paths.escudo" />
          </svg>
          Recomendações e Orientações Não Farmacológicas
        </label>
        <textarea
          id="recomendacoes"
          v-model="recomendacoes"
          rows="1"
          placeholder="Ex.: Praticar atividade física diariamente."
          class="field-sizing-content min-h-13 resize-none rounded-lg bg-[#eef1fe] px-4 py-3.5 text-base text-gray-900 outline-none focus:ring-2 focus:ring-[#0a9ba5]"
        />

        <h2 class="mb-4 mt-8 text-sm font-semibold text-[#08283a]">Validade da Receita</h2>
        <div class="grid grid-cols-2 gap-2 self-center md:grid-cols-4" role="radiogroup" aria-label="Validade da Receita">
          <button
            v-for="v in validades"
            :key="v.valor"
            type="button"
            role="radio"
            :aria-checked="validadeReceita === v.valor"
            class="h-11 w-38 cursor-pointer rounded-md text-sm transition-colors"
            :class="
              validadeReceita === v.valor
                ? 'bg-[#0b6e66] text-white'
                : 'bg-[#e3e9fb] text-gray-800 hover:bg-[#d3ddf8]'
            "
            @click="validadeReceita = v.valor"
          >
            {{ v.label }}
          </button>
        </div>
      </section>

      <p v-if="mensagem" class="text-center text-sm text-red-700">{{ mensagem }}</p>

      <div class="flex justify-center">
        <BotaoAssinarCertificado documento="Receita" @click="emitir" />
      </div>
    </main>
  </div>
</template>
