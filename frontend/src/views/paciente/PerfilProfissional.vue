<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppHeader from '@/components/shared/AppHeader.vue'
import BackLink from '@/components/shared/BackLink.vue'
import PerfilProfissionalLayout from '@/layouts/paciente/PerfilProfissionalLayout.vue'

const route = useRoute()
const router = useRouter()

const user = ref({ name: 'Nome Paciente', role: 'Paciente' })

function logout() {
  user.value = null
}

function verAvaliacoes() {
  router.push({
    name: 'avaliacoesDoProfissional',
    params: route.params.id ? { id: route.params.id } : {},
  })
}

function agendar({ data, horario }) {
  // TODO: enviar para a API
  console.log('Agendar consulta:', data, horario)
}
</script>

<template>
  <div class="flex min-h-screen flex-col bg-[#f8faff]">
    <AppHeader :user="user" @logout="logout" />

    <main class="mx-auto flex w-full max-w-300 flex-1 flex-col gap-6 px-12 pb-12">
      <BackLink />
      <PerfilProfissionalLayout @ver-avaliacoes="verAvaliacoes" @agendar="agendar" />
    </main>
  </div>
</template>
