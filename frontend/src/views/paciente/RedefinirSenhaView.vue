<script setup>
/**
 * RedefinirSenhaView — passo 2 da recuperação de senha: código + nova senha
 *
 * Fluxo: Recuperar Senha -> Enviar Código -> esta tela (rota `redefinir-senha`)
 *        -> Redefinir Senha -> confirmação (rota `senha-redefinida`)
 *
 * O e-mail informado no passo anterior chega em `history.state.email`
 * (enviado pelo router.push da tela de recuperação).
 *
 * Estrutura:
 *   - Coluna esquerda: logo + cartão com o formulário
 *   - Coluna direita: imagem ilustrativa (escondida em telas < lg)
 */

import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import FormField from '@/components/shared/FormField.vue'
import FormButton from '@/components/shared/FormButton.vue'
import heroImage from '@/assets/imagempaciente.jpg'

const router = useRouter()

const lockIcon =
  'M16.5 10.5V6.75a4.5 4.5 0 1 0-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 0 0 2.25-2.25v-6.75a2.25 2.25 0 0 0-2.25-2.25H6.75a2.25 2.25 0 0 0-2.25 2.25v6.75a2.25 2.25 0 0 0 2.25 2.25Z'

const keyIcon =
  'M15.75 5.25a3 3 0 0 1 3 3m3 0a6 6 0 0 1-7.029 5.912c-.563-.097-1.159.026-1.563.43L10.5 17.25H8.25v2.25H6v2.25H2.25v-2.818c0-.597.237-1.17.659-1.591l6.499-6.499c.404-.404.527-1 .43-1.563A6 6 0 1 1 21.75 8.25Z'

  const CODIGO_TAMANHO = 6

const form = reactive({ codigo: '', senha: '', confirmarSenha: '' })
const errors = reactive({})
const carregando = ref(false)

// Cada campo só aceita o que se pede
const filtros = {
  codigo: (v) => v.replace(/\D/g, '').slice(0, CODIGO_TAMANHO), // só números
  senha: (v) => v.replace(/\s/g, '').slice(0, 64), // sem espaços
  confirmarSenha: (v) => v.replace(/\s/g, '').slice(0, 64),
}

function atualizar(campo, valor) {
  form[campo] = filtros[campo](valor)
  delete errors[campo]
  if (campo === 'senha') delete errors.confirmarSenha
}

function validar() {
  const e = {}

  if (form.codigo.length !== CODIGO_TAMANHO) e.codigo = `O código tem ${CODIGO_TAMANHO} dígitos.`
  if (form.senha.length < 8) e.senha = 'A senha deve ter no mínimo 8 caracteres.'
  if (form.confirmarSenha !== form.senha) e.confirmarSenha = 'As senhas não conferem.'

  Object.keys(errors).forEach((k) => delete errors[k])
  Object.assign(errors, e)
  return Object.keys(e).length === 0
}

async function redefinirSenha() {
  if (carregando.value || !validar()) return

  carregando.value = true
  try {
    // TODO: confirmar o código e gravar a nova senha no backend
    // const email = history.state?.email
    // await authService.redefinirSenha({ email, codigo: form.codigo, nova_senha: form.senha })

    // Enquanto o serviço não está ligado, segue direto para a confirmação.
    // Ao ligar, deixe o push só depois do await (e trate código inválido/expirado).
    router.push({ name: 'login/paciente/sucessoredefinirsenha' })   // <- só esta linha muda
  } finally {
    carregando.value = false
  }
}

function voltarAoLogin() {
  router.push({ name: 'login/paciente' })
}
</script>

<template>
  <main class="grid min-h-screen bg-[#fafaff] lg:grid-cols-[minmax(0,43fr)_minmax(0,57fr)]">
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
            <h1 class="text-2xl font-medium text-[#00507a]">Redefinir Senha</h1>
            <p class="mt-2 text-[15px] leading-6 text-gray-700">
              Crie uma nova senha para voltar a ter acesso aos nossos serviços na palma de sua mão.
            </p>
          </header>

          <form class="flex flex-col gap-6" novalidate @submit.prevent="redefinirSenha">
            <FormField
              label="Código de Recuperação"
              variant="outline"
              inputmode="numeric"
              placeholder="000000"
              :icon="keyIcon"  
              :model-value="form.codigo"
              :error="errors.codigo"
              @update:model-value="atualizar('codigo', $event)"
            />

            <FormField
              label="Nova Senha"
              type="password"
              variant="outline"
              placeholder="••••••••"
              :icon="lockIcon"
              :model-value="form.senha"
              :error="errors.senha"
              @update:model-value="atualizar('senha', $event)"
            />

            <FormField
              label="Confirmar Nova Senha"
              type="password"
              variant="outline"
              placeholder="••••••••"
              :icon="lockIcon"
              :model-value="form.confirmarSenha"
              :error="errors.confirmarSenha"
              @update:model-value="atualizar('confirmarSenha', $event)"
            />

            <FormButton type="submit" class="h-13! w-full" :disabled="carregando">
              Redefinir Senha
            </FormButton>
          </form>

          <div class="mt-8 flex flex-col items-center gap-4 border-t border-gray-200 pt-8">
            <p class="text-[15px] text-gray-700">Lembrou sua senha?</p>
            <FormButton
              variant="text"
              class="border-2 border-[#042d5c] bg-white"
              @click="voltarAoLogin"
            >
              Voltar para o Login
            </FormButton>
          </div>
        </div>
      </div>
    </section>

    <!-- Coluna da imagem (somente desktop) -->
    <aside class="relative hidden overflow-hidden lg:block">
      <img
        :src="heroImage"
        alt="Paciente em uma teleconsulta com um médico"
        class="absolute inset-0 size-full object-cover object-right"
      />
    </aside>
  </main>
</template>