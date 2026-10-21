<script setup>
/**
 * FormButton — botão padrão de formulários e ações
 *
 * COMO USAR (na página):
 *
 *   import FormButton from '@/components/shared/FormButton.vue'
 *
 *   <FormButton>Salvar</FormButton>                              // primary (padrão)
 *   <FormButton type="submit">Entrar</FormButton>                // botão de envio de formulário
 *   <FormButton variant="text">Voltar</FormButton>               // só texto
 *   <FormButton variant="soft">Deixar Conta Inativa</FormButton> // ação secundária
 *   <FormButton variant="danger" icon="M6 18 18 6M6 6l12 12">    // destrutivo, com ícone
 *     Excluir Conta
 *   </FormButton>
 *   <FormButton variant="outline" icon="...">Editar</FormButton>          // branco com borda
 *   <FormButton variant="outline-danger" icon="...">Excluir</FormButton>  // branco com borda, texto vermelho
 *   <FormButton :disabled="carregando">Enviar</FormButton>       // desabilitado
 *   <FormButton @click="salvar">Salvar</FormButton>              // o click é repassado ao <button>
 *
 * PROPS
 *   variant   String  (padrão: 'primary')
 *               aparência do botão. Valores aceitos:
 *               - 'primary'        -> azul escuro, preenchido (ação principal)
 *               - 'text'           -> só texto, sem fundo (ex.: "Voltar")
 *               - 'soft'           -> azul claro (ação secundária, ex.: "Deixar Conta Inativa")
 *               - 'danger'         -> vermelho, preenchido (ação destrutiva, ex.: "Excluir Conta")
 *               - 'outline'        -> fundo branco com borda cinza (ex.: "Editar")
 *               - 'outline-danger' -> igual ao outline, texto vermelho (ex.: "Excluir")
 *               Qualquer outro valor gera aviso no console (validator).
 *   type      String  (padrão: 'button')
 *               tipo nativo do <button>: 'button', 'submit' ou 'reset'.
 *               Atenção: o padrão é 'button', então para enviar um <form>
 *               é preciso passar type="submit" explicitamente.
 *   icon      String  (padrão: '')
 *               caminho "d" de um SVG 24x24 (ex.: dos Heroicons). Quando informado,
 *               o ícone aparece à esquerda do texto. Vazio = sem ícone.
 *   disabled  Boolean (padrão: false)
 *               desabilita o botão (opacidade reduzida e cursor "not-allowed").
 *
 * SLOTS
 *   default   texto (ou conteúdo) exibido dentro do botão.
 *
 * EVENTOS
 *   Nenhum declarado. Como o componente tem um único elemento raiz (<button>),
 *   listeners como @click caem direto nele (fallthrough de atributos do Vue).
 *   Obs.: com `disabled`, o navegador não dispara o click.
 *
 * ESTILO
 *   Já vem com Tailwind: altura fixa h-11, cantos arredondados, texto sm semibold.
 *   Para criar uma nova variante, adicione uma chave em `styles` e inclua o nome
 *   no validator da prop `variant`.
 *
 * DEPENDÊNCIAS
 *   - Tailwind CSS
 */

defineProps({
  variant: {
    type: String,
    default: 'primary',
    validator: (v) => ['primary', 'text', 'soft', 'danger', 'outline', 'outline-danger'].includes(v),
  },
  type: { type: String, default: 'button' },
  icon: { type: String, default: '' },
  disabled: { type: Boolean, default: false },
})

const styles = {
  primary: 'bg-[#042d5c] px-6 text-white hover:bg-[#0b3f7a]',
  text: 'px-4 text-gray-700 hover:text-[#042d5c]',
  soft: 'bg-[#e1e8fb] px-6 text-[#0b2f5b] hover:bg-[#d3ddf8]',
  danger: 'bg-red-700 px-6 text-white hover:bg-red-800',
  outline: 'border border-gray-200 bg-white px-4 text-[#0b2f5b] hover:bg-gray-50',
  'outline-danger': 'border border-gray-200 bg-white px-4 text-red-700 hover:bg-red-50',
}
</script>

<template>
  <button
    :type="type"
    :disabled="disabled"
    class="inline-flex h-11 cursor-pointer items-center justify-center gap-2 rounded-lg text-sm font-semibold transition-colors disabled:cursor-not-allowed disabled:opacity-50"
    :class="styles[variant]"
  >
    <svg
      v-if="icon"
      class="size-4"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      stroke-width="2.5"
      stroke="currentColor"
      aria-hidden="true"
    >
      <path stroke-linecap="round" stroke-linejoin="round" :d="icon" />
    </svg>
    <slot />
  </button>
</template>