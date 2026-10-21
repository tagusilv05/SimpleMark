<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/services/api' // ajuste para a sua instância axios
import AppHeader from '@/components/shared/AppHeader.vue'
import BackLink from '@/components/shared/BackLink.vue'

const route = useRoute()

const user = ref({ name: '', role: 'Profissional' })

onMounted(async () => {
  try {
    const { data } = await api.get('/profissionais/me')
    user.value = { name: data.nome, role: 'Profissional' }
  } catch (e) {
    console.error(e)
  }
})

function logout() {
  // TODO: limpar o token e redirecionar para o login
  user.value = null
}
</script>

<template>
  <div class="flex min-h-screen flex-col bg-[#f8faff]">
    <AppHeader :user="user" @logout="logout" />

    <main class="mx-auto flex w-full max-w-300 flex-1 flex-col gap-6 px-12 pb-12">
      <BackLink v-if="route.meta.voltar" />
      <RouterView />
    </main>
  </div>
</template>