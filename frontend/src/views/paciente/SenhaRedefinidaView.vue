<script setup>
/**
 * SenhaRedefinidaView — passo 3 da recuperação de senha: confirmação
 *
 * Fluxo: Redefinir Senha -> Redefinir Senha (botão) -> esta tela (rota `senha-redefinida`)
 * -> Retornar ao login.
 *
 * Estrutura:
 *   - Coluna esquerda: logo + cartão de confirmação
 *   - Coluna direita: imagem ilustrativa (escondida em telas < lg)
 */

import { useRouter } from 'vue-router'
import FormButton from '@/components/shared/FormButton.vue'
import heroImage from '@/assets/imagempaciente.jpg'

const router = useRouter()

// Ícone "check-circle" (Heroicons 24x24)
const iconeCheck = 'M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z'

function voltarAoLogin() {
  router.push({ name: 'login/paciente' })
}
</script>

<template>
  <main class="grid min-h-screen bg-[#fafaff] lg:grid-cols-[minmax(0,42fr)_minmax(0,58fr)]">
    <!-- Coluna do conteúdo -->
    <section class="flex flex-col px-6 pt-6 sm:px-10 lg:pt-8">
      <img
        src="/LOGO%20OFICIAL%20SEM%20FUNDO.png"
        alt="Simple Mark"
        class="h-36 w-auto self-start"
      />

      <!-- cartão logo abaixo da logo (distância fixa), em vez de centralizado na altura da tela -->
      <div class="mb-auto mt-8 w-full max-w-117.75 lg:ml-16 lg:mt-16">
        <div
          class="rounded-xl bg-[#cdf7e8] px-6 pb-8 pt-10 sm:px-13"
          role="status"
          aria-live="polite"
        >
          <h1 class="text-center text-2xl font-medium text-[#00507a]">
            Senha Redefinida Com Sucesso!
          </h1>

          <div class="mt-9 flex justify-center">
            <svg
              class="size-24 text-[#00436b]"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke-width="1.5"
              stroke="currentColor"
              aria-hidden="true"
            >
              <path stroke-linecap="round" stroke-linejoin="round" :d="iconeCheck" />
            </svg>
          </div>

          <FormButton class="mt-6 h-13! w-full" @click="voltarAoLogin">
            Retornar ao login
          </FormButton>
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