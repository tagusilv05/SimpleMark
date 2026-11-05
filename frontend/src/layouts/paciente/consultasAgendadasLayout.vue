<script setup>
import { useRoute } from 'vue-router'
import AppHeader from '@/components/shared/AppHeader.vue'
import BackLink from '@/components/shared/BackLink.vue'

const route = useRoute()

</script>

<template>
  <div class="flex min-h-screen flex-col bg-[#f8faff]">
    <AppHeader />

    <main class="mx-auto flex w-full max-w-300 flex-1 flex-col gap-6 px-12 pb-12">
      <BackLink
        v-if="route.meta.voltar"
        :to="route.name === 'meusAgendamentos' ? { name: 'home' } : null"
      />
      <RouterView />
    </main>
  </div>
</template>