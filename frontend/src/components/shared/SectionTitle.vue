<script setup>
/**
 * SectionTitle — título de seção com subtítulo opcional
 *
 * COMO USAR (na página):
 *
 *   import SectionTitle from '@/components/shared/SectionTitle.vue'
 *
 *   <SectionTitle title="Médicos Mais Avaliados"
 *                 subtitle="Profissionais reconhecidos pela excelência no atendimento" />
 *   <SectionTitle title="Só o título" />
 *
 * PROPS
 *   title     String  (obrigatória)  texto principal (renderizado como <h2>).
 *   subtitle  String  (padrão: '')   linha de apoio abaixo do título. Vazio = não aparece.
 *
 * DEPENDÊNCIAS
 *   - Tailwind CSS
 */

defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
})
</script>

<template>
  <div class="flex flex-col gap-1.5">
    <h2 class="text-xl font-bold text-[#0b2f5b]">{{ title }}</h2>
    <p v-if="subtitle" class="text-sm text-gray-500">{{ subtitle }}</p>
  </div>
</template>
