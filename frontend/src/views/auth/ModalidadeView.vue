<script setup>
/**
 * ModalidadeView — escolha da modalidade de login
 *
 * Tela exibida ao clicar em "Entrar" na home (rota /login). A pessoa escolhe se
 * entra como paciente, profissional de saúde ou administrador e segue para o
 * login correspondente.
 *
 * Estrutura:
 *   - Coluna esquerda: logo + cartão com os botões de modalidade
 *   - Coluna direita: imagem ilustrativa (escondida em telas < lg)
 */

import { useRouter } from 'vue-router'
import FormButton from '@/components/shared/FormButton.vue'
import heroImage from '@/assets/imagemprofissional.png'

const router = useRouter()

// `rota` é o name da rota no router (src/router/index.js)
const modalidades = [
  { label: 'Paciente', rota: 'login/paciente' },
  { label: 'Profissional de Saúde', rota: 'login/profissional' },
  { label: 'Administrador', rota: 'login/administrador' },
]

function escolher(rota) {
  router.push({ name: rota })
}
</script>

<template>
  <main class="grid min-h-screen bg-[#fafaff] lg:grid-cols-[minmax(0,45fr)_minmax(0,55fr)]">
    <!-- Coluna do conteúdo -->
    <section class="flex flex-col px-6 py-6 sm:px-10 lg:py-8">
      <img
        src="/LOGO%20OFICIAL%20SEM%20FUNDO.png"
        alt="Simple Mark"
        class="h-36 w-auto self-start"
      />

      <div class="mb-auto mt-8 w-full max-w-111.75 lg:ml-16 lg:mt-12">
        <div class="rounded-2xl border border-gray-200 bg-white p-6 sm:p-10">
          <header>
            <h1 class="text-2xl font-medium text-[#00507a]">Escolha sua modalidade para login:</h1>
            <p class="mt-3 text-[15px] leading-6 text-gray-700">
              Bem-vindo à área de login da Simple Mark, selecione sua modalidade para seguir no
              login.
            </p>
          </header>

          <nav class="mt-8 flex flex-col gap-8" aria-label="Modalidades de login">
            <FormButton
              v-for="m in modalidades"
              :key="m.rota"
              class="h-13! w-full"
              @click="escolher(m.rota)"
            >
              {{ m.label }}
            </FormButton>
          </nav>
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