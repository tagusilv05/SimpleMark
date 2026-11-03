<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import * as perfil from '@/services/perfilService'
import ProfileCard from '@/components/shared/ProfileCard.vue'
import SideMenu from '@/components/shared/SideMenu.vue'
import FormCardDadosPessoais from '@/components/shared/FormCardDadosPessoais.vue'
import FormCardEndereco from '@/components/shared/FormCardEndereco.vue'
import FormCardSeguranca from '@/components/shared/FormCardSeguranca.vue'
import FormCardExcluirConta from '@/components/shared/FormCardExcluirConta.vue'
import ProfessionalManagement from '@/components/profissional/ProfessionalManagement.vue'

// 'paciente' | 'profissional'
const props = defineProps({
  role: {
    type: String,
    default: 'paciente',
    validator: (v) => ['paciente', 'profissional'].includes(v),
  },
})

const router = useRouter()
const auth = useAuthStore()

const isProfissional = computed(() => props.role === 'profissional')
const roleLabel = computed(() => (isProfissional.value ? 'Profissional' : 'Paciente'))
const idUsuario = computed(() => auth.usuario?.id) // ajuste se sua store usa outro nome

const aba = ref('dados')
const carregando = ref(false)
const erro = ref('')
const sucesso = ref('')

const dados = ref({
  nome: '', cpf: '', orgao: '', nascimento: '', genero: '', telefone: '', email: '',
})

const endereco = ref({
  cep: '', cidade: '', logradouro: '', numero: '', bairro: '', complemento: '',
})

const profissional = ref({
  fotoUrl: '',
  verificado: true,
  apresentacao: '',
  especialidades: [],
})

// Lista vinda do backend: [{ id_especialidade, especialidade }]
const listaEspecialidades = ref([])
const especialidadesDisponiveis = computed(() => listaEspecialidades.value.map((e) => e.especialidade))

// Cópia do que veio do servidor, para detectar especialidades removidas ao salvar
let especialidadesOriginais = []

/* ---------- Conversões backend <-> tela ---------- */

// '1980-01-15' -> '15/01/1980' (sem new Date, para evitar bug de fuso)
function isoParaBR(iso) {
  if (!iso) return ''
  const [a, m, d] = iso.split('-')
  return `${d}/${m}/${a}`
}

function formatarPreco(valor) {
  return `R$ ${Number(valor ?? 0).toFixed(2).replace('.', ',')}`
}

function precoParaNumero(preco) {
  if (typeof preco === 'number') return preco
  return Number(String(preco).replace(/[^\d,]/g, '').replace(',', '.')) || 0
}

function idPorNome(nome) {
  return listaEspecialidades.value.find((e) => e.especialidade === nome)?.id_especialidade
}

/* ---------- Carregamento ---------- */

async function executar(fn, msgSucesso = '') {
  erro.value = ''
  sucesso.value = ''
  carregando.value = true
  try {
    await fn()
    if (msgSucesso) sucesso.value = msgSucesso
  } catch (e) {
    erro.value = e.message
  } finally {
    carregando.value = false
  }
}

async function carregarTudo() {
  const id = idUsuario.value
  const token = auth.token

  const [info, end] = await Promise.all([
    perfil.buscarInfoUsuario(id, token),
    perfil.buscarInfoEndereco(id, token),
  ])

  dados.value = {
    nome: info.nome,
    cpf: info.cpf,
    orgao: info.orgao_emissor,
    nascimento: isoParaBR(info.data_nascimento),
    genero: info.genero,
    telefone: info.telefone,
    email: info.email,
  }
  endereco.value = { ...end, numero: String(end.numero ?? '') }

  if (isProfissional.value) {
    const [lista, infoProf] = await Promise.all([
      perfil.listarEspecialidades(token),
      perfil.buscarInfoProfissional(id, token),
    ])
    listaEspecialidades.value = lista

    profissional.value.apresentacao = infoProf.info_profissional ?? ''
    profissional.value.especialidades = (infoProf.especialidade ?? []).map((e) => ({
      id: e.id_especialidade,
      name: e.nome,
      registration: e.numero_conselho,
      council: e.conselho,
      price: formatarPreco(e.valor),
    }))
    especialidadesOriginais = profissional.value.especialidades.map((e) => e.id)

    // Foto é opcional: se não existir, só segue sem ela
    try {
      profissional.value.fotoUrl = await perfil.buscarImagemProfissional(id, token)
    } catch {
      profissional.value.fotoUrl = ''
    }
  }
}

onMounted(() => executar(carregarTudo))

/* ---------- Ações ---------- */

function salvar(valores) {
  // O backend só altera nome, email e telefone
  return executar(async () => {
    const r = await perfil.alterarInfoPessoal(
      { id: idUsuario.value, nome: valores.nome, email: valores.email, telefone: valores.telefone },
      auth.token,
    )
    dados.value = { ...dados.value, ...r }
  }, 'Dados pessoais atualizados.')
}

function salvarEndereco(valores) {
  return executar(async () => {
    const r = await perfil.alterarEndereco(idUsuario.value, valores, auth.token)
    endereco.value = { ...r, numero: String(r.numero) }
  }, 'Endereço atualizado.')
}

function salvarSenha() {
  // Ainda não existe endpoint de troca de senha no backend
  erro.value = 'A troca de senha ainda não está disponível.'
}

function buscarCep() {
  window.open('https://buscacepinter.correios.com.br/app/endereco/index.php', '_blank')
}

function trocarFoto(file) {
  return executar(async () => {
    await perfil.salvarImagemProfissional(idUsuario.value, file, auth.token)
    profissional.value.fotoUrl = URL.createObjectURL(file)
  }, 'Foto atualizada.')
}

function salvarProfissional() {
  return executar(async () => {
    const atuais = profissional.value.especialidades

    // 1) remove as especialidades que o usuário tirou da lista
    const idsAtuais = atuais.map((e) => e.id).filter(Boolean)
    const removidas = especialidadesOriginais.filter((id) => !idsAtuais.includes(id))
    for (const idEsp of removidas) {
      await perfil.excluirEspecialidade(idUsuario.value, idEsp, auth.token)
    }

    // 2) envia bio + especialidades (inclui valor da consulta)
    const payload = atuais.map((e) => ({
      id_especialidade: e.id ?? idPorNome(e.name),
      numero_conselho: e.registration,
      conselho: e.council,
      valor: precoParaNumero(e.price),
    }))
    await perfil.alterarInfoProfissional(
      idUsuario.value,
      profissional.value.apresentacao,
      payload,
      auth.token,
    )

    // 3) guarda o novo estado como "original"
    profissional.value.especialidades = atuais.map((e, i) => ({
      ...e,
      id: payload[i].id_especialidade,
    }))
    especialidadesOriginais = payload.map((p) => p.id_especialidade)
  }, 'Perfil profissional atualizado.')
}

function desativarConta() {
  // Ainda não existe endpoint de desativação no backend
  erro.value = 'A desativação de conta ainda não está disponível.'
}

function excluirConta() {
  return executar(async () => {
    await perfil.excluirUsuario(idUsuario.value, props.role, auth.token)
    auth.logout?.() // ajuste para o nome da ação de sair na sua store
    router.push('/login') // ajuste para a sua rota de login
  })
}
</script>

<template>
  <div class="flex flex-col gap-6">
    <ProfileCard
      :name="dados.nome"
      :role="roleLabel"
      :email="dados.email"
      :phone="dados.telefone"
      member-since="Fevereiro de 2026"
    />

    <p v-if="erro" class="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{{ erro }}</p>
    <p v-if="sucesso" class="rounded-lg bg-green-50 px-4 py-3 text-sm text-green-700">
      {{ sucesso }}
    </p>

    <div class="grid grid-cols-1 items-start gap-8 md:grid-cols-[16rem_1fr]">
      <SideMenu v-model="aba" :role="role" />

      <FormCardDadosPessoais
        v-if="aba === 'dados'"
        v-model="dados"
        @submit="salvar"
        @back="router.back()"
      />

      <FormCardEndereco
        v-else-if="aba === 'endereco'"
        v-model="endereco"
        @submit="salvarEndereco"
        @hint="buscarCep"
      />

      <FormCardSeguranca v-else-if="aba === 'seguranca'" @submit="salvarSenha" />

      <FormCardExcluirConta
        v-else-if="aba === 'excluir'"
        @desativar="desativarConta"
        @excluir="excluirConta"
      />

      <ProfessionalManagement
        v-else-if="aba === 'perfil' && isProfissional"
        v-model:bio="profissional.apresentacao"
        v-model:specialties="profissional.especialidades"
        :photo="profissional.fotoUrl"
        :verified="profissional.verificado"
        :specialty-options="especialidadesDisponiveis"
        @photo-change="trocarFoto"
        @save="salvarProfissional"
      />

      <section
        v-else
        class="rounded-xl bg-white p-8 text-gray-500 shadow-[0_2px_12px_rgba(11,47,91,0.08)]"
      >
        Em breve. (aba: {{ aba }})
      </section>
    </div>
  </div>
</template>