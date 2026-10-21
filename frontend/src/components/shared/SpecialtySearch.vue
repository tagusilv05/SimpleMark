<script setup>
/**
 * SpecialtySearch — cartão de busca por especialidade (pílula "Teleconsulta" + lista + Pesquisar)
 *
 * COMO USAR (na página):
 *
 *   import SpecialtySearch from '@/components/shared/SpecialtySearch.vue'
 *
 *   <SpecialtySearch
 *     :options="especialidades"
 *     :loading="carregando"
 *     @search="(idEspecialidade) => router.push({ name: 'busca-profissionais', query: { id_especialidade: idEspecialidade } })"
 *   />
 *
 * PROPS
 *   options  Array  (padrão: [])
 *              lista de { id_especialidade, especialidade } (formato do backend).
 *   loading  Boolean  (padrão: false)
 *              enquanto true, a lista fica desabilitada com "Carregando...".
 *
 * EVENTOS
 *   @search  disparado ao clicar em "Pesquisar" (ou dar Enter), com o id da especialidade
 *            escolhida (Number) ou null se o usuário não escolheu nenhuma
 *            (nesse caso o pai pode buscar todas).
 *
 * DEPENDÊNCIAS
 *   - @/components/shared/FormButton.vue
 *   - Tailwind CSS
 */

import { computed, ref, useId } from 'vue'
import FormButton from '@/components/shared/FormButton.vue'

const props = defineProps({
  options: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['search'])

const id = useId()
const selected = ref('')

const placeholder = computed(() => (props.loading ? 'Carregando...' : 'Escolher especialidade'))

function submit() {
  emit('search', selected.value === '' ? null : Number(selected.value))
}

const paths = {
  video: 'M4.5 4.5a3 3 0 0 0-3 3v9a3 3 0 0 0 3 3h8.25a3 3 0 0 0 3-3v-9a3 3 0 0 0-3-3H4.5ZM19.94 18.75l-2.69-2.69V7.94l2.69-2.69c.944-.945 2.56-.276 2.56 1.06v11.38c0 1.336-1.616 2.005-2.56 1.06Z',
  search: 'm21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z',
  chevron: 'm19.5 8.25-7.5 7.5-7.5-7.5',
}
</script>

<template>
  <form
    class="flex w-full max-w-xl flex-col gap-3 rounded-xl bg-white p-3.5 shadow-[0_4px_20px_rgba(11,47,91,0.10)]"
    @submit.prevent="submit"
  >
    <!-- Modalidade (hoje só teleconsulta) -->
    <span
      class="inline-flex w-fit items-center gap-1.5 rounded-full bg-[#3f9aa6] px-3 py-1 text-[11px] font-semibold text-white"
    >
      <svg class="size-3.5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
        <path :d="paths.video" />
      </svg>
      Teleconsulta
    </span>

    <div class="flex flex-col gap-2 sm:flex-row">
      <div class="relative flex-1">
        <svg
          class="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-gray-500"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke-width="2"
          stroke="currentColor"
          aria-hidden="true"
        >
          <path stroke-linecap="round" stroke-linejoin="round" :d="paths.search" />
        </svg>

        <label :for="id" class="sr-only">Especialidade</label>
        <select
          :id="id"
          v-model="selected"
          :disabled="loading"
          class="h-10 w-full cursor-pointer appearance-none rounded-lg border border-gray-200 bg-white pl-9 pr-9 text-xs text-gray-700 outline-none transition focus:ring-2 focus:ring-[#0a9ba5] disabled:cursor-wait disabled:text-gray-400"
        >
          <option value="">{{ placeholder }}</option>
          <option v-for="o in options" :key="o.id_especialidade" :value="o.id_especialidade">
            {{ o.especialidade }}
          </option>
        </select>

        <svg
          class="pointer-events-none absolute right-3 top-1/2 size-3.5 -translate-y-1/2 text-gray-500"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke-width="2.5"
          stroke="currentColor"
          aria-hidden="true"
        >
          <path stroke-linecap="round" stroke-linejoin="round" :d="paths.chevron" />
        </svg>
      </div>

      <FormButton type="submit" :icon="paths.search" class="h-10! sm:px-8!">Pesquisar</FormButton>
    </div>
  </form>
</template>
