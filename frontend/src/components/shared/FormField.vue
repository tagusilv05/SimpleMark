<script setup>

/**
 * FormField — campo de formulário com rótulo, caixa (input ou select) e ícone
 *
 * COMO USAR (na página):
 *
 *   import FormField from '@/components/shared/FormField.vue'
 *
 *   <FormField label="Nome" v-model="nome" />                              // input de texto simples
 *   <FormField label="E-mail" type="email" v-model="email"
 *              placeholder="voce@exemplo.com" />                           // com placeholder
 *   <FormField label="Telefone" type="tel" v-model="telefone"
 *              icon="M2.25 6.75c0 8.284 6.716 15 15 15h2.25a2.25 2.25 0 0 0 2.25-2.25v-1.372" />  // com ícone à esquerda
 *   <FormField label="Senha" type="password" v-model="senha" />            // ganha o botão de olho
 *   <FormField label="Data de nascimento" type="date" v-model="nascimento" />
 *   <FormField label="Sexo" type="select" v-model="sexo"
 *              :options="['Masculino', 'Feminino', 'Outro']" />            // select com lista simples
 *   <FormField label="Estado" type="select" v-model="uf"
 *              :options="[{ value: 'PI', label: 'Piauí' }]" />             // select com { value, label }
 *   <FormField label="CPF" v-model="cpf" locked />                         // bloqueado (somente leitura)
 *   <FormField label="Valor" v-model="valor" variant="white" />            // caixa branca com borda
 *   <FormField label="Apresentação" type="textarea" v-model="bio" />       // várias linhas; cresce conforme se escreve
 *   <FormField label="Valor" v-model="v" size="sm"
 *              input-class="text-lg font-bold" />                          // baixo (h-11) e texto grande em negrito
 *
 *   <FormField label="CEP" v-model="cep">                                  // slot "hint" ao lado do rótulo
 *     <template #hint>
 *       <a href="#" class="text-sm text-[#0b2f5b]">Não sei meu CEP</a>
 *     </template>
 *   </FormField>
 *
 * PROPS
 *   label        String  (obrigatória)
 *                  texto do rótulo exibido acima da caixa. Fica ligado ao campo
 *                  por `for`/`id` (o id é gerado automaticamente com useId).
 *   modelValue   String | Number  (padrão: '')
 *                  valor do campo. Use com v-model.
 *   type         String  (padrão: 'text')
 *                  tipo do campo: 'text', 'email', 'tel', 'date', 'password', etc.
 *                  (qualquer type nativo de <input>), 'select' para lista suspensa
 *                  ou 'textarea' para texto de várias linhas.
 *                  - 'password' -> ganha botão de olho para mostrar/esconder a senha.
 *                  - 'select'   -> renderiza <select> com seta à direita.
 *   icon         String  (padrão: '')
 *                  caminho "d" de um SVG 24x24 (ex.: dos Heroicons), exibido à
 *                  esquerda dentro da caixa. Vazio = sem ícone.
 *   placeholder  String  (padrão: '')
 *                  texto de dica dentro do input. Não se aplica ao select.
 *   options      Array  (padrão: [])
 *                  só para type="select". Aceita:
 *                  - lista simples: ['Masculino', 'Feminino']
 *                  - lista de objetos: [{ value: 'M', label: 'Masculino' }]
 *   size         String  (padrão: 'md')
 *                  altura da caixa de input/select: 'md' (h-13) ou 'sm' (h-11,
 *                  mesma altura do FormButton). O textarea cresce sozinho.
 *   inputClass   String  (padrão: 'text-[15px]')
 *                  classes Tailwind do texto digitado no input/textarea, ex.:
 *                  input-class="text-lg font-bold" para texto maior e em negrito.
 *   labelClass   String  (padrão: 'text-sm font-bold text-gray-900')
 *                  classes Tailwind do rótulo. Use para mudar o estilo do texto,
 *                  ex.: label-class="text-xs font-semibold uppercase text-gray-500".
 *   variant      String  (padrão: 'soft')
 *                  cor da caixa (input, select e textarea):
 *                  - 'soft'  -> fundo azul claro (#eef1fe), sem borda
 *                  - 'white' -> fundo branco com borda cinza clara
 *                  Qualquer outro valor gera aviso no console (validator).
 *   readonly     Boolean  (padrão: false)
 *                  somente leitura: texto cinza (text-gray-500), sem cadeado e sem
 *                  anel de foco. Use para travar até o usuário clicar em "Editar";
 *                  ao voltar para false o texto fica escuro e editável.
 *                  Vale para input e textarea.
 *   locked       Boolean  (padrão: false)
 *                  campo bloqueado (somente leitura): texto acinzentado e cadeado
 *                  à direita. No input usa `readonly`; no select usa `disabled`.
 *
 * SLOTS
 *   hint   texto ou link opcional à direita do rótulo (ex.: "Não sei meu CEP").
 *
 * EVENTOS
 *   update:modelValue   emitido a cada digitação (input) ou mudança (select),
 *                       com o novo valor. É o que faz o v-model funcionar.
 *                       Atenção: no select o valor sempre chega como String,
 *                       mesmo que o `value` da opção seja um número.
 *
 * ESTILO
 *   Já vem com Tailwind: caixa h-13 com cantos arredondados e anel de foco na
 *   cor turquesa. A cor de fundo vem da prop `variant`. Para criar outra cor,
 *   adicione uma chave em `boxStyles` e inclua o nome no validator de `variant`.
 *
 * DEPENDÊNCIAS
 *   - Vue 3.5+ (usa useId)
 *   - Tailwind CSS
 */



import { computed, nextTick, onMounted, ref, useId, watch } from 'vue'

// Campo com rótulo + caixa (input ou select) + ícone.
// type: 'text' | 'email' | 'tel' | 'date' | 'password' | ... | 'select'
// type="password" ganha o botão de olho para mostrar/esconder a senha.
// options (só para select): ['Masculino', ...] ou [{ value, label }]
// locked: campo bloqueado (somente leitura), mostra cadeado à direita
const props = defineProps({
  label: { type: String, required: true },
  modelValue: { type: [String, Number], default: '' },
  type: { type: String, default: 'text' },
  icon: { type: String, default: '' },
  placeholder: { type: String, default: '' },
  options: { type: Array, default: () => [] },
  locked: { type: Boolean, default: false },
  readonly: { type: Boolean, default: false },
  labelClass: { type: String, default: 'text-sm font-bold text-gray-900' },
  size: {
    type: String,
    default: 'md',
    validator: (v) => ['md', 'sm'].includes(v),
  },
  inputClass: { type: String, default: 'text-[15px]' },
  variant: {
    type: String,
    default: 'soft',
    validator: (v) => ['soft', 'white'].includes(v),
  },
})

const emit = defineEmits(['update:modelValue'])

const id = useId()

const paths = {
  lock: 'M16.5 10.5V6.75a4.5 4.5 0 1 0-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 0 0 2.25-2.25v-6.75a2.25 2.25 0 0 0-2.25-2.25H6.75a2.25 2.25 0 0 0-2.25 2.25v6.75a2.25 2.25 0 0 0 2.25 2.25Z',
  chevron: 'm19.5 8.25-7.5 7.5-7.5-7.5',
  eye: 'M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z',
  eyeOff:
    'M3.98 8.223A10.477 10.477 0 0 0 1.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.451 10.451 0 0 1 12 4.5c4.756 0 8.773 3.162 10.065 7.498a10.522 10.522 0 0 1-4.293 5.774M6.228 6.228 3 3m3.228 3.228 3.65 3.65m7.894 7.894L21 21m-3.228-3.228-3.65-3.65m0 0a3 3 0 1 0-4.243-4.243m4.242 4.242L9.88 9.88',
}

// Senha: alterna entre escondida e visível
const visible = ref(false)
const inputType = computed(() => (props.type === 'password' && visible.value ? 'text' : props.type))

// Cor da caixa, escolhida pela prop `variant`
const boxStyles = {
  soft: 'bg-[#eef1fe]',
  white: 'border border-gray-200 bg-white',
}
const boxClass = computed(() => boxStyles[props.variant])

// Estado do input/textarea: bloqueado (cinza + cadeado), só leitura ou editável.
// A cor do texto e o anel de foco ficam aqui para não conflitarem com classes estáticas.
const isReadonly = computed(() => props.locked || props.readonly)
const stateClass = computed(() => {
  if (props.locked) return 'cursor-not-allowed text-gray-400'
  if (props.readonly) return 'cursor-default text-gray-500'
  return 'text-gray-800 focus:ring-2 focus:ring-[#0a9ba5]'
})

// Altura da caixa (input/select), escolhida pela prop `size`
const sizeStyles = { md: 'h-13', sm: 'h-11' }
const sizeClass = computed(() => sizeStyles[props.size])

// Textarea que cresce conforme o usuário escreve
const textareaEl = ref(null)
function autoGrow() {
  const el = textareaEl.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = `${el.scrollHeight}px`
}
function onTextareaInput(event) {
  emit('update:modelValue', event.target.value)
  autoGrow()
}
onMounted(autoGrow)
// também ajusta quando o texto muda por fora (ex.: dados carregados depois)
watch(() => props.modelValue, () => nextTick(autoGrow))

const optionValue = (o) => (typeof o === 'object' ? o.value : o)
const optionLabel = (o) => (typeof o === 'object' ? o.label : o)
</script>

<template>
  <div class="flex flex-col gap-2">
    <!-- Slot "hint": texto/link opcional à direita do rótulo (ex.: "Não sei meu CEP") -->
    <div class="flex items-center justify-between gap-2">
      <label :for="id" :class="labelClass">{{ label }}</label>
      <slot name="hint" />
    </div>

    <div class="relative">
      <!-- Ícone da esquerda -->
      <svg
        v-if="icon"
        class="pointer-events-none absolute left-4 top-1/2 size-5 -translate-y-1/2"
        :class="locked ? 'text-gray-400' : 'text-gray-500'"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        stroke-width="1.5"
        stroke="currentColor"
        aria-hidden="true"
      >
        <path stroke-linecap="round" stroke-linejoin="round" :d="icon" />
      </svg>

      <!-- Select -->
      <select
        v-if="type === 'select'"
        :id="id"
        :value="modelValue"
        :disabled="locked"
        class="w-full cursor-pointer appearance-none rounded-lg pr-11 text-[15px] text-gray-700 outline-none transition focus:ring-2 focus:ring-[#0a9ba5] disabled:cursor-not-allowed disabled:text-gray-400"
        :class="[sizeClass, boxClass, icon ? 'pl-12' : 'pl-4']"
        @change="emit('update:modelValue', $event.target.value)"
      >
        <option v-for="o in options" :key="optionValue(o)" :value="optionValue(o)">
          {{ optionLabel(o) }}
        </option>
      </select>

      <!-- Textarea -->
      <textarea
        v-else-if="type === 'textarea'"
        :id="id"
        :value="modelValue"
        :placeholder="placeholder"
        :readonly="isReadonly"
        ref="textareaEl"
        rows="3"
        class="w-full resize-none overflow-hidden rounded-lg px-4 py-3 outline-none transition placeholder:text-gray-400"
        :class="[boxClass, inputClass, stateClass]"
        @input="onTextareaInput"
      />

      <!-- Input -->
      <input
        v-else
        :id="id"
        :type="inputType"
        :value="modelValue"
        :placeholder="placeholder"
        :readonly="isReadonly"
        class="w-full rounded-lg pr-11 outline-none transition placeholder:text-gray-400"
        :class="[sizeClass, boxClass, inputClass, stateClass, icon ? 'pl-12' : 'pl-4']"
        @input="emit('update:modelValue', $event.target.value)"
      />

      <!-- Olho da senha (mostrar / esconder) -->
      <button
        v-if="type === 'password'"
        type="button"
        class="absolute right-3 top-1/2 flex size-8 -translate-y-1/2 cursor-pointer items-center justify-center rounded-md text-gray-600 transition hover:text-[#042d5c]"
        :aria-label="visible ? 'Esconder senha' : 'Mostrar senha'"
        :aria-pressed="visible"
        @click="visible = !visible"
      >
        <svg
          class="size-5"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke-width="1.5"
          stroke="currentColor"
          aria-hidden="true"
        >
          <path stroke-linecap="round" stroke-linejoin="round" :d="visible ? paths.eyeOff : paths.eye" />
        </svg>
      </button>

      <!-- Ícone da direita: cadeado (bloqueado) ou seta (select) -->
      <svg
        v-if="locked || type === 'select'"
        class="pointer-events-none absolute right-4 top-1/2 -translate-y-1/2 text-gray-500"
        :class="type === 'select' && !locked ? 'size-4' : 'size-4'"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        :stroke-width="type === 'select' && !locked ? 2.5 : 1.5"
        stroke="currentColor"
        aria-hidden="true"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          :d="locked ? paths.lock : paths.chevron"
        />
      </svg>
    </div>
  </div>
</template>