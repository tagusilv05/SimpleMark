<script setup>
/**
 * PerfilConta — conteúdo da tela "Minha Conta" (paciente e profissional).
 *
 * Abas: Dados Pessoais, Endereço, Segurança (troca de senha), Perfil Profissional
 * (só profissional: apresentação, foto, especialidades e valores) e Excluir Conta
 * (desativar ou excluir). Tudo vem da API pela conta logada (services/perfilService).
 */
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
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
const route = useRoute()
const auth = useAuthStore()

const isProfissional = computed(() => props.role === 'profissional')
const roleLabel = computed(() => (isProfissional.value ? 'Profissional' : 'Paciente'))
const idUsuario = computed(() => auth.usuario?.id)

// Aba inicial pode vir da URL (?aba=perfil), ex.: botão "Gerenciar especialidades" da agenda
const ABAS = ['dados', 'endereco', 'seguranca', 'perfil', 'excluir']
const abaPedida = String(route.query.aba ?? '')
const aba = ref(ABAS.includes(abaPedida) && (abaPedida !== 'perfil' || props.role === 'profissional') ? abaPedida : 'dados')
const carregando = ref(false)
const erro = ref('')
const erroSenha = ref('')
const sucesso = ref('')

const dados = ref({
  nome: '', cpf: '', orgao: '', nascimento: '', genero: '', telefone: '', email: '',
})

const endereco = ref({
  cep: '', cidade: '', logradouro: '', numero: '', bairro: '', complemento: '',
})

const profissional = ref({
  fotoUrl: '',
  apresentacao: '',
  // { id (chave da lista), idEspecialidade, name, registration, council, number, price }
  especialidades: [],
})
// O backend só devolve o perfil de profissional validado (conta ativa)
const verificado = computed(() => Boolean(auth.usuario?.status))

// Lista vinda do backend: [{ id_especialidade, especialidade }]
const listaEspecialidades = ref([])
// No select de nova especialidade só aparecem as que o profissional ainda não tem
const especialidadesDisponiveis = computed(() => {
  const usadas = new Set(profissional.value.especialidades.map((e) => e.name))
  return listaEspecialidades.value.map((e) => e.especialidade).filter((nome) => !usadas.has(nome))
})

// id_especialidade das especialidades como estão no servidor (para saber o que foi removido)
let especialidadesOriginais = []

/* ---------- Conversões backend <-> tela ---------- */

// '1980-01-15' -> '15/01/1980' (sem new Date, para evitar bug de fuso)
function isoParaBR(iso) {
  if (!iso) return ''
  const [a, m, d] = iso.split('-')
  return `${d}/${m}/${a}`
}

function formatarTelefone(valor) {
  const d = String(valor ?? '').replace(/\D/g, '')
  if (d.length === 11) return d.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3')
  if (d.length === 10) return d.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3')
  return valor ?? ''
}

function formatarPreco(valor) {
  return Number(valor ?? 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
}

// 'R$ 1.250,50' -> 1250.5 · '250' -> 250 · '250.5' -> 250.5
function precoParaNumero(preco) {
  if (typeof preco === 'number') return preco
  let texto = String(preco ?? '').replace(/[^\d.,]/g, '')
  if (texto.includes(',')) texto = texto.replace(/\./g, '').replace(',', '.')
  const numero = Number(texto)
  return Number.isFinite(numero) ? numero : NaN
}

// 'CRM-PI 1234' -> { conselho: 'CRM-PI', numero: '1234' }
function separarRegistro(registro) {
  const texto = String(registro ?? '').trim()
  const partes = texto.match(/^([A-Za-zÀ-ú]+(?:[-/ ][A-Za-z]{2})?)\s*[-:nº°.]*\s*(\d[\w.\-/]*)$/)
  if (partes) return { conselho: partes[1].toUpperCase().replace(' ', '-'), numero: partes[2] }
  return { conselho: '', numero: texto }
}

function idPorNome(nome) {
  return listaEspecialidades.value.find((e) => e.especialidade === nome)?.id_especialidade
}

function especialidadeDaApi(e) {
  return {
    id: e.id_especialidade,
    idEspecialidade: e.id_especialidade,
    name: e.nome,
    council: e.conselho,
    number: e.numero_conselho,
    registration: [e.conselho, e.numero_conselho].filter(Boolean).join(' '),
    price: formatarPreco(e.valor),
  }
}

/* ---------- Carregamento ---------- */

async function executar(fn, msgSucesso = '') {
  erro.value = ''
  sucesso.value = ''
  carregando.value = true
  try {
    await fn()
    if (msgSucesso) sucesso.value = msgSucesso
    return true
  } catch (e) {
    erro.value = e.message || 'Não foi possível concluir a operação.'
    return false
  } finally {
    carregando.value = false
  }
}

async function carregarProfissional(id) {
  const [lista, infoProf] = await Promise.all([
    perfil.listarEspecialidades(),
    perfil.buscarInfoProfissional(id),
  ])
  listaEspecialidades.value = lista

  profissional.value.apresentacao = infoProf.info_profissional ?? ''
  profissional.value.especialidades = (infoProf.especialidade ?? []).map(especialidadeDaApi)
  especialidadesOriginais = profissional.value.especialidades.map((e) => e.idEspecialidade)

  // Foto é opcional: se não existir, só segue sem ela
  try {
    profissional.value.fotoUrl = await perfil.buscarImagemProfissional(id)
  } catch {
    profissional.value.fotoUrl = ''
  }
}

async function carregarTudo() {
  const id = idUsuario.value
  if (!id) throw new Error('Entre novamente para ver os dados da sua conta.')

  const [info, end] = await Promise.all([perfil.buscarInfoUsuario(id), perfil.buscarInfoEndereco(id)])

  dados.value = {
    nome: info.nome,
    cpf: info.cpf,
    orgao: info.orgao_emissor,
    nascimento: isoParaBR(info.data_nascimento),
    genero: info.genero,
    telefone: formatarTelefone(info.telefone),
    email: info.email,
  }
  if (end) endereco.value = { ...end, numero: String(end.numero ?? ''), complemento: end.complemento ?? '' }

  if (isProfissional.value) await carregarProfissional(id)
}

onMounted(() => executar(carregarTudo))

/* ---------- Ações ---------- */

function salvar(valores) {
  // O backend altera nome, e-mail e telefone (CPF, nascimento etc. não mudam)
  return executar(async () => {
    const r = await perfil.alterarInfoPessoal({
      id: idUsuario.value,
      nome: valores.nome,
      email: valores.email,
      telefone: valores.telefone,
    })
    dados.value = { ...dados.value, ...r, telefone: formatarTelefone(r.telefone) }
    auth.atualizarUsuario({ nome: r.nome, email: r.email, telefone: r.telefone })
  }, 'Dados pessoais atualizados.')
}

function salvarEndereco(valores) {
  return executar(async () => {
    const r = await perfil.alterarEndereco(idUsuario.value, valores)
    endereco.value = { ...r, numero: String(r.numero ?? ''), complemento: r.complemento ?? '' }
  }, 'Endereço atualizado.')
}

async function salvarSenha(valores) {
  erroSenha.value = ''
  const ok = await executar(() => perfil.alterarSenha(valores), 'Senha alterada com sucesso.')
  if (!ok) {
    erroSenha.value = erro.value
    erro.value = ''
  }
}

function buscarCep() {
  window.open('https://buscacepinter.correios.com.br/app/endereco/index.php', '_blank')
}

function trocarFoto(file) {
  return executar(async () => {
    await perfil.salvarImagemProfissional(idUsuario.value, file)
    profissional.value.fotoUrl = URL.createObjectURL(file)
  }, 'Foto atualizada.')
}

function salvarProfissional() {
  return executar(async () => {
    const atuais = profissional.value.especialidades.map((e) => {
      const idEspecialidade = e.idEspecialidade ?? idPorNome(e.name)
      // Item novo (formulário "Adicionar") traz o registro num texto só: 'CRM-PI 1234'
      const { conselho, numero } = e.council ? { conselho: e.council, numero: e.number } : separarRegistro(e.registration)
      return { ...e, idEspecialidade, council: conselho, number: numero }
    })

    for (const e of atuais) {
      if (!e.idEspecialidade) throw new Error(`Especialidade "${e.name}" não encontrada.`)
      if (!e.council || !e.number) {
        throw new Error(`Informe o conselho e o número de "${e.name}" (ex.: CRM-PI 1234).`)
      }
      const valor = precoParaNumero(e.price)
      if (!Number.isFinite(valor) || valor <= 0) throw new Error(`Informe um valor válido para "${e.name}".`)
    }

    // 1) remove as especialidades que o profissional tirou da lista
    const idsAtuais = atuais.map((e) => e.idEspecialidade)
    for (const idEsp of especialidadesOriginais.filter((id) => !idsAtuais.includes(id))) {
      await perfil.excluirEspecialidade(idUsuario.value, idEsp)
    }

    // 2) envia apresentação + especialidades (as existentes são atualizadas, as novas criadas)
    await perfil.alterarInfoProfissional(
      idUsuario.value,
      profissional.value.apresentacao,
      atuais.map((e) => ({
        id_especialidade: e.idEspecialidade,
        numero_conselho: e.number,
        conselho: e.council,
        valor: precoParaNumero(e.price),
      })),
    )

    // 3) recarrega do servidor para mostrar exatamente o que ficou gravado
    await carregarProfissional(idUsuario.value)
  }, 'Perfil profissional atualizado.')
}

function encerrarSessaoLocal() {
  // O servidor já encerrou as sessões desta conta
  auth.limparSessaoLocal()
  router.replace({ name: 'home' })
}

async function desativarConta() {
  const ok = await executar(() => perfil.inativarUsuario(idUsuario.value))
  if (ok) encerrarSessaoLocal()
}

async function excluirConta() {
  const ok = await executar(() => perfil.excluirUsuario(idUsuario.value, props.role))
  if (ok) encerrarSessaoLocal()
}
</script>

<template>
  <div class="flex flex-col gap-6">
    <ProfileCard
      :name="dados.nome"
      :role="roleLabel"
      :email="dados.email"
      :phone="dados.telefone"
      :verified="isProfissional && verificado"
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

      <FormCardSeguranca v-else-if="aba === 'seguranca'" :error="erroSenha" @submit="salvarSenha" />

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
        :verified="verificado"
        :specialty-options="especialidadesDisponiveis"
        :saving="carregando"
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