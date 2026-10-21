<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import adminApi from '@/services/adminApi'
import AdminHeader from '@/components/administracao/AdminHeader.vue'
import UserAvatar from '@/components/shared/UserAvatar.vue'

const router = useRouter()
const pending = ref([])
const selected = ref(null)
const search = ref('')
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const actionError = ref('')

const filtered = computed(() => {
  const term = search.value.trim().toLowerCase()
  if (term.length > 0 && term.length < 5) return []
  return pending.value.filter(
    (item) =>
      !term ||
      [item.nome, item.email, item.cpf, item.numero_conselho ?? ''].some((value) =>
        value.toLowerCase().includes(term),
      ),
  )
})
const approvedToday = ref(0)
const rejectedToday = ref(0)

async function loadPending() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await adminApi.get('/api/v1/administracao/profissionais/pendentes')
    pending.value = data
    if (selected.value)
      selected.value =
        pending.value.find((item) => item.id_profissional === selected.value.id_profissional) ??
        null
  } catch (err) {
    error.value = err.message || 'Não foi possível carregar os cadastros pendentes.'
  } finally {
    loading.value = false
  }
}

async function approve() {
  if (!selected.value) return
  saving.value = true
  actionError.value = ''
  try {
    await adminApi.post(`/api/v1/administracao/profissionais/${selected.value.id_profissional}/validar`)
    approvedToday.value += 1
    selected.value = null
    await loadPending()
  } catch (err) {
    actionError.value = err.message || 'Não foi possível aprovar o profissional.'
  } finally {
    saving.value = false
  }
}

async function reject() {
  if (!selected.value) return
  saving.value = true
  actionError.value = ''
  try {
    await adminApi.post(`/api/v1/administracao/profissionais/${selected.value.id_profissional}/banir`, {
      motivo: 'Cadastro rejeitado na validação manual.',
    })
    rejectedToday.value += 1
    selected.value = null
    await loadPending()
  } catch (err) {
    actionError.value = err.message || 'Não foi possível rejeitar o cadastro.'
  } finally {
    saving.value = false
  }
}

function logout() {
  adminApi.clearAccessToken()
  router.push('/administracao/validacao-profissionais')
}
onMounted(loadPending)
</script>

<template>
  <div class="min-h-screen bg-[#f4f7fb] text-[#073b57]">
    <AdminHeader @logout="logout" />
    <main class="mx-auto max-w-[1440px] px-4 py-6 lg:px-6">
      <div class="mb-5 flex flex-col justify-between gap-3 md:flex-row md:items-end">
        <div>
          <p class="flex items-center gap-1 text-[10px] text-[#8496a8]">
            <RouterLink to="/administracao" class="hover:text-[#073b57]"
              >Área do Administrador</RouterLink
            ><span>›</span
            ><RouterLink
              to="/administracao/validacao-profissionais"
              class="font-semibold text-[#073b57]"
              >Validação Profissional</RouterLink
            >
          </p>
          <h1 class="mt-1 text-xl font-bold">Validação e Homologação de Profissionais</h1>
          <p class="text-xs text-[#8496a8]">
            Analise os dados enviados e decida manualmente sobre a liberação da conta.
          </p>
        </div>
        <label class="relative"
          ><span class="sr-only">Filtrar profissionais</span
          ><svg
            class="absolute left-3 top-2.5 size-3.5 text-[#8ba0b4]"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            aria-hidden="true"
          >
            <circle cx="10.8" cy="10.8" r="6.8" />
            <path stroke-linecap="round" d="m16 16 5 5" /></svg
          ><input
            v-model="search"
            class="h-9 rounded-lg border border-[#dce5ed] bg-white pl-8 pr-3 text-xs outline-none focus:border-[#08718d]"
            placeholder="Filtrar por nome, CPF ou conselho"
        /></label>
      </div>

      <section class="mb-5 grid gap-3 sm:grid-cols-3">
        <div class="rounded-xl border border-[#dde6ef] bg-white p-4">
          <div class="flex items-start justify-between">
            <p class="text-[10px] uppercase text-[#8194a5]">Aguardando análise</p>
            <div class="flex size-9 items-center justify-center rounded-lg bg-[#fff4de]">
              <svg
                class="size-5 text-[#d88808]"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="1.7"
                aria-hidden="true"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M7 5.5h10A1.5 1.5 0 0 1 18.5 7v12A1.5 1.5 0 0 1 17 20.5H7A1.5 1.5 0 0 1 5.5 19V7A1.5 1.5 0 0 1 7 5.5Z"
                />
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M9 5.5V4.75A1.25 1.25 0 0 1 10.25 3.5h3.5A1.25 1.25 0 0 1 15 4.75v.75M9 10h6m-6 3h4"
                />
                <circle
                  cx="16.5"
                  cy="17"
                  r="3.25"
                  fill="currentColor"
                  stroke="white"
                  stroke-width="1.2"
                />
                <path stroke="white" stroke-linecap="round" d="M16.5 15.5v1.7l1 0.6" />
              </svg>
            </div>
          </div>
          <p class="mt-1 text-xl font-bold">{{ pending.length }}</p>
          <p class="mt-1 flex items-center gap-1 text-[10px] text-[#ce7912]">
            <svg
              class="size-3"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              aria-hidden="true"
            >
              <path d="M5 22h14" />
              <path d="M5 2h14" />
              <path d="M17 22v-4.172a2 2 0 0 0-.586-1.414L12 12l-4.414 4.414A2 2 0 0 0 7 17.828V22" />
              <path d="M7 2v4.172a2 2 0 0 0 .586 1.414L12 12l4.414-4.414A2 2 0 0 0 17 6.172V2" />
            </svg>
            Revisão manual
          </p>
        </div>

        <div class="rounded-xl border border-[#dde6ef] bg-white p-4">
          <div class="flex items-start justify-between">
            <p class="text-[10px] uppercase text-[#8194a5]">Aprovados hoje</p>
            <div class="flex size-9 items-center justify-center rounded-lg bg-[#e3f7f0]">
              <svg
                class="size-5 text-[#079878]"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="1.7"
                aria-hidden="true"
              >
                <circle cx="12" cy="12" r="9.25" />
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="m8.25 12 2.45 2.45 5.05-5.05"
                />
              </svg>
            </div>
          </div>
          <p class="mt-1 text-xl font-bold text-[#079878]">{{ approvedToday }}</p>
          <p class="mt-1 flex items-center gap-1 text-[10px] text-[#079878]">
            <svg
              class="size-3"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              aria-hidden="true"
            >
              <circle cx="12" cy="12" r="10" />
              <path d="m9 12 2 2 4-4" />
            </svg>
            Nesta sessão
          </p>
        </div>

        <div class="rounded-xl border border-[#dde6ef] bg-white p-4">
          <div class="flex items-start justify-between">
            <p class="text-[10px] uppercase text-[#8194a5]">Rejeitados</p>
            <div class="flex size-9 items-center justify-center rounded-lg bg-[#fdeaee]">
              <svg
                class="size-5 text-[#df3152]"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="1.7"
                stroke-linecap="round"
                stroke-linejoin="round"
                aria-hidden="true"
              >
                <path d="m14 13-8.381 8.38a1 1 0 0 1-3.001-3l8.384-8.381" />
                <path d="m16 16 6-6" />
                <path d="m21.5 10.5-8-8" />
                <path d="m8 8 6-6" />
                <path d="m8.5 7.5 8 8" />
              </svg>
            </div>
          </div>
          <p class="mt-1 text-xl font-bold text-[#df3152]">{{ rejectedToday }}</p>
          <p class="mt-1 flex items-center gap-1 text-[10px] text-[#df3152]">
            <svg
              class="size-3"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              aria-hidden="true"
            >
              <circle cx="12" cy="12" r="10" />
              <path d="m4.9 4.9 14.2 14.2" />
            </svg>
            Nesta sessão
          </p>
        </div>
      </section>
      <p v-if="error" class="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">{{ error }}</p>
      <div class="grid items-start gap-4 lg:grid-cols-[minmax(0,1.4fr)_minmax(340px,1fr)]">
        <section>
          <div class="mb-2 flex justify-between">
            <h2 class="flex items-center gap-1.5 text-xs font-bold">
              <svg
                class="size-3.5 text-[#079878]"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="1.8"
                aria-hidden="true"
              >
                <path stroke-linecap="round" stroke-linejoin="round" d="M5 6h14M5 12h14M5 18h14" />
                <circle cx="3" cy="6" r=".7" fill="currentColor" />
                <circle cx="3" cy="12" r=".7" fill="currentColor" />
                <circle cx="3" cy="18" r=".7" fill="currentColor" /></svg
              >Cadastros Pendentes de Validação ({{ pending.length }})
            </h2>
            <span class="text-[10px] text-[#8194a5]">Ordenado por mais recentes</span>
          </div>
          <div v-if="loading" class="rounded-xl bg-white p-8 text-center text-sm text-[#8095a8]">
            Carregando cadastros...
          </div>
          <div
            v-else-if="!filtered.length"
            class="rounded-xl bg-white p-8 text-center text-sm text-[#8095a8]"
          >
            {{
              search.length > 0 && search.length < 5
                ? 'Digite pelo menos 5 caracteres para buscar.'
                : 'Nenhum cadastro pendente.'
            }}
          </div>
          <div v-else class="space-y-2">
            <button
              v-for="item in filtered"
              :key="item.id_profissional"
              class="w-full rounded-xl border bg-white p-4 text-left shadow-sm transition hover:border-[#006087]"
              :class="
                selected?.id_profissional === item.id_profissional
                  ? 'border-[#006087] ring-1 ring-[#006087]'
                  : 'border-[#dde6ef]'
              "
              @click="selected = item"
            >
              <div class="flex items-start gap-3">
                <UserAvatar
                  :name="item.nome"
                  class="size-8 bg-[#eef3f8] text-[10px] font-bold text-[#38566b]"
                />
                <div class="min-w-0 flex-1">
                  <div class="flex flex-wrap items-center gap-2">
                    <span class="text-xs font-bold">{{ item.nome }}</span
                    ><span
                      class="rounded bg-[#edf4ff] px-2 py-1 text-[9px] font-semibold text-[#2361a0]"
                      >{{ item.orgao_conselho || 'Conselho não informado' }}
                      {{ item.numero_conselho || '' }}</span
                    >
                  </div>
                  <p class="mt-1 text-[10px] text-[#8397a8]">
                    {{ item.especialidades.join(' · ') || 'Especialidade não informada' }} ·
                    {{ item.email }}
                  </p>
                  <div class="mt-2 flex gap-2 text-[9px]">
                    <span class="rounded bg-[#e8faf3] px-2 py-1 text-[#078c69]"
                      >◉ Cadastro pendente</span
                    ><span class="text-[#91a1ae]">CPF: {{ item.cpf }}</span>
                  </div>
                </div>
                <span class="text-[9px] text-[#8ba0b1]">Pendente</span>
              </div>
            </button>
          </div>
        </section>
        <section
          v-if="selected"
          class="overflow-hidden rounded-xl border border-[#dce6ed] bg-white shadow-sm"
        >
          <div class="bg-[#003449] p-5 text-white">
            <p class="text-[9px] uppercase text-[#8dd6d7]">Dossiê de validação</p>
            <h2 class="mt-1 text-sm font-bold">{{ selected.nome }}</h2>
          </div>
          <div class="space-y-5 p-5 text-xs">
            <div>
              <p class="mb-2 font-bold">1. Identificação cadastral</p>
              <dl class="space-y-2 rounded-lg bg-[#f7f9fb] p-3">
                <div class="flex justify-between gap-3">
                  <dt class="text-[#879aaa]">E-mail</dt>
                  <dd class="font-semibold">{{ selected.email }}</dd>
                </div>
                <div class="flex justify-between gap-3">
                  <dt class="text-[#879aaa]">CPF</dt>
                  <dd class="font-semibold">{{ selected.cpf }}</dd>
                </div>
              </dl>
            </div>
            <div>
              <p class="mb-2 font-bold">2. Credenciais médicas</p>
              <dl class="space-y-2 rounded-lg bg-[#f7f9fb] p-3">
                <div class="flex justify-between gap-3">
                  <dt class="text-[#879aaa]">Conselho</dt>
                  <dd class="font-semibold">{{ selected.orgao_conselho || 'Não informado' }}</dd>
                </div>
                <div class="flex justify-between gap-3">
                  <dt class="text-[#879aaa]">Número</dt>
                  <dd class="font-semibold">{{ selected.numero_conselho || 'Não informado' }}</dd>
                </div>
                <div class="flex justify-between gap-3">
                  <dt class="text-[#879aaa]">Especialidades</dt>
                  <dd class="text-right font-semibold">
                    {{ selected.especialidades.join(', ') || 'Não informadas' }}
                  </dd>
                </div>
              </dl>
            </div>
            <p
              class="rounded-lg border border-[#f4dfb5] bg-[#fff9ec] p-3 text-[10px] text-[#97701c]"
            >
              Os documentos não são validados automaticamente. A conferência deve ser feita
              manualmente pelo administrador.
            </p>
            <p v-if="actionError" class="text-xs text-red-700">{{ actionError }}</p>
            <div class="flex gap-2">
              <button
                class="flex-1 rounded-lg bg-[#079c72] py-3 text-xs font-bold text-white disabled:opacity-50"
                :disabled="saving"
                @click="approve"
              >
                ◉ Aprovar</button
              ><button
                class="rounded-lg border border-red-200 bg-red-50 px-5 py-3 text-xs font-bold text-red-600 disabled:opacity-50"
                :disabled="saving"
                @click="reject"
              >
                × Rejeitar
              </button>
            </div>
          </div>
        </section>
        <section
          v-else
          class="rounded-xl border border-dashed border-[#cddbe5] bg-white p-8 text-center text-sm text-[#8194a5]"
        >
          Selecione um cadastro para visualizar os dados disponíveis.
        </section>
      </div>
    </main>
  </div>
</template>