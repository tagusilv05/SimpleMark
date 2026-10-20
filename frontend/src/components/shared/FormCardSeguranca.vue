<script setup>
import { computed, ref } from 'vue'
import FormField from './FormField.vue'
import FormButton from './FormButton.vue'

// ---- Ícones (caminho "d" de SVGs 24x24, estilo contorno) ----
const icons = {
  lock: 'M16.5 10.5V6.75a4.5 4.5 0 1 0-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 0 0 2.25-2.25v-6.75a2.25 2.25 0 0 0-2.25-2.25H6.75a2.25 2.25 0 0 0-2.25 2.25v6.75a2.25 2.25 0 0 0 2.25 2.25Z',
  key: 'M15.75 5.25a3 3 0 0 1 3 3m3 0a6 6 0 0 1-7.029 5.912c-.563-.097-1.159.026-1.563.43L10.5 17.25H8.25v2.25H6v2.25H2.25v-2.818c0-.597.237-1.17.659-1.591l6.499-6.499c.404-.404.527-1 .43-1.563A6 6 0 1 1 21.75 8.25Z',
  checkCircle: 'M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z',
  check: 'm4.5 12.75 6 6 9-13.5',
}

// Os rótulos e os campos já vêm definidos aqui dentro.
// Eventos: submit = clicou em Salvar (recebe { atual, nova })
const props = defineProps({
  title: { type: String, default: 'Segurança & Senha de Acesso' },
  submitLabel: { type: String, default: 'Salvar Alterações' },
  // Mensagem de erro vinda de fora (ex.: "Senha atual incorreta", da API)
  error: { type: String, default: '' },
})

const emit = defineEmits(['submit'])

const form = ref({ atual: '', nova: '', confirmar: '' })
const localError = ref('')

// Requisitos da nova senha (sempre em verde; também validados ao salvar)
const rules = computed(() => [
  { key: 'tamanho', label: 'Mínimo de 8 dígitos', ok: form.value.nova.length >= 8 },
  { key: 'maiuscula', label: 'Ao menos 1 letra maiúscula', ok: /[A-Z]/.test(form.value.nova) },
  {
    key: 'especial',
    label: 'Número e caractere especial (@#$)',
    ok: /\d/.test(form.value.nova) && /[^A-Za-z0-9]/.test(form.value.nova),
  },
])

const mensagem = computed(() => props.error || localError.value)

function submit() {
  localError.value = ''

  if (!form.value.atual) {
    localError.value = 'Informe a senha atual.'
  } else if (!rules.value.every((r) => r.ok)) {
    localError.value = 'A nova senha não atende a todos os requisitos.'
  } else if (form.value.nova !== form.value.confirmar) {
    localError.value = 'A confirmação não é igual à nova senha.'
  }
  if (localError.value) return

  emit('submit', { atual: form.value.atual, nova: form.value.nova })
  form.value = { atual: '', nova: '', confirmar: '' }
}
</script>

<template>
  <form
    class="flex flex-col gap-8 rounded-xl bg-white p-8 shadow-[0_2px_12px_rgba(11,47,91,0.08)]"
    @submit.prevent="submit"
  >
    <h2 v-if="title" class="text-2xl font-medium text-[#0b2f5b]">{{ title }}</h2>

    <div class="flex flex-col gap-6">
      <FormField
        v-model="form.atual"
        label="Senha Atual"
        type="password"
        placeholder="Digite sua senha atual"
        :icon="icons.lock"
      />
      <FormField
        v-model="form.nova"
        label="Nova Senha"
        type="password"
        placeholder="Criar nova senha"
        :icon="icons.key"
      />
      <FormField
        v-model="form.confirmar"
        label="Confirmar Nova Senha"
        type="password"
        placeholder="Repita a nova senha"
        :icon="icons.checkCircle"
      />
    </div>

    <!-- Requisitos da senha -->
    <ul class="flex flex-wrap gap-x-6 gap-y-2 rounded-xl bg-[#eef1fe] px-4 py-4">
      <li
        v-for="rule in rules"
        :key="rule.key"
        class="inline-flex items-center gap-1.5 text-xs font-bold text-[#0a7a82]"
      >
        <svg
          class="size-4 shrink-0"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke-width="1.5"
          stroke="currentColor"
          aria-hidden="true"
        >
          <path stroke-linecap="round" stroke-linejoin="round" :d="icons.checkCircle" />
        </svg>
        {{ rule.label }}
      </li>
    </ul>

    <p v-if="mensagem" role="alert" class="-mt-4 text-sm font-medium text-red-600">
      {{ mensagem }}
    </p>

    <div class="flex items-center justify-end gap-3">
      <slot name="actions">
        <FormButton type="submit" :icon="icons.check">{{ submitLabel }}</FormButton>
      </slot>
    </div>
  </form>
</template>