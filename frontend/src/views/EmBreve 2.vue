<script setup>
// Página provisória para rotas cujas telas ainda não foram implementadas.
import AppHeader from '@/components/shared/AppHeader.vue'
import AppFooter from '@/components/shared/AppFooter.vue'
</script>

<template>
  <div class="flex min-h-screen flex-col bg-[#f8faff]">
    <AppHeader />

    <main class="flex flex-1 flex-col items-center justify-center gap-4 px-12 py-20 text-center">
      <h1 class="text-2xl font-bold text-[#0b2f5b]">Em breve</h1>
      <p class="text-sm text-gray-500">Esta página ainda está em construção.</p>
      <RouterLink
        to="/"
        class="inline-flex h-11 items-center rounded-lg bg-[#042d5c] px-6 text-sm font-semibold text-white transition-colors hover:bg-[#0b3f7a]"
      >
        Voltar para o início
      </RouterLink>
    </main>

    <AppFooter />
  </div>
</template>
