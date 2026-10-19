<script setup>
import { computed, ref, watch } from 'vue'
import FormField from './FormField.vue'
import FormButton from './FormButton.vue'

// ---- Ícones (caminho "d" de SVGs 24x24, estilo contorno) ----
const icons = {
  user: 'M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.5 20.118a7.5 7.5 0 0 1 15 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.5-1.632Z',
  id: 'M15 9h3.75M15 12h3.75M15 15h3.75M4.5 19.5h15a2.25 2.25 0 0 0 2.25-2.25V6.75A2.25 2.25 0 0 0 19.5 4.5h-15a2.25 2.25 0 0 0-2.25 2.25v10.5A2.25 2.25 0 0 0 4.5 19.5Zm6-10.125a1.875 1.875 0 1 1-3.75 0 1.875 1.875 0 0 1 3.75 0Zm1.294 6.336a6.721 6.721 0 0 1-3.17.789 6.721 6.721 0 0 1-3.168-.789 3.376 3.376 0 0 1 6.338 0Z',
  calendar:
    'M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 0 1 2.25-2.25h13.5A2.25 2.25 0 0 1 21 7.5v11.25m-18 0A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75m-18 0v-7.5A2.25 2.25 0 0 1 5.25 9h13.5A2.25 2.25 0 0 1 21 11.25v7.5',
  phone:
    'M10.5 1.5H8.25A2.25 2.25 0 0 0 6 3.75v16.5a2.25 2.25 0 0 0 2.25 2.25h7.5A2.25 2.25 0 0 0 18 20.25V3.75a2.25 2.25 0 0 0-2.25-2.25H13.5m-3 0V3h3V1.5m-3 0h3m-3 18.75h3',
  email:
    'M21.75 6.75v10.5a2.25 2.25 0 0 1-2.25 2.25h-15a2.25 2.25 0 0 1-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0 0 19.5 4.5h-15a2.25 2.25 0 0 0-2.25 2.25m19.5 0v.243a2.25 2.25 0 0 1-1.07 1.916l-7.5 4.615a2.25 2.25 0 0 1-2.36 0L3.32 8.91a2.25 2.25 0 0 1-1.07-1.916V6.75',
  check: 'm4.5 12.75 6 6 9-13.5',
}

const defaultFields = [
  { key: 'nome', label: 'Nome Completo', icon: icons.user, placeholder: 'Nome Paciente', span: 2 },
  { key: 'cpf', label: 'CPF', icon: icons.id, placeholder: '123.456.789-00', locked: true },
  { key: 'orgao', label: 'Órgão Emissor (RG / UF)', icon: icons.id, placeholder: 'SSP / PI', locked: true },
  { key: 'nascimento', label: 'Data de Nascimento', icon: icons.calendar, placeholder: 'dd/mm/aaaa', locked: true },
  {
    key: 'genero',
    label: 'Gênero',
    icon: icons.user,
    type: 'select',
    options: ['Masculino', 'Feminino', 'Outro', 'Prefiro não informar'],
    locked: true,
  },
  { key: 'telefone', label: 'Telefone / WhatsApp', icon: icons.phone, type: 'tel', placeholder: '(11) 98765-4321' },
  { key: 'email', label: 'E-mail de Contato', icon: icons.email, type: 'email', placeholder: 'nome@email.com' },
]

// fields: lista própria (opcional). Sem ela, usa os campos acima.
// v-model = objeto com os valores: { nome: '...', cpf: '...' }
// Os botões "Voltar" e "Salvar" já vêm no card (slot "actions" troca por outros).
const props = defineProps({
  title: { type: String, default: 'Dados Cadastrais do Paciente' },
  fields: { type: Array, default: null },
  submitLabel: { type: String, default: 'Salvar Alterações' },
  showBack: { type: Boolean, default: true }, // false = esconde o botão "Voltar"
})

// Valores SALVOS. Só mudam quando o formulário é enviado.
// Funciona COM v-model e também sem ele.
const model = defineModel({ type: Object, default: () => ({}) })

// Rascunho: é o que o usuário digita. Não afeta o resto da tela até salvar.
const values = ref({ ...model.value })

// Se o valor salvo mudar por fora (ex.: veio da API), atualiza o rascunho.
watch(model, (novo) => (values.value = { ...novo }), { deep: true })

// submit = clicou em Salvar (recebe os valores) | back = clicou em Voltar
const emit = defineEmits(['submit', 'back'])

const list = computed(() => props.fields ?? defaultFields)

// Classes completas (o Tailwind precisa enxergar o texto inteiro)
const spans = {
  1: 'sm:col-span-1',
  2: 'sm:col-span-2',
}

function update(key, value) {
  values.value = { ...values.value, [key]: value }
}

function submit() {
  model.value = { ...values.value } // só agora o valor salvo é atualizado
  emit('submit', model.value)
}
</script>

<template>
  <form
    class="flex flex-col gap-8 rounded-xl bg-white p-8 shadow-[0_2px_12px_rgba(11,47,91,0.08)]"
    @submit.prevent="submit"
  >
    <h2 v-if="title" class="text-2xl font-medium text-[#0b2f5b]">{{ title }}</h2>

    <div class="grid grid-cols-1 gap-x-5 gap-y-6 sm:grid-cols-2">
      <FormField
        v-for="field in list"
        :key="field.key"
        :class="spans[field.span ?? 1]"
        :label="field.label"
        :type="field.type"
        :icon="field.icon"
        :placeholder="field.placeholder"
        :options="field.options"
        :locked="field.locked"
        :model-value="values[field.key] ?? ''"
        @update:model-value="update(field.key, $event)"
      />
    </div>

    <div class="flex items-center justify-end gap-3">
      <slot name="actions">
        <!-- <FormButton v-if="showBack" variant="text" @click="emit('back')">Voltar</FormButton> -->
        <FormButton type="submit" :icon="icons.check">{{ submitLabel }}</FormButton>
      </slot>
    </div>
  </form>
</template>