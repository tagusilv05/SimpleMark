<script setup>
/**
 * LoginView — tela de login do Portal do Profissional
 *
 * Estrutura:
 *   - Coluna esquerda: logo + cartão com o formulário de acesso
 *   - Coluna direita: imagem ilustrativa (escondida em telas < lg)
 *
 * Componentes usados:
 *   - FormField  (e-mail e senha)
 *   - FormButton (Entrar e Cadastre-se agora
 */

import { reactive, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import FormField from '@/components/shared/FormField.vue'
import FormButton from '@/components/shared/FormButton.vue'
import heroImage from '@/assets/imagemprofissional.png'

const router = useRouter()

const form = reactive({
  email: '',
  senha: '',
  lembrar: false,
})

const carregando = ref(false)

// Caminhos "d" dos ícones (Heroicons 24x24)
const icons = {
  mail: 'M21.75 6.75v10.5a2.25 2.25 0 0 1-2.25 2.25h-15a2.25 2.25 0 0 1-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0 0 19.5 4.5h-15a2.25 2.25 0 0 0-2.25 2.25m19.5 0v.243a2.25 2.25 0 0 1-1.07 1.916l-7.5 4.615a2.25 2.25 0 0 1-2.36 0L3.32 8.91a2.25 2.25 0 0 1-1.07-1.916V6.75',
  lock: 'M16.5 10.5V6.75a4.5 4.5 0 1 0-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 0 0 2.25-2.25v-6.75a2.25 2.25 0 0 0-2.25-2.25H6.75a2.25 2.25 0 0 0-2.25 2.25v6.75a2.25 2.25 0 0 0 2.25 2.25Z',
  login: 'M15.75 9V5.25A2.25 2.25 0 0 0 13.5 3h-6a2.25 2.25 0 0 0-2.25 2.25v13.5A2.25 2.25 0 0 0 7.5 21h6a2.25 2.25 0 0 0 2.25-2.25V15m3 0 3-3m0 0-3-3m3 3H9',
}

async function entrar() {
  if (carregando.value) return
  carregando.value = true
  try {
    // TODO: chamar o serviço de autenticação
    // await authService.login({ email: form.email, senha: form.senha, lembrar: form.lembrar })
    // router.push({ name: 'dashboard' })
  } finally {
    carregando.value = false
  }
}

function irParaCadastro() {
  router.push({ name: 'cadastro/profissional' })
}
</script>

<template>
  <main class="grid min-h-screen bg-[#fafaff] lg:grid-cols-[minmax(0,45fr)_minmax(0,55fr)]">
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
            <h1 class="text-2xl font-medium text-[#00507a]">Acesse sua conta</h1>
            <p class="mt-2 text-[15px] text-gray-700">Bem-vindo ao Portal do Profissional</p>
          </header>

          <form class="flex flex-col gap-6" @submit.prevent="entrar">
            <FormField
              v-model="form.email"
              label="E-mail"
              type="email"
              placeholder="seu@email.com"
              :icon="icons.mail"
            />

            <FormField
              v-model="form.senha"
              label="Senha"
              type="password"
              placeholder="Digite sua senha"
              :icon="icons.lock"
            />

            <div class="flex items-center justify-between gap-4">
              <label class="flex cursor-pointer items-center gap-2 text-sm font-medium text-gray-700">
                <input
                  v-model="form.lembrar"
                  type="checkbox"
                  class="size-4 cursor-pointer rounded border-gray-300 accent-[#042d5c]"
                />
                Lembrar de mim
              </label>

              <RouterLink
                :to="{ name: 'login/profissional/recuperarsenha' }"
                class="text-sm font-bold text-[#042d5c] hover:underline"
              >
                Esqueceu a senha?
              </RouterLink>
            </div>

            <FormButton type="submit" class="w-full" :disabled="carregando">
              Entrar
              <svg
                class="size-5"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke-width="2"
                stroke="currentColor"
                aria-hidden="true"
              >
                <path stroke-linecap="round" stroke-linejoin="round" :d="icons.login" />
              </svg>
            </FormButton>
          </form>

          <div class="mt-8 flex flex-col items-center gap-4 border-t border-gray-200 pt-8">
            <p class="text-[15px] text-gray-700">Ainda não tem uma conta?</p>
            <FormButton
              variant="text"
              class="border-2 border-[#042d5c] bg-white"
              @click="irParaCadastro"
            >
              Cadastre-se agora
            </FormButton>
          </div>
        </div>
      </div>
    </section>

    <!-- Coluna da imagem (somente desktop) -->
    <aside class="relative hidden overflow-hidden lg:block">
      <img
        :src="heroImage"
        alt="Profissional de saúde realizando uma teleconsulta"
        class="absolute inset-0 size-full object-cover object-right"
      />
    </aside>
  </main>
</template>