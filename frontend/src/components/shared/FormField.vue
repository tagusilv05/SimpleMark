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
 *   <FormField label="E-mail" v-model="email" variant="outline" />         // caixa branca com borda (telas de login)
 *   <FormField label="CPF" v-model="cpf" inputmode="numeric"
 *              :error="erros.cpf" />                                       // teclado numérico + mensagem de erro
 *   <FormField label="CEP" v-model="cep" indent />                         // sem ícone, mas alinhado como se tivesse
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
 *                  (qualquer type nativo de <input>) ou 'select' para lista suspensa.
 *                  - 'password' -> ganha botão de olho para mostrar/esconder a senha.
 *                  - 'select'   -> renderiza <select> com seta à direita.
 *   variant      String  (padrão: 'filled')
 *                  aparência da caixa:
 *                  - 'filled'  -> fundo azul claro, sem borda (padrão)
 *                  - 'outline' -> fundo branco com borda cinza (telas de login e cadastro)
 *   icon         String  (padrão: '')
 *                  caminho "d" de um SVG 24x24 (ex.: dos Heroicons), exibido à
 *                  esquerda dentro da caixa. Vazio = sem ícone.
 *   indent       Boolean  (padrão: false)
 *                  mantém o recuo à esquerda do texto mesmo sem ícone (alinha com
 *                  os campos que têm ícone).
 *   placeholder  String  (padrão: '')
 *                  texto de dica dentro do input. No select, vira a primeira opção
 *                  (desabilitada, em cinza) enquanto nada foi escolhido.
 *   inputmode    String  (padrão: '')
 *                  teclado sugerido em celulares: 'numeric', 'tel', 'email'...
 *                  Vazio = não define.
 *   error        String  (padrão: '')
 *                  mensagem de erro exibida abaixo da caixa (vermelha). A caixa
 *                  também ganha destaque vermelho. Vazio = sem erro.
 *   options      Array  (padrão: [])
 *                  só para type="select". Aceita:
 *                  - lista simples: ['Masculino', 'Feminino']
 *                  - lista de objetos: [{ value: 'M', label: 'Masculino' }]
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
 * FILTRO DE DIGITAÇÃO
 *   Se a página alterar o valor recebido (máscara de CPF, só números etc.), o
 *   campo passa a mostrar o valor final, inclusive quando ele não muda (ex.: uma
 *   letra digitada num campo numérico é descartada na hora). Por isso o campo
 *   precisa estar ligado a um v-model (ou :model-value + @update:model-value).
 *
 * ESTILO
 *   Já vem com Tailwind: caixa h-13 com fundo azul claro, cantos arredondados e
 *   anel de foco na cor turquesa. Para ajustar cores ou altura, edite as classes
 *   do <input> / <select> no template.
 *
 * DEPENDÊNCIAS
 *   - Vue 3.5+ (usa useId)
 *   - Tailwind CSS
 */



import { computed, nextTick, ref, useId } from 'vue'

// Campo com rótulo + caixa (input ou select) + ícone.
// type: 'text' | 'email' | 'tel' | 'date' | 'password' | ... | 'select'
// type="password" ganha o botão de olho para mostrar/esconder a senha.
// options (só para select): ['Masculino', ...] ou [{ value, label }]
// locked: campo bloqueado (somente leitura), mostra cadeado à direita
// variant: 'filled' (padrão) | 'outline'
// error: mensagem de erro abaixo da caixa
const props = defineProps({
  label: { type: String, required: true },
  modelValue: { type: [String, Number], default: '' },
  type: { type: String, default: 'text' },
  variant: {
    type: String,
    default: 'filled',
    validator: (v) => ['filled', 'outline'].includes(v),
  },
  icon: { type: String, default: '' },
  indent: { type: Boolean, default: false },
  placeholder: { type: String, default: '' },
  inputmode: { type: String, default: '' },
  error: { type: String, default: '' },
  options: { type: Array, default: () => [] },
  locked: { type: Boolean, default: false },
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

// Aparência da caixa (fundo e borda); com erro, ganha destaque vermelho
const boxStyle = computed(() => {
  if (props.variant === 'outline') {
    return props.error ? 'border border-red-500 bg-white' : 'border border-gray-300 bg-white'
  }
  return props.error ? 'bg-[#eef1fe] ring-2 ring-red-400' : 'bg-[#eef1fe]'
})

// Recuo à esquerda: com ícone, ou quando `indent` pede o mesmo alinhamento
const hasIndent = computed(() => !!props.icon || props.indent)

// Senha: alterna entre escondida e visível
const visible = ref(false)
const inputType = computed(() => (props.type === 'password' && visible.value ? 'text' : props.type))

const optionValue = (o) => (typeof o === 'object' ? o.value : o)
const optionLabel = (o) => (typeof o === 'object' ? o.label : o)

// Emite o valor digitado e, depois que a página responde, garante que o campo mostre
// o valor final (máscara/filtro). Sem isso, uma tecla descartada (ex.: letra num campo
// numérico) continuaria aparecendo, porque o valor do v-model não mudou.
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
    <!-- Slot "hint": texto/link opcional à direita do rótulo (ex.: "Não sei meu CEP") -->
    <div class="flex items-center justify-between gap-2">
      <label :for="id" class="text-sm font-bold text-gray-900">{{ label }}</label>
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
        :aria-invalid="!!error"
        class="h-13 w-full cursor-pointer appearance-none rounded-lg pr-11 text-[15px] outline-none transition focus:ring-2 focus:ring-[#0a9ba5] disabled:cursor-not-allowed disabled:text-gray-400"
        :class="[
          boxStyle,
          hasIndent ? 'pl-12' : 'pl-4',
          modelValue === '' && placeholder ? 'text-gray-400' : 'text-gray-700',
        ]"
        @change="emit('update:modelValue', $event.target.value)"
      >
        <option v-if="placeholder" value="" disabled>{{ placeholder }}</option>
        <option v-for="o in options" :key="optionValue(o)" :value="optionValue(o)">
          {{ optionLabel(o) }}
        </option>
      </select>

      <!-- Input -->
      <input
        v-else
        :id="id"
        :type="inputType"
        :value="modelValue"
        :placeholder="placeholder"
        :readonly="locked"
        :inputmode="inputmode || undefined"
        :aria-invalid="!!error"
        class="h-13 w-full rounded-lg pr-11 text-[15px] text-gray-800 outline-none transition placeholder:text-gray-400 focus:ring-2 focus:ring-[#0a9ba5] read-only:cursor-not-allowed read-only:text-gray-400 read-only:focus:ring-0"
        :class="[boxStyle, hasIndent ? 'pl-12' : 'pl-4']"
        @input="onInput"
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

    <!-- Mensagem de erro -->
    <p v-if="error" class="text-xs font-medium text-red-600" role="alert">{{ error }}</p>
  </div>
</template>