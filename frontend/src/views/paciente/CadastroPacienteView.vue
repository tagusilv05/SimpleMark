<script setup>
/**
 * CadastroPacienteView — tela de criação de conta do paciente
 *
 * Fluxo: home -> Entrar -> Paciente -> login do paciente -> Cadastre-se agora -> esta tela
 * (rota `cadastro/paciente`).
 *
 * Estrutura:
 *   - Coluna esquerda: logo + cartão com o formulário
 *   - Coluna direita: imagem ilustrativa (escondida em telas < lg)
 *
 * Cada campo só aceita o que se pede (ver `mascaras`): o texto digitado ou colado
 * passa por um filtro, então letras não entram em CPF/telefone/CEP/data, números
 * não entram no nome, e assim por diante. A validação completa roda ao enviar.
 *
 * Componentes usados:
 *   - FormField  (variante "outline", com erro por campo)
 *   - FormButton (Criar Conta e Faça login)
 */

import { nextTick, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import FormField from '@/components/shared/FormField.vue'
import FormButton from '@/components/shared/FormButton.vue'
import heroImage from '@/assets/imagempaciente.jpg'

const router = useRouter()

// Caminhos "d" dos ícones (Heroicons 24x24)
const icons = {
  user: 'M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z',
  calendar:
    'M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 0 1 2.25-2.25h13.5A2.25 2.25 0 0 1 21 7.5v11.25m-18 0A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75m-18 0v-7.5A2.25 2.25 0 0 1 5.25 9h13.5A2.25 2.25 0 0 1 21 11.25v7.5m-9-6h.008v.008H12v-.008ZM12 15h.008v.008H12V15Zm0 2.25h.008v.008H12v-.008ZM9.75 15h.008v.008H9.75V15Zm0 2.25h.008v.008H9.75v-.008ZM7.5 15h.008v.008H7.5V15Zm0 2.25h.008v.008H7.5v-.008Zm6.75-4.5h.008v.008h-.008v-.008Zm0 2.25h.008v.008h-.008V15Zm0 2.25h.008v.008h-.008v-.008Zm2.25-4.5h.008v.008H16.5v-.008Zm0 2.25h.008v.008H16.5V15Z',
  users:
    'M15 19.128a9.38 9.38 0 0 0 2.625.372 9.337 9.337 0 0 0 4.121-.952 4.125 4.125 0 0 0-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 0 1 8.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0 1 11.964-3.07M12 6.375a3.375 3.375 0 1 1-6.75 0 3.375 3.375 0 0 1 6.75 0Zm8.25 2.25a2.625 2.625 0 1 1-5.25 0 2.625 2.625 0 0 1 5.25 0Z',
  id: 'M15 9h3.75M15 12h3.75M15 15h3.75M4.5 19.5h15a2.25 2.25 0 0 0 2.25-2.25V6.75A2.25 2.25 0 0 0 19.5 4.5h-15a2.25 2.25 0 0 0-2.25 2.25v10.5A2.25 2.25 0 0 0 4.5 19.5Zm6-10.125a1.875 1.875 0 1 1-3.75 0 1.875 1.875 0 0 1 3.75 0Zm1.294 6.336a6.721 6.721 0 0 1-3.17.789 6.721 6.721 0 0 1-3.168-.789 3.376 3.376 0 0 1 6.338 0Z',
  mail: 'M21.75 6.75v10.5a2.25 2.25 0 0 1-2.25 2.25h-15a2.25 2.25 0 0 1-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0 0 19.5 4.5h-15a2.25 2.25 0 0 0-2.25 2.25m19.5 0v.243a2.25 2.25 0 0 1-1.07 1.916l-7.5 4.615a2.25 2.25 0 0 1-2.36 0L3.32 8.91a2.25 2.25 0 0 1-1.07-1.916V6.75',
  phone:
    'M2.25 6.75c0 8.284 6.716 15 15 15h2.25a2.25 2.25 0 0 0 2.25-2.25v-1.372c0-.516-.351-.966-.852-1.091l-4.423-1.106c-.44-.11-.902.055-1.173.417l-.97 1.293c-.282.376-.769.542-1.21.38a12.035 12.035 0 0 1-7.143-7.143c-.162-.441.004-.928.38-1.21l1.293-.97c.363-.271.527-.734.417-1.173L6.963 3.102a1.125 1.125 0 0 0-1.091-.852H4.5A2.25 2.25 0 0 0 2.25 4.5v2.25Z',
  pin: 'M15 10.5a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1 1 15 0Z',
  home: 'm2.25 12 8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25',
  lock: 'M16.5 10.5V6.75a4.5 4.5 0 1 0-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 0 0 2.25-2.25v-6.75a2.25 2.25 0 0 0-2.25-2.25H6.75a2.25 2.25 0 0 0-2.25 2.25v6.75a2.25 2.25 0 0 0 2.25 2.25Z',
}

const generos = ['Masculino', 'Feminino', 'Outro']

const form = reactive({
  nome: '',
  nascimento: '',
  genero: '',
  cpf: '',
  orgaoEmissor: '',
  email: '',
  celular: '',
  cep: '',
  endereco: '',
  senha: '',
  confirmarSenha: '',
})

const errors = reactive({})
const carregando = ref(false)

// ---- Filtros de digitação: cada campo só aceita o que se pede ----
const soDigitos = (v) => v.replace(/\D/g, '')
const limparEspacos = (v) => v.replace(/\s{2,}/g, ' ').replace(/^\s+/, '')

const mascaras = {
  // letras (com acentos), espaço, apóstrofo e hífen
  nome: (v) => limparEspacos(v.replace(/[^\p{L}\s'’-]/gu, '')).slice(0, 100),

  // DD/MM/AAAA
  nascimento: (v) => {
    const d = soDigitos(v).slice(0, 8)
    if (d.length > 4) return `${d.slice(0, 2)}/${d.slice(2, 4)}/${d.slice(4)}`
    if (d.length > 2) return `${d.slice(0, 2)}/${d.slice(2)}`
    return d
  },

  // 000.000.000-00
  cpf: (v) => {
    const d = soDigitos(v).slice(0, 11)
    if (d.length > 9) return `${d.slice(0, 3)}.${d.slice(3, 6)}.${d.slice(6, 9)}-${d.slice(9)}`
    if (d.length > 6) return `${d.slice(0, 3)}.${d.slice(3, 6)}.${d.slice(6)}`
    if (d.length > 3) return `${d.slice(0, 3)}.${d.slice(3)}`
    return d
  },

  // só letras, espaço, ponto, barra e hífen (ex.: SSP/PI, DETRAN-PI, CIN), sem números
  orgaoEmissor: (v) => limparEspacos(v.replace(/[^\p{L}\s/.-]/gu, '')).slice(0, 20),

  // sem espaços e sem números; só letras, @ . _ + - e um único @
  email: (v) => {
    const limpo = v.replace(/[^a-zA-Z@._+-]/g, '').toLowerCase().slice(0, 100)
    const i = limpo.indexOf('@')
    return i === -1 ? limpo : limpo.slice(0, i + 1) + limpo.slice(i + 1).replace(/@/g, '')
  },

  // (00) 00000-0000
  celular: (v) => {
    const d = soDigitos(v).slice(0, 11)
    if (d.length > 7) return `(${d.slice(0, 2)}) ${d.slice(2, 7)}-${d.slice(7)}`
    if (d.length > 2) return `(${d.slice(0, 2)}) ${d.slice(2)}`
    return d ? `(${d}` : ''
  },

  // 00000-000
  cep: (v) => {
    const d = soDigitos(v).slice(0, 8)
    return d.length > 5 ? `${d.slice(0, 5)}-${d.slice(5)}` : d
  },

  // letras, números, espaço e , . - / º ª #
  endereco: (v) => limparEspacos(v.replace(/[^\p{L}\d\s,.\-/ºª#]/gu, '')).slice(0, 150),

  // sem espaços
  senha: (v) => v.replace(/\s/g, '').slice(0, 64),
  confirmarSenha: (v) => v.replace(/\s/g, '').slice(0, 64),
}

function atualizar(campo, valor) {
  form[campo] = mascaras[campo] ? mascaras[campo](valor) : valor
  delete errors[campo]
  if (campo === 'senha') delete errors.confirmarSenha
}

// ---- Validações (rodam ao clicar em "Criar Conta") ----
function cpfValido(valor) {
  const d = soDigitos(valor)
  if (d.length !== 11 || /^(\d)\1{10}$/.test(d)) return false
  const digito = (base) => {
    let soma = 0
    for (let i = 0; i < base; i++) soma += Number(d[i]) * (base + 1 - i)
    const resto = (soma * 10) % 11
    return resto === 10 ? 0 : resto
  }
  return digito(9) === Number(d[9]) && digito(10) === Number(d[10])
}

function dataValida(valor) {
  const m = /^(\d{2})\/(\d{2})\/(\d{4})$/.exec(valor)
  if (!m) return false
  const [dia, mes, ano] = [Number(m[1]), Number(m[2]), Number(m[3])]
  const data = new Date(ano, mes - 1, dia)
  const existe =
    data.getFullYear() === ano && data.getMonth() === mes - 1 && data.getDate() === dia
  return existe && ano >= 1900 && data <= new Date()
}

function validar() {
  const e = {}

  if (form.nome.trim().split(/\s+/).filter(Boolean).length < 2) e.nome = 'Informe nome e sobrenome.'
  if (!dataValida(form.nascimento)) e.nascimento = 'Informe uma data válida (DD/MM/AAAA).'
  if (!generos.includes(form.genero)) e.genero = 'Selecione o gênero.'
  if (!cpfValido(form.cpf)) e.cpf = 'CPF inválido.'
  if (form.orgaoEmissor.trim().length < 2) e.orgaoEmissor = 'Informe o órgão emissor.'
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(form.email)) e.email = 'Informe um e-mail válido.'

  const celular = soDigitos(form.celular)
  if (celular.length !== 11 || celular[2] !== '9') e.celular = 'Informe um celular válido com DDD.'

  if (soDigitos(form.cep).length !== 8) e.cep = 'O CEP deve ter 8 dígitos.'
  if (form.endereco.trim().length < 5) e.endereco = 'Informe seu endereço.'
  if (form.senha.length < 8) e.senha = 'A senha deve ter no mínimo 8 caracteres.'
  if (form.confirmarSenha !== form.senha) e.confirmarSenha = 'As senhas não conferem.'

  Object.keys(errors).forEach((k) => delete errors[k])
  Object.assign(errors, e)
  return Object.keys(e).length === 0
}

async function criarConta() {
  if (carregando.value) return

  if (!validar()) {
    // leva a tela até o primeiro campo com erro
    await nextTick()
    document.querySelector('[role="alert"]')?.scrollIntoView({ behavior: 'smooth', block: 'center' })
    return
  }

  carregando.value = true
  try {
    // TODO: enviar ao backend. Sugestão de payload (só números onde faz sentido):
    // const [dia, mes, ano] = form.nascimento.split('/')
    // await pacienteService.cadastrar({
    //   nome: form.nome.trim(),
    //   data_nascimento: `${ano}-${mes}-${dia}`,
    //   genero: form.genero,
    //   cpf: soDigitos(form.cpf),
    //   orgao_emissor: form.orgaoEmissor.trim(),
    //   email: form.email,
    //   celular: soDigitos(form.celular),
    //   cep: soDigitos(form.cep),
    //   endereco: form.endereco.trim(),
    //   senha: form.senha,
    // })
    // Enquanto o serviço não está ligado, segue direto para a tela de sucesso.
    // Ao ligar, deixe o push só depois do await do cadastro (e trate o erro do backend).
    router.push({ name: 'cadastro/paciente/sucesso' })
  } finally {
    carregando.value = false
  }
}

function irParaLogin() {
  router.push({ name: 'login/paciente' })
}
</script>

<template>
  <main class="grid min-h-screen bg-[#fafaff] lg:grid-cols-[minmax(0,40fr)_minmax(0,60fr)]">
    <!-- Coluna do formulário -->
    <section class="flex flex-col px-6 pt-6 sm:px-10 lg:pt-8">
      <img
        src="/LOGO%20OFICIAL%20SEM%20FUNDO.png"
        alt="Simple Mark"
        class="h-36 w-auto self-start"
      />

      <!-- my-auto centraliza o cartão no espaço entre a logo e o fim da página (margens iguais em cima e embaixo) -->
      <div class="my-auto w-full max-w-111.75 py-8 lg:ml-16">
        <div class="rounded-2xl border border-gray-200 bg-white p-6 sm:p-10">
          <header class="mb-8">
            <h1 class="text-2xl font-medium text-[#00507a]">Crie sua conta</h1>
            <p class="mt-2 text-[15px] leading-6 text-gray-700">
              Preencha os dados abaixo para acessar o portal do paciente.
            </p>
          </header>

          <form class="flex flex-col gap-6" novalidate @submit.prevent="criarConta">
            <FormField
              label="Nome Completo"
              variant="outline"
              placeholder="Seu nome completo"
              :icon="icons.user"
              :model-value="form.nome"
              :error="errors.nome"
              @update:model-value="atualizar('nome', $event)"
            />

            <FormField
              label="Data de Nascimento"
              variant="outline"
              inputmode="numeric"
              placeholder="DD/MM/AAAA"
              :icon="icons.calendar"
              :model-value="form.nascimento"
              :error="errors.nascimento"
              @update:model-value="atualizar('nascimento', $event)"
            />

            <FormField
              label="Gênero"
              type="select"
              variant="outline"
              placeholder="Selecione o gênero"
              :options="generos"
              :icon="icons.users"
              :model-value="form.genero"
              :error="errors.genero"
              @update:model-value="atualizar('genero', $event)"
            />

            <FormField
              label="CPF"
              variant="outline"
              inputmode="numeric"
              placeholder="000.000.000-00"
              :icon="icons.id"
              :model-value="form.cpf"
              :error="errors.cpf"
              @update:model-value="atualizar('cpf', $event)"
            />

            <FormField
              label="Órgão Emissor"
              variant="outline"
              placeholder="Órgão emissor CIN"
              :icon="icons.id"
              :model-value="form.orgaoEmissor"
              :error="errors.orgaoEmissor"
              @update:model-value="atualizar('orgaoEmissor', $event)"
            />

            <FormField
              label="E-mail"
              type="email"
              variant="outline"
              inputmode="email"
              placeholder="seu@email.com"
              :icon="icons.mail"
              :model-value="form.email"
              :error="errors.email"
              @update:model-value="atualizar('email', $event)"
            />

            <FormField
              label="Celular"
              type="tel"
              variant="outline"
              inputmode="tel"
              placeholder="(00) 00000-0000"
              :icon="icons.phone"
              :model-value="form.celular"
              :error="errors.celular"
              @update:model-value="atualizar('celular', $event)"
            />

            <FormField
              label="CEP"
              variant="outline"
              inputmode="numeric"
              placeholder="00000-000"
              :icon="icons.pin"
              :model-value="form.cep"
              :error="errors.cep"
              @update:model-value="atualizar('cep', $event)"
            />

            <FormField
              label="Endereço"
              variant="outline"
              placeholder="Av. Principal, 45, próx catedral da sé"
              :icon="icons.home"
              :model-value="form.endereco"
              :error="errors.endereco"
              @update:model-value="atualizar('endereco', $event)"
            />

            <FormField
              label="Senha"
              type="password"
              variant="outline"
              placeholder="••••••••"
              :icon="icons.lock"
              :model-value="form.senha"
              :error="errors.senha"
              @update:model-value="atualizar('senha', $event)"
            />

            <FormField
              label="Confirmar Senha"
              type="password"
              variant="outline"
              placeholder="••••••••"
              :icon="icons.lock"
              :model-value="form.confirmarSenha"
              :error="errors.confirmarSenha"
              @update:model-value="atualizar('confirmarSenha', $event)"
            />

            <FormButton type="submit" class="h-13! w-full" :disabled="carregando">
              Criar Conta
            </FormButton>
          </form>

          <div class="mt-8 flex flex-col items-center gap-4 border-t border-gray-200 pt-8">
            <p class="text-[15px] text-gray-700">Já possui uma conta?</p>
            <FormButton
              variant="text"
              class="border-2 border-[#042d5c] bg-white"
              @click="irParaLogin"
            >
              Faça login
            </FormButton>
          </div>
        </div>
      </div>
    </section>

    <!-- Coluna da imagem (somente desktop) -->
    <!-- A imagem fica fixa na altura da janela enquanto o formulário rola, em vez de esticar pela página inteira -->
    <aside class="hidden lg:block">
      <div class="sticky top-0 h-screen overflow-hidden">
        <img
          :src="heroImage"
          alt="Paciente em uma teleconsulta com um médico"
          class="size-full object-cover object-right"
        />
      </div>
    </aside>
  </main>
</template>