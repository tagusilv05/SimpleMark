<script setup>
import { computed, ref, watch } from 'vue'
import FormField from './FormField.vue'
import FormButton from './FormButton.vue'
import RoleBadge from './RoleBadge.vue'

// ---- Ícones (caminho "d" de SVGs 24x24, estilo contorno) ----
const icons = {
  // Pin preenchido (solid), usado na etiqueta do topo
  pin: 'm11.54 22.351.07.04.028.016a.76.76 0 0 0 .723 0l.028-.015.071-.041a16.975 16.975 0 0 0 1.144-.742 19.58 19.58 0 0 0 2.683-2.282c1.944-1.99 3.963-4.98 3.963-8.827a8.25 8.25 0 0 0-16.5 0c0 3.846 2.02 6.837 3.963 8.827a19.58 19.58 0 0 0 2.682 2.282 16.975 16.975 0 0 0 1.145.742ZM12 13.5a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z',
  check: 'm4.5 12.75 6 6 9-13.5',
}

// ---- Campos padrão (Endereço Residencial) ----
// { key, label, type?, placeholder?, options?, locked?, span?, hint? }
//   span = 1 a 4 (a linha tem 4 colunas) -> é o "tamanho da caixa"
//   hint = texto-link à direita do rótulo (emite o evento "hint" com a key)
const defaultFields = [
  { key: 'cep', label: 'CEP', placeholder: '00000-000', span: 2, hint: 'Não sei meu CEP' },
  { key: 'cidade', label: 'Cidade', placeholder: 'Cidade', span: 2 },
  { key: 'logradouro', label: 'Logradouro / Rua / Avenida', placeholder: 'Rua Projetada', span: 3 },
  { key: 'numero', label: 'Número', placeholder: '1000', span: 1 },
  { key: 'bairro', label: 'Bairro', placeholder: 'Meu Bairro', span: 2 },
  { key: 'complemento', label: 'Complemento', placeholder: 'Apto, bloco...', span: 2 },
]

// fields: lista própria (opcional). Sem ela, usa os campos acima.
// v-model = objeto com os valores: { cep: '...', cidade: '...' }
// O v-model só é atualizado quando clicar em Salvar.
const props = defineProps({
  title: { type: String, default: 'Endereço Residencial' },
  badge: { type: String, default: 'Endereço Principal' }, // '' = esconde a etiqueta
  fields: { type: Array, default: null },
  submitLabel: { type: String, default: 'Salvar Alterações' },
})

const model = defineModel({ type: Object, default: () => ({}) })

// Rascunho: é o que o usuário digita. Só vai para o v-model ao salvar.
const values = ref({ ...model.value })
watch(model, (novo) => (values.value = { ...novo }), { deep: true })

// submit = clicou em Salvar (recebe os valores) | hint = clicou no link do rótulo
const emit = defineEmits(['submit', 'hint'])

const list = computed(() => props.fields ?? defaultFields)

// Classes completas (o Tailwind precisa enxergar o texto inteiro)
const spans = {
  1: 'sm:col-span-1',
  2: 'sm:col-span-2',
  3: 'sm:col-span-3',
  4: 'sm:col-span-4',
}

function update(key, value) {
  values.value = { ...values.value, [key]: value }
}

function submit() {
  model.value = { ...values.value }
  emit('submit', model.value)
}
</script>

<template>
  <form
    class="flex flex-col gap-8 rounded-xl bg-white p-8 shadow-[0_2px_12px_rgba(11,47,91,0.08)]"
    @submit.prevent="submit"
  >
    <header class="flex items-center justify-between gap-4">
      <h2 v-if="title" class="text-2xl font-medium text-[#0b2f5b]">{{ title }}</h2>

      <RoleBadge v-if="badge" :label="badge" :icon="icons.pin" />
    </header>

    <div class="grid grid-cols-1 gap-x-5 gap-y-6 sm:grid-cols-4">
      <FormField
        v-for="field in list"
        :key="field.key"
        :class="spans[field.span ?? 2]"
        :label="field.label"
        :type="field.type"
        :placeholder="field.placeholder"
        :options="field.options"
        :locked="field.locked"
        :model-value="values[field.key] ?? ''"
        @update:model-value="update(field.key, $event)"
      >
        <template v-if="field.hint" #hint>
          <button
            type="button"
            class="cursor-pointer text-xs font-bold text-[#0a7a82] hover:underline"
            @click="emit('hint', field.key)"
          >
            {{ field.hint }}
          </button>
        </template>
      </FormField>
    </div>

    <div class="flex items-center justify-end gap-3">
      <slot name="actions">
        <FormButton type="submit" :icon="icons.check">{{ submitLabel }}</FormButton>
      </slot>
    </div>
  </form>
</template>