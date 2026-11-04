<script setup>
import { useRoute, useRouter } from 'vue-router'
import AppHeader from '@/components/shared/AppHeader.vue'
import BackLink from '@/components/shared/BackLink.vue'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

async function logout() {
  await auth.logout()
  router.push({ name: 'login/paciente' })
}
</script>

<template>
  <div class="flex min-h-screen flex-col bg-[#f8faff]">
    <AppHeader :user="auth.usuarioHeader" @logout="logout" />

    <main class="mx-auto flex w-full max-w-300 flex-1 flex-col gap-6 px-12 pb-12">
      <BackLink
        v-if="route.meta.voltar"
        :to="route.name === 'meusAgendamentos' ? { name: 'home' } : null"
      />
      <RouterView />
    </main>
  </div>
</template>