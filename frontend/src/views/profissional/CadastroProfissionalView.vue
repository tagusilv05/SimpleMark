<script setup>
/**
 * CadastroProfissionalView — criação de conta do profissional de saúde
 *
 * Fluxo: login do profissional -> "Cadastre-se" -> esta tela (rota `cadastro/profissional`)
 *        -> Criar Conta -> sucesso (rota `cadastro/profissional/sucesso`).
 *
 * Estrutura:
 *   - Coluna esquerda: logo + cartão com o formulário (a página rola)
 *   - Coluna direita: imagem ilustrativa, fixa na altura da janela enquanto o
 *     formulário rola (escondida em telas < lg) — igual ao CadastroPacienteView
 *
 * Filtros de digitação (cada campo só aceita o que se pede):
 *   - só letras:   nome, órgão emissor
 *   - só números:  data, CPF, celular, CEP (com máscara)
 *   - e-mail:      só caracteres válidos de e-mail
 */

import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import FormField from '@/components/shared/FormField.vue'
import FormTextarea from '@/components/shared/FormTextarea.vue'
import FormButton from '@/components/shared/FormButton.vue'
import heroImage from '@/assets/imagemprofissional.png'

const router = useRouter()

// Caminhos "d" dos ícones (Heroicons 24x24).
// user, calendar, users, id, mail, phone, pin e lock são os mesmos do CadastroPacienteView.
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
  lock: 'M16.5 10.5V6.75a4.5 4.5 0 1 0-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 0 0 2.25-2.25v-6.75a2.25 2.25 0 0 0-2.25-2.25H6.75a2.25 2.25 0 0 0-2.25 2.25v6.75a2.25 2.25 0 0 0 2.25 2.25Z',

  // Só do profissional
  map: 'M9 6.75V15m6-6v8.25m.503 3.498 4.875-2.437c.381-.19.622-.58.622-1.006V4.82c0-.836-.88-1.38-1.628-1.006l-3.869 1.934c-.317.159-.69.159-1.006 0L9.503 3.252a1.125 1.125 0 0 0-1.006 0L3.622 5.689C3.24 5.88 3 6.27 3 6.695V19.18c0 .836.88 1.38 1.628 1.006l3.869-1.934c.317-.159.69-.159 1.006 0l4.994 2.497c.317.158.69.158 1.006 0Z',
  shield:
    'M9 12.75 11.25 15 15 9.75m-3-7.036A11.959 11.959 0 0 1 3.598 6 11.99 11.99 0 0 0 3 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285Z',
  clipboard:
    'M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 0 0 2.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 0 0-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 0 0 .75-.75 2.25 2.25 0 0 0-.1-.664m-5.8 0A2.251 2.251 0 0 1 13.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25ZM6.75 12h.008v.008H6.75V12Zm0 3h.008v.008H6.75V15Zm0 3h.008v.008H6.75V18Z',
}

const INFO_MAX = 500 // limite de caracteres de "Informações Profissionais"

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
  registro: '',
  informacoes: '',
  senha: '',
  confirmarSenha: '',
})
const errors = reactive({})
const carregando = ref(false)

/* ---------- Filtros / máscaras ---------- */

const soNumeros = (v) => v.replace(/\D/g, '')

// Só letras (com acentos) e espaços; sem espaço no início nem espaços duplicados
const soLetras = (v) =>
  v
    .replace(/[^\p{L}\s]/gu, '')
    .replace(/\s{2,}/g, ' ')
    .replace(/^\s/, '')

function mascaraData(v) {
  const n = soNumeros(v).slice(0, 8)
  if (n.length <= 2) return n
  if (n.length <= 4) return `${n.slice(0, 2)}/${n.slice(2)}`
  return `${n.slice(0, 2)}/${n.slice(2, 4)}/${n.slice(4)}`
}

