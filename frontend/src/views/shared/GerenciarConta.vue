<script setup>
import { ref, computed } from 'vue'
import AppHeader from '@/components/shared/AppHeader.vue'
import BackLink from '@/components/shared/BackLink.vue'
import PerfilConta from '@/layouts/shared/PerfilConta.vue'

// 'paciente' | 'profissional' (vem da rota)
const props = defineProps({
  role: {
    type: String,
    default: 'paciente',
  },
})

const user = ref({
  name: props.role === 'profissional' ? 'Nome Profissional' : 'Nome Paciente',
  role: props.role === 'profissional' ? 'Profissional' : 'Paciente',
})

function logout() {
  user.value = null
}
</script>

<template>
  <div class="flex min-h-screen flex-col bg-[#f8faff]">
    <AppHeader :user="user" @logout="logout" />

    <main class="mx-auto flex w-full max-w-300 flex-1 flex-col gap-6 px-12 pb-12">
      <BackLink />
      <PerfilConta :role="role" />
    </main>
  </div>
</template>
