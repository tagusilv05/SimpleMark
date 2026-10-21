<script setup>
/**
 * SpecialtyItem — linha de uma especialidade ativa com valor da consulta e ações
 *
 * COMO USAR (na página):
 *
 *   import SpecialtyItem from '@/components/profissional/SpecialtyItem.vue'
 *
 *   <SpecialtyItem
 *     name="Cardiologia Clínica"
 *     registration="CRM 12345-SP"
 *     v-model="especialidade.price"
 *     @edit="editar(especialidade)"
 *     @remove="remover(especialidade.id)"
 *   />
 *
 *   <SpecialtyItem name="Pediatria" registration="CRM 999-PI" v-model="valor" />
 *
 * PROPS
 *   name          String  (obrigatória)  nome da especialidade.
 *   registration  String  (padrão: '')   registro no conselho (ex.: 'CRM 12345-SP').
 *   modelValue    String | Number  (padrão: '')
 *                   valor da consulta. Use com v-model.
 *
 * EDIÇÃO
 *   O campo de valor começa travado (somente leitura). Ao clicar em "Editar" ele é
 *   liberado e recebe o foco; o botão vira "Salvar". Ao clicar em "Salvar" o campo
 *   trava de novo. O valor já é enviado ao pai a cada digitação (v-model), então
 *   "Salvar" só encerra a edição e avisa com o evento `save`.
 *
 * EVENTOS
 *   update:modelValue   novo valor digitado (faz o v-model funcionar).
 *   edit                usuário clicou em "Editar" (campo liberado).
 *   save                usuário clicou em "Salvar" (edição encerrada); use para
 *                       gravar na API se quiser.
 *   remove              clique em "Excluir". O componente não pede confirmação:
 *                       faça isso na página.
 *
 * ESTILO
 *   Tailwind. Cartão azul claro: ícone de estetoscópio à esquerda, nome e registro
 *   no meio, campo de valor (caixa branca) e botões Editar / Excluir à direita.
 *   Quebra de linha em telas pequenas.
 *
 * DEPENDÊNCIAS
 *   - FormField (variant, size, input-class e label-class) e FormButton (variants 'outline'
 *     e 'outline-danger'), ambos em shared
 *   - Tailwind CSS
 */
import { nextTick, ref } from 'vue'
import FormField from '@/components/shared/FormField.vue'
import FormButton from '@/components/shared/FormButton.vue'

defineProps({
  name: { type: String, required: true },
  registration: { type: String, default: '' },
  modelValue: { type: [String, Number], default: '' },
})

const emit = defineEmits(['update:modelValue', 'edit', 'save', 'remove'])

// Campo de valor travado até clicar em "Editar"
const editing = ref(false)
const root = ref(null)

async function toggleEdit() {
  if (editing.value) {
    editing.value = false
    emit('save')
    return
  }
  editing.value = true
  emit('edit')
  await nextTick()
  root.value?.querySelector('input')?.focus()
}

// Ícones (caminhos "d" de SVG 24x24) usados nos botões
const checkIcon = 'm4.5 12.75 6 6 9-13.5'
const pencilIcon =
  'm16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125'
const trashIcon =
  'm14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0'
</script>

<template>
  <div ref="root" class="flex flex-wrap items-center gap-4 rounded-2xl bg-[#eef1fe] p-5">
    <!-- Ícone de estetoscópio -->
    <div class="flex size-12 shrink-0 items-center justify-center rounded-xl bg-[#042d5c] text-white">
      <svg
        class="size-6"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        stroke-width="2"
        stroke="currentColor"
        stroke-linecap="round"
        stroke-linejoin="round"
        aria-hidden="true"
      >
        <path d="M11 2v2" />
        <path d="M5 2v2" />
        <path d="M5 3H4a2 2 0 0 0-2 2v4a6 6 0 0 0 12 0V5a2 2 0 0 0-2-2h-1" />
        <path d="M8 15a6 6 0 0 0 12 0v-3" />
        <circle cx="20" cy="10" r="2" />
      </svg>
    </div>

    <!-- Nome + registro -->
    <div class="min-w-44 flex-1">
      <p class="text-lg font-bold text-[#0b2f5b]">{{ name }}</p>
      <div class="mt-1 flex flex-wrap items-center gap-x-4 gap-y-1">
        <span
          v-if="registration"
          class="inline-flex items-center gap-1.5 text-sm font-semibold text-gray-600"
        >
          <span class="size-1.5 shrink-0 rounded-full bg-gray-400" aria-hidden="true"></span>
          {{ registration }}
        </span>
      </div>
    </div>

    <!-- Valor da consulta -->
    <div class="w-40">
      <FormField
        label="Valor da consulta"
        label-class="text-xs font-semibold uppercase tracking-wide text-gray-500"
        variant="white"
        size="sm"
        :readonly="!editing"
        input-class="text-base font-bold"
        placeholder="R$ 0,00"
        :model-value="modelValue"
        @update:model-value="$emit('update:modelValue', $event)"
      />
    </div>

    <!-- Ações -->
    <div class="flex items-center gap-2 self-end">
      <FormButton variant="outline" :icon="editing ? checkIcon : pencilIcon" @click="toggleEdit">
        {{ editing ? 'Salvar' : 'Editar' }}
      </FormButton>
      <FormButton variant="outline-danger" :icon="trashIcon" @click="emit('remove')">Excluir</FormButton>
    </div>
  </div>
</template>