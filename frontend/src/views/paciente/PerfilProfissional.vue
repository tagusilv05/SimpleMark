<script setup>
import { useRoute, useRouter } from 'vue-router'
import AppHeader from '@/components/shared/AppHeader.vue'
import BackLink from '@/components/shared/BackLink.vue'
import PerfilProfissionalLayout from '@/layouts/paciente/PerfilProfissionalLayout.vue'

const route = useRoute()
const router = useRouter()

function verAvaliacoes(idProfissional) {
  const id = idProfissional || route.params.id
  router.push({
    name: 'avaliacoesDoProfissional',
    params: id ? { id } : {},
  })
}
</script>

<template>
  <div class="flex min-h-screen flex-col bg-[#f8faff]">
    <AppHeader />

    <main class="mx-auto flex w-full max-w-300 flex-1 flex-col gap-6 px-12 pb-12">
      <BackLink />
      <PerfilProfissionalLayout
        :id="route.params.id"
        @ver-avaliacoes="verAvaliacoes"
      />
    </main>
  </div>
</template>