function mascaraCpf(v) {
  const n = soNumeros(v).slice(0, 11)
  if (n.length <= 3) return n
  if (n.length <= 6) return `${n.slice(0, 3)}.${n.slice(3)}`
  if (n.length <= 9) return `${n.slice(0, 3)}.${n.slice(3, 6)}.${n.slice(6)}`
  return `${n.slice(0, 3)}.${n.slice(3, 6)}.${n.slice(6, 9)}-${n.slice(9)}`
}

function mascaraCelular(v) {
  const n = soNumeros(v).slice(0, 11)
  if (n.length === 0) return ''
  if (n.length <= 2) return `(${n}`
  if (n.length <= 7) return `(${n.slice(0, 2)}) ${n.slice(2)}`
  return `(${n.slice(0, 2)}) ${n.slice(2, 7)}-${n.slice(7)}`
}

function mascaraCep(v) {
  const n = soNumeros(v).slice(0, 8)
  return n.length <= 5 ? n : `${n.slice(0, 5)}-${n.slice(5)}`
}

// Só caracteres válidos de e-mail, sem espaços e com um único @
function filtroEmail(v) {
  const limpo = v.replace(/[^a-zA-Z0-9@._+-]/g, '').toLowerCase().slice(0, 100)
  const i = limpo.indexOf('@')
  return i === -1 ? limpo : limpo.slice(0, i + 1) + limpo.slice(i + 1).replace(/@/g, '')
}

const filtros = {
  nome: (v) => soLetras(v).slice(0, 100),
  nascimento: mascaraData,
  genero: (v) => v,
  cpf: mascaraCpf,
  orgaoEmissor: (v) => soLetras(v).slice(0, 30),
  email: filtroEmail,
  celular: mascaraCelular,
  cep: mascaraCep,
  endereco: (v) => v.replace(/^\s/, '').replace(/\s{2,}/g, ' ').slice(0, 150),
  // Registro (ex.: CRM 12345/PI): letras, números, espaço, "/" e "-"
  registro: (v) =>
    v
      .replace(/[^\p{L}\d\s/-]/gu, '')
      .replace(/\s{2,}/g, ' ')
      .replace(/^\s/, '')
      .slice(0, 30),
  informacoes: (v) => v.slice(0, INFO_MAX),
  senha: (v) => v.replace(/\s/g, '').slice(0, 64), // sem espaços
  confirmarSenha: (v) => v.replace(/\s/g, '').slice(0, 64),
}

function atualizar(campo, valor) {
  form[campo] = filtros[campo](valor)
  delete errors[campo]
  if (campo === 'senha') delete errors.confirmarSenha
}

/* ---------- Validação ---------- */

function cpfValido(cpf) {
  const n = soNumeros(cpf)
  if (n.length !== 11 || /^(\d)\1{10}$/.test(n)) return false
  const digito = (base) => {
    let soma = 0
    for (let i = 0; i < base; i++) soma += Number(n[i]) * (base + 1 - i)
    const r = (soma * 10) % 11
    return r === 10 ? 0 : r
  }
  return digito(9) === Number(n[9]) && digito(10) === Number(n[10])
}

// Data DD/MM/AAAA existente, não futura e com idade mínima de 18 anos
function validarNascimento(v) {
  if (v.length !== 10) return 'Informe a data no formato DD/MM/AAAA.'
  const [dia, mes, ano] = v.split('/').map(Number)
  const data = new Date(ano, mes - 1, dia)
  const existe =
    data.getFullYear() === ano && data.getMonth() === mes - 1 && data.getDate() === dia
  if (!existe || ano < 1900) return 'Data de nascimento inválida.'
  const hoje = new Date()
  if (data > hoje) return 'A data não pode ser futura.'
  const maioridade = new Date(ano + 18, mes - 1, dia)
  if (maioridade > hoje) return 'É necessário ter 18 anos ou mais.'
  return ''
}

function validar() {
  const e = {}

  if (form.nome.trim().split(' ').filter(Boolean).length < 2) {
    e.nome = 'Informe seu nome completo.'
  }
  const erroData = validarNascimento(form.nascimento)
  if (erroData) e.nascimento = erroData
  if (!form.genero) e.genero = 'Selecione o gênero.'
  if (!cpfValido(form.cpf)) e.cpf = 'CPF inválido.'
  if (form.orgaoEmissor.trim().length < 2) e.orgaoEmissor = 'Informe o órgão emissor.'
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(form.email)) e.email = 'Informe um e-mail válido.'
  if (soNumeros(form.celular).length !== 11) e.celular = 'Informe o celular com DDD.'
  if (soNumeros(form.cep).length !== 8) e.cep = 'CEP inválido.'
  if (form.endereco.trim().length < 5) e.endereco = 'Informe seu endereço.'
  if (form.registro.trim().length < 3) e.registro = 'Informe seu registro profissional.'
  if (form.senha.length < 8) e.senha = 'A senha deve ter no mínimo 8 caracteres.'
  if (!form.confirmarSenha) e.confirmarSenha = 'Confirme sua senha.'
  else if (form.confirmarSenha !== form.senha) e.confirmarSenha = 'As senhas não conferem.'

  Object.keys(errors).forEach((k) => delete errors[k])
  Object.assign(errors, e)
  return Object.keys(e).length === 0
}

/* ---------- Ações ---------- */

async function criarConta() {
  if (carregando.value) return
  if (!validar()) {
    // Leva o foco até o primeiro campo com erro (o formulário é longo e rola)
    document.querySelector('[aria-invalid="true"]')?.focus()
    return
  }

  carregando.value = true
  try {
    // TODO: enviar o cadastro do profissional para o backend, por exemplo:
    // await authService.cadastrarProfissional({
    //   nome: form.nome.trim(),
    //   nascimento: form.nascimento,
    //   genero: form.genero,
    //   cpf: soNumeros(form.cpf),
    //   orgao_emissor: form.orgaoEmissor.trim(),
    //   email: form.email,
    //   celular: soNumeros(form.celular),
    //   cep: soNumeros(form.cep),
    //   endereco: form.endereco.trim(),
    //   registro_profissional: form.registro.trim(),
    //   informacoes: form.informacoes.trim(),
    //   senha: form.senha,
    // })

    // Enquanto o serviço não está ligado, segue direto para a tela de sucesso.
    // Ao ligar, deixe o push só depois do await (e trate e-mail/CPF já cadastrados).
    router.push({ name: 'cadastro/profissional/sucesso' })
  } finally {
    carregando.value = false
  }
}

function irParaLogin() {
  router.push({ name: 'login/profissional' })
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
              Preencha os dados abaixo para acessar o portal do profissional de saúde.
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
              :icon="icons.users"
              :options="generos"
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
              :icon="icons.map"
              :model-value="form.cep"
              :error="errors.cep"
              @update:model-value="atualizar('cep', $event)"
            />

            <FormField
              label="Endereço"
              variant="outline"
              placeholder="Av. Principal, 45, próx catedral da sé"
              :icon="icons.pin"
              :model-value="form.endereco"
              :error="errors.endereco"
              @update:model-value="atualizar('endereco', $event)"
            />

            <FormField
              label="Registro Profissional"
              variant="outline"
              placeholder="Médico Geriatra"
              :icon="icons.shield"
              :model-value="form.registro"
              :error="errors.registro"
              @update:model-value="atualizar('registro', $event)"
            />

            <FormTextarea
              label="Informações Profissionais"
              placeholder="Suas principais informações profissionais, como formação, tempo de atuação e etc."
              :icon="icons.clipboard"
              :rows="3"
              :maxlength="INFO_MAX"
              :model-value="form.informacoes"
              :error="errors.informacoes"
              @update:model-value="atualizar('informacoes', $event)"
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
          alt="Profissional de saúde em uma teleconsulta com uma paciente"
          class="size-full object-cover object-right"
        />
      </div>
    </aside>
  </main>
</template>