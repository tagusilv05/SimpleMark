<script setup>
import AppHeader from '@/components/shared/AppHeader.vue'
import BackLink from '@/components/shared/BackLink.vue'
import PatientProfileProfissional from '@/layouts/profissional/PatientProfileProfissional.vue'




</script>

<template>
  <div class="flex min-h-screen flex-col bg-[#f8faff]">
    <AppHeader />

    <main class="mx-auto flex w-full max-w-300 flex-1 flex-col gap-6 px-12 pb-12">
      <BackLink />
      <PatientProfileProfissional/>
    </main>
  </div>
</template>