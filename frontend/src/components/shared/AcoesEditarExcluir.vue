<script setup>
/**
 * AcoesEditarExcluir — par de ícones (lápis + lixeira) para editar/excluir um item
 *
 * COMO USAR (na página):
 *
 *   import AcoesEditarExcluir from '@/components/shared/AcoesEditarExcluir.vue'
 *
 *   <AcoesEditarExcluir @editar="editando = true" @excluir="remover(item)" />
 *   <AcoesEditarExcluir :editando="editando" @editar="editando = !editando" />
 *
 * PROPS
 *   editando  Boolean (padrão: false)  troca o lápis por um "check" (concluir edição).
 *
 * EVENTOS
 *   @editar   clique no lápis (ou no check).
 *   @excluir  clique na lixeira.
 *
 * DEPENDÊNCIAS
 *   - Tailwind CSS
 */

defineProps({
  editando: { type: Boolean, default: false },
})

defineEmits(['editar', 'excluir'])

const paths = {
  lapis:
    'm16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L6.832 19.82a4.5 4.5 0 0 1-1.897 1.13l-2.685.8.8-2.685a4.5 4.5 0 0 1 1.13-1.897L16.863 4.487Z',
  check: 'm4.5 12.75 6 6 9-13.5',
  lixeira:
    'm14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0',
}
</script>

<template>
  <div class="flex shrink-0 items-center gap-2 text-gray-700">
    <button
      type="button"
      class="cursor-pointer rounded p-1 transition-colors hover:text-[#0a9ba5]"
      :aria-label="editando ? 'Concluir edição' : 'Editar'"
      @click="$emit('editar')"
    >
      <svg class="size-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" aria-hidden="true">
        <path stroke-linecap="round" stroke-linejoin="round" :d="editando ? paths.check : paths.lapis" />
      </svg>
    </button>
    <button
      type="button"
      class="cursor-pointer rounded p-1 transition-colors hover:text-red-700"
      aria-label="Excluir"
      @click="$emit('excluir')"
    >
      <svg class="size-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" aria-hidden="true">
        <path stroke-linecap="round" stroke-linejoin="round" :d="paths.lixeira" />
      </svg>
    </button>
  </div>
</template>
