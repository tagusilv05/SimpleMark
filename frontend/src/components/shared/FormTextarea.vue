<script setup>
/**
 * FormTextarea — área de texto com rótulo, no mesmo visual do FormField (variante "outline")
 *
 * COMO USAR (na página):
 *
 *   import FormTextarea from '@/components/shared/FormTextarea.vue'
 *
 *   <FormTextarea label="Informações Profissionais" v-model="info"
 *                 placeholder="Conte sobre sua formação..." :maxlength="500" :rows="3" />
 *
 * PROPS
 *   label        String  (obrigatória)  rótulo acima da caixa (ligado por for/id).
 *   modelValue   String  (padrão: '')   valor do campo. Use com v-model.
 *   placeholder  String  (padrão: '')   texto de dica.
 *   rows         Number  (padrão: 3)    altura inicial, em linhas.
 *   maxlength    Number  (padrão: 0)    limite de caracteres (0 = sem limite). Com limite,
 *                                       aparece um contador "n/limite" abaixo da caixa.
 *   icon         String  (padrão: '')   caminho "d" de um SVG 24x24 (Heroicons), exibido à
 *                                       esquerda, alinhado à primeira linha. Vazio = sem ícone.
 *   indent       Boolean (padrão: false) mantém o recuo à esquerda mesmo sem ícone.
 *   error        String  (padrão: '')   mensagem de erro (vermelha) abaixo da caixa.
 *
 * EVENTOS
 *   update:modelValue   emitido a cada digitação, com o novo valor.
 *
 * FILTRO DE DIGITAÇÃO
 *   Igual ao FormField: se a página alterar o valor recebido, o campo mostra o valor final.
 */

import { computed, nextTick, useId } from 'vue'

const props = defineProps({
  label: { type: String, required: true },
  modelValue: { type: String, default: '' },
  placeholder: { type: String, default: '' },
  rows: { type: Number, default: 3 },
  maxlength: { type: Number, default: 0 },
  icon: { type: String, default: '' },
  indent: { type: Boolean, default: false },
  error: { type: String, default: '' },
})

const emit = defineEmits(['update:modelValue'])

const id = useId()

// Recuo à esquerda: com ícone, ou quando `indent` pede o mesmo alinhamento
const hasIndent = computed(() => !!props.icon || props.indent)

function onInput(event) {
  const el = event.target
  emit('update:modelValue', el.value)
  nextTick(() => {
    const final = String(props.modelValue ?? '')
    if (el.value !== final) el.value = final
  })
}
</script>

<template>
  <div class="flex flex-col gap-2">
    <label :for="id" class="text-sm font-bold text-gray-900">{{ label }}</label>

    <div class="relative">
      <!-- Ícone da esquerda (alinhado à primeira linha do texto) -->
      <svg
        v-if="icon"
        class="pointer-events-none absolute left-4 top-3 size-5 text-gray-500"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        stroke-width="1.5"
        stroke="currentColor"
        aria-hidden="true"
      >
        <path stroke-linecap="round" stroke-linejoin="round" :d="icon" />
      </svg>

      <textarea
        :id="id"
        :value="modelValue"
        :rows="rows"
        :placeholder="placeholder"
        :maxlength="maxlength || undefined"
        :aria-invalid="!!error"
        class="w-full resize-none rounded-lg border bg-white py-3 pr-4 text-[15px] leading-5 text-gray-800 outline-none transition placeholder:text-gray-400 focus:ring-2 focus:ring-[#0a9ba5]"
        :class="[error ? 'border-red-500' : 'border-gray-300', hasIndent ? 'pl-12' : 'pl-4']"
        @input="onInput"
      />
    </div>

    <div class="flex justify-between gap-2">
      <p v-if="error" class="text-xs font-medium text-red-600" role="alert">{{ error }}</p>
      <span v-else />
      <span v-if="maxlength" class="text-xs text-gray-500">
        {{ modelValue.length }}/{{ maxlength }}
      </span>
    </div>
  </div>
</template>