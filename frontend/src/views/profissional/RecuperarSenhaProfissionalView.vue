<script setup>
/**
 * RecuperarSenhaProfissionalView — passo 1 da recuperação de senha do profissional: informar o e-mail
 *
 * Fluxo: login do profissional -> Esqueceu a senha? -> esta tela (rota `login/profissional/recuperarsenha`)
 *        -> Enviar Código -> Redefinir Senha (rota `login/profissional/redefinirsenha`)
 *
 * Estrutura:
 *   - Coluna esquerda: logo + cartão com o formulário
 *   - Coluna direita: imagem ilustrativa (escondida em telas < lg)
 */

import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import FormField from '@/components/shared/FormField.vue'
import FormButton from '@/components/shared/FormButton.vue'
import heroImage from '@/assets/imagemprofissional.png'

const router = useRouter()

const mailIcon =
  'M21.75 6.75v10.5a2.25 2.25 0 0 1-2.25 2.25h-15a2.25 2.25 0 0 1-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0 0 19.5 4.5h-15a2.25 2.25 0 0 0-2.25 2.25m19.5 0v.243a2.25 2.25 0 0 1-1.07 1.916l-7.5 4.615a2.25 2.25 0 0 1-2.36 0L3.32 8.91a2.25 2.25 0 0 1-1.07-1.916V6.75'

const form = reactive({ email: '' })
const errors = reactive({})
const carregando = ref(false)

// Só caracteres válidos de e-mail, sem espaços e com um único @
function filtrarEmail(valor) {
  const limpo = valor.replace(/[^a-zA-Z0-9@._+-]/g, '').toLowerCase().slice(0, 100)
  const i = limpo.indexOf('@')
  return i === -1 ? limpo : limpo.slice(0, i + 1) + limpo.slice(i + 1).replace(/@/g, '')
}

function atualizarEmail(valor) {
  form.email = filtrarEmail(valor)
  delete errors.email
}

function validar() {
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(form.email)) {
    errors.email = 'Informe um e-mail válido.'
    return false
  }
  return true
}

async function enviarCodigo() {
  if (carregando.value || !validar()) return
  carregando.value = true
  try {
    // TODO: chamar o serviço de recuperação de senha do profissional
    // await authService.solicitarCodigoProfissional({ email: form.email })

    // Segue para a tela de redefinição (leva o e-mail para a próxima etapa)
    await router.push({ name: 'login/profissional/redefinirsenha', query: { email: form.email } })
  } catch {
    errors.email = 'Não foi possível enviar o código. Tente novamente.'
  } finally {
    carregando.value = false
  }
}

function voltarAoLogin() {
  router.push({ name: 'login/profissional' })
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
            <h1 class="text-2xl font-medium text-[#00507a]">Recuperar Senha</h1>
            <p class="mt-2 text-[15px] leading-6 text-gray-700">
              Informe seu e-mail para receber um código para recuperação de sua senha.
            </p>
          </header>

          <form class="flex flex-col gap-6" novalidate @submit.prevent="enviarCodigo">
            <FormField
              label="E-mail"
              type="email"
              variant="outline"
              inputmode="email"
              placeholder="seu@email.com"
              :icon="mailIcon"
              :model-value="form.email"
              :error="errors.email"
              @update:model-value="atualizarEmail"
            />

            <FormButton type="submit" class="h-13! w-full" :disabled="carregando">
              Enviar Código
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
        alt="Profissional de saúde em uma teleconsulta com uma paciente"
        class="absolute inset-0 size-full object-cover object-right"
      />
    </aside>
  </main>
</template>