<script setup>
/**
 * SpecialtyChip — botão-cartão com o nome de uma especialidade
 *
 * COMO USAR (na página):
 *
 *   import SpecialtyChip from '@/components/shared/SpecialtyChip.vue'
 *
 *   <SpecialtyChip label="Cardiologia" @click="buscar(esp)" />
 *
 *   <div class="grid grid-cols-2 gap-4 md:grid-cols-6">
 *     <SpecialtyChip v-for="e in especialidades" :key="e.id_especialidade"
 *                    :label="e.especialidade" @click="buscar(e)" />
 *   </div>
 *
 * PROPS
 *   label  String  (obrigatória)  nome exibido no cartão.
 *
 * EVENTOS
 *   Nenhum declarado: como o <button> é o único elemento raiz, @click cai direto nele.
 *
 * DEPENDÊNCIAS
 *   - Tailwind CSS
 */

defineProps({
  label: { type: String, required: true },
})
</script>

<template>
  <button
    type="button"
    class="flex h-11 w-full cursor-pointer items-center justify-center truncate rounded-lg border border-gray-200 bg-white px-3 text-xs font-semibold text-gray-900 transition hover:border-[#0a9ba5] hover:text-[#0b2f5b] hover:shadow-[0_2px_8px_rgba(11,47,91,0.10)] focus-visible:outline-2 focus-visible:outline-[#0a9ba5]"
  >
    {{ label }}
  </button>
</template>
