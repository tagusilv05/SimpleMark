<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import adminApi from '@/services/adminApi'
import AdminHeader from '@/components/administracao/AdminHeader.vue'
import UserAvatar from '@/components/shared/UserAvatar.vue'

const router = useRouter()
const users = ref([])
const selected = ref(null)
const search = ref('')
const status = ref('todos')
const profile = ref('todos')
const loading = ref(true)
const error = ref('')
const actionError = ref('')
const removing = ref(false)

const visibleUsers = computed(() => {
  const term = search.value.trim().toLowerCase()
  if (term.length > 0 && term.length < 5) return []
  return users.value.filter((user) => {
    const match =
      !term ||
      [user.name, user.email, user.document].some((value) => value.toLowerCase().includes(term))
    return (
      match &&
      (profile.value === 'todos' || user.roleKey === profile.value) &&
      (status.value === 'todos' || user.status === status.value)
    )
  })
})

function mapUsers(data) {
  const professionals = (data.profissionais ?? []).map((item) => ({
    id: item.id_profissional,
    name: item.nome,
    email: item.email,
    document: item.id_usuario,
    role: 'Profissional',
    roleKey: 'profissional',
    status: 'desconhecido',
    type: 'profissional',
  }))
  const patients = (data.pacientes ?? []).map((item) => ({
    id: item.id_paciente,
    name: item.nome,
    email: item.email,
    document: item.id_usuario,
    role: 'Paciente',
    roleKey: 'paciente',
    status: 'desconhecido',
    type: 'paciente',
  }))
  return [...professionals, ...patients]
}

async function loadUsers() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await adminApi.get('/api/v1/administracao/usuarios/ids')
    users.value = mapUsers(data)
    if (selected.value)
      selected.value = users.value.find((user) => user.document === selected.value.document) ?? null
  } catch (err) {
    error.value = err.message || 'Não foi possível carregar os usuários.'
  } finally {
    loading.value = false
  }
}

function selectUser(user) {
  selected.value = selected.value?.document === user.document ? null : user
  actionError.value = ''
}

async function deleteUser() {
  if (!selected.value) return
  removing.value = true
  actionError.value = ''
  try {
    await adminApi.post(`/api/v1/administracao/${selected.value.type}s/${selected.value.id}/banir`)
    selected.value = null
    await loadUsers()
  } catch (err) {
    actionError.value = err.message || 'Não foi possível excluir a conta.'
  } finally {
    removing.value = false
  }
}

function logout() {
  adminApi.clearAccessToken()
  router.push('/administracao/usuarios')
}
onMounted(loadUsers)
</script>

<template>
  <div class="min-h-screen bg-[#f4f7fb] text-[#073b57]">
    <AdminHeader @logout="logout" />
    <main class="mx-auto max-w-[1440px] px-4 py-6 lg:px-6">
      <div class="mb-5">
        <p class="flex items-center gap-1 text-[10px] text-[#8496a8]">
          <RouterLink to="/administracao" class="hover:text-[#073b57]"
            >Área do Administrador</RouterLink
          ><span>›</span
          ><RouterLink to="/administracao/usuarios" class="font-semibold text-[#073b57]"
            >Gestão de Usuários</RouterLink
          >
        </p>
        <h1 class="mt-1 text-xl font-bold">Gerenciamento de Usuários</h1>
        <p class="text-xs text-[#8496a8]">
          Consulte os usuários cadastrados no Sistema, vizualize as informações completas de perfil
          e gerencie a exclusão de contas.
        </p>
      </div>
      <section class="rounded-xl border border-[#dde6ef] bg-white p-3 shadow-sm">
        <div class="flex flex-col gap-2 md:flex-row">
          <label class="relative flex-1"
            ><span class="sr-only">Buscar usuário</span
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
              class="h-9 w-full rounded-lg border border-[#dce5ed] bg-[#f8fafc] pl-8 pr-3 text-xs outline-none focus:border-[#08718d]"
              placeholder="Buscar por nome, e-mail ou identificador"
          /></label>
          <select
            v-model="status"
            class="h-9 rounded-lg border border-[#dce5ed] bg-white px-3 text-xs text-[#536b80]"
          >
            <option value="todos">Status: Todos</option>
            <option value="ativo">Status: Ativos</option>
            <option value="inativo">Status: Inativos</option>
          </select>
          <button
            class="flex h-9 items-center gap-1.5 rounded-lg bg-[#042d5c] px-4 text-xs font-semibold text-white hover:bg-[#0b3f7a]"
            @click="loadUsers"
          >
            <svg
              class="size-3.5"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              aria-hidden="true"
            >
              <circle cx="10.8" cy="10.8" r="6.8" />
              <path stroke-linecap="round" d="m16 16 5 5" /></svg
            >Buscar Usuário
          </button>
        </div>
        <div class="mt-3 flex flex-wrap items-center gap-2 text-[10px]">
          <span class="text-[#657c90]">Filtrar por Perfil:</span
          ><button
            v-for="item in [
              { value: 'todos', label: 'Todos os Usuários' },
              { value: 'profissional', label: 'Profissionais' },
              { value: 'paciente', label: 'Pacientes' },
            ]"
            :key="item.value"
            class="rounded-md px-3 py-1.5 font-semibold"
            :class="
              profile === item.value ? 'bg-[#042d5c] text-white' : 'bg-[#f0f4f8] text-[#60778b]'
            "
            @click="profile = item.value"
          >
            {{ item.label }}
          </button>
        </div>
      </section>
      <p v-if="error" class="mt-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">{{ error }}</p>
      <section class="mt-4 overflow-hidden rounded-xl border border-[#dde6ef] bg-white shadow-sm">
        <div v-if="loading" class="p-8 text-center text-sm text-[#8095a8]">
          Carregando usuários...
        </div>
        <div v-else-if="!visibleUsers.length" class="p-8 text-center text-sm text-[#8095a8]">
          {{
            search.length > 0 && search.length < 5
              ? 'Digite pelo menos 5 caracteres para buscar.'
              : 'Nenhum usuário encontrado.'
          }}
        </div>
        <div v-else class="overflow-x-auto">
          <table class="w-full min-w-[760px] text-left text-[10px]">
            <thead class="bg-[#f8fafc] uppercase text-[#71879b]">
              <tr>
                <th class="px-3 py-3">Usuário / Cadastro</th>
                <th class="px-3">Perfil</th>
                <th class="px-3">Identificador</th>
                <th class="px-3">Contato</th>
                <th class="px-3">Status da conta</th>
                <th class="px-3 text-right">Ações</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="user in visibleUsers"
                :key="user.document"
                class="border-t border-[#edf1f5]"
              >
                <td class="px-3 py-3">
                  <div class="flex items-center gap-2">
                    <UserAvatar
                      :name="user.name"
                      class="size-7 bg-[#d8f6f1] text-[9px] font-bold text-[#087d7d]"
                    />
                    <div>
                      <p class="font-bold text-[#16435c]">{{ user.name }}</p>
                      <p class="text-[#9aaaba]">{{ user.email }}</p>
                    </div>
                  </div>
                </td>
                <td class="px-3">
                  <span class="rounded bg-[#eef5fb] px-2 py-1 font-semibold text-[#45657a]">{{
                    user.role
                  }}</span>
                </td>
                <td class="px-3 font-mono text-[#40596d]">{{ user.document.slice(0, 16) }}...</td>
                <td class="px-3 text-[#8194a5]">Não fornecido pela API</td>
                <td class="px-3">
                  <span class="rounded-full bg-[#f0f4f7] px-2 py-1 font-semibold text-[#71879b]"
                    >● Não informado</span
                  >
                </td>
                <td class="px-3 text-right">
                  <button
                    class="rounded-md bg-[#f1f5f8] px-3 py-1.5 font-semibold text-[#526a7d]"
                    @click="selectUser(user)"
                  >
                    ◉ Ver detalhes
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
      <section v-if="selected" class="mt-4 rounded-xl border border-[#cbdbe5] bg-white shadow-sm">
        <div class="flex items-center justify-between border-b border-[#e5edf2] px-5 py-4">
          <div>
            <p class="text-[10px] uppercase text-[#71879b]">Visualização detalhada selecionada</p>
            <p class="text-sm font-bold">{{ selected.name }}</p>
          </div>
          <button
            class="text-xl text-[#9ab0bf]"
            aria-label="Fechar detalhes"
            @click="selected = null"
          >
            ×
          </button>
        </div>
        <div class="grid gap-5 p-5 md:grid-cols-2">
          <div>
            <p class="mb-2 text-[10px] uppercase text-[#71879b]">Dados disponíveis</p>
            <dl class="rounded-lg bg-[#f8fafc] p-4 text-xs">
              <div class="flex justify-between border-b border-white py-2">
                <dt class="text-[#8498a9]">Nome completo</dt>
                <dd class="font-semibold">{{ selected.name }}</dd>
              </div>
              <div class="flex justify-between border-b border-white py-2">
                <dt class="text-[#8498a9]">E-mail</dt>
                <dd class="font-semibold">{{ selected.email }}</dd>
              </div>
              <div class="flex justify-between py-2">
                <dt class="text-[#8498a9]">Perfil</dt>
                <dd class="font-semibold">{{ selected.role }}</dd>
              </div>
            </dl>
          </div>
          <div>
            <p class="mb-2 text-[10px] uppercase text-[#71879b]">Identificação da conta</p>
            <dl class="rounded-lg bg-[#f8fafc] p-4 text-xs">
              <div class="flex justify-between border-b border-white py-2">
                <dt class="text-[#8498a9]">ID do usuário</dt>
                <dd class="max-w-[220px] truncate font-mono font-semibold">
                  {{ selected.document }}
                </dd>
              </div>
              <div class="flex justify-between py-2">
                <dt class="text-[#8498a9]">Status</dt>
                <dd class="font-semibold text-[#71879b]">Não informado pela API atual</dd>
              </div>
            </dl>
          </div>
        </div>
        <div
          class="mx-5 mb-5 flex flex-col items-start justify-between gap-3 rounded-lg border border-red-100 bg-red-50 p-3 text-xs md:flex-row md:items-center"
        >
          <div>
            <p class="font-bold text-red-700">Zona de Ação Crítica - Exclusão Definitiva</p>
            <p class="text-red-500">A exclusão banirá a conta e encerrará suas sessões.</p>
          </div>
          <button
            class="rounded-md bg-red-600 px-4 py-2 font-semibold text-white disabled:opacity-50"
            :disabled="removing"
            @click="deleteUser"
          >
            {{ removing ? 'Excluindo...' : 'Excluir Conta do Usuário' }}
          </button>
        </div>
        <p v-if="actionError" class="mx-5 mb-5 text-xs text-red-700">{{ actionError }}</p>
      </section>
    </main>
  </div>
</template>