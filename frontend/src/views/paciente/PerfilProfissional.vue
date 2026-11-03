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

function verAvaliacoes(idProfissional) {
  const id = idProfissional || route.params.id
  router.push({
    name: 'avaliacoesDoProfissional',
    params: id ? { id } : {},
  })
}

// A escolha de dia e horário é finalizada na tela de Agendamento, com a agenda real do profissional
function agendar(dados) {
  const id = dados?.idProfissional || route.params.id
  router.push({
    name: 'agendamento',
    query: id ? { profissional: id } : {},
  })
}
</script>

<template>
  <div class="flex min-h-screen flex-col bg-[#f8faff]">
    <AppHeader :user="user" @logout="logout" />

    <main class="mx-auto flex w-full max-w-300 flex-1 flex-col gap-6 px-12 pb-12">
      <BackLink />
      <PerfilProfissionalLayout
        :id="route.params.id"
        @ver-avaliacoes="verAvaliacoes"
        @agendar="agendar"
      />
    </main>
  </div>
</template>
