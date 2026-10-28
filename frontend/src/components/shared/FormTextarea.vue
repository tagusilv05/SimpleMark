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
 *   variant      String  (padrão: 'outline') aparência da caixa, igual ao FormField:
 *                                       'outline' -> fundo branco com borda cinza
 *                                       'filled'  -> fundo azul claro, sem borda
 *   counter      Boolean (padrão: true)  com `maxlength`, mostra o contador "n/limite" abaixo
 *                                       da caixa. Use false para exibi-lo você mesma
 *                                       (ex.: no slot "hint", ao lado do rótulo).
 *
 * SLOTS
 *   hint   conteúdo opcional à direita do rótulo (ex.: contador de caracteres).
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
  variant: { type: String, default: 'outline', validator: (v) => ['outline', 'filled'].includes(v) },
  counter: { type: Boolean, default: true },
  error: { type: String, default: '' },
})

const emit = defineEmits(['update:modelValue'])

const id = useId()

// Recuo à esquerda: com ícone, ou quando `indent` pede o mesmo alinhamento
const hasIndent = computed(() => !!props.icon || props.indent)

// Aparência da caixa (fundo e borda); com erro, ganha destaque vermelho
const boxStyle = computed(() => {
  if (props.variant === 'filled') {
    return props.error ? 'bg-[#eef1fe] ring-2 ring-red-400' : 'bg-[#eef1fe]'
  }
  return props.error ? 'border border-red-500 bg-white' : 'border border-gray-300 bg-white'
})

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
    <div class="flex items-center justify-between gap-2">
      <label :for="id" class="text-sm font-bold text-gray-900">{{ label }}</label>
      <slot name="hint" />
    </div>

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
        class="w-full resize-none rounded-lg py-3 pr-4 text-[15px] leading-5 text-gray-800 outline-none transition placeholder:text-gray-400 focus:ring-2 focus:ring-[#0a9ba5]"
        :class="[boxStyle, hasIndent ? 'pl-12' : 'pl-4']"
        @input="onInput"
      />
    </div>

    <div class="flex justify-between gap-2">
      <p v-if="error" class="text-xs font-medium text-red-600" role="alert">{{ error }}</p>
      <span v-else />
      <span v-if="maxlength && counter" class="text-xs text-gray-500">
        {{ modelValue.length }}/{{ maxlength }}
      </span>
    </div>
  </div>
</template>