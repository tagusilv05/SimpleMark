<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import AppHeader from '@/components/shared/AppHeader.vue'
import BackLink from '@/components/shared/BackLink.vue'
import PatientProfileProfissional from '@/layouts/profissional/PatientProfileProfissional.vue'

const router = useRouter()

const user = ref({ name: 'Nome Paciente', role: 'Paciente' })

function logout() {
  user.value = null
}

</script>

<template>
  <div class="flex min-h-screen flex-col bg-[#f8faff]">
    <AppHeader :user="user" @logout="logout" />

    <main class="mx-auto flex w-full max-w-300 flex-1 flex-col gap-6 px-12 pb-12">
      <BackLink />
      <PatientProfileProfissional/>
    </main>
  </div>
</template>