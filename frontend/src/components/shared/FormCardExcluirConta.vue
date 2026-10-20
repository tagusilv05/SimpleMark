<script setup>
import AccountActionCard from './AccountActionCard.vue'

/**
 * FormCardExcluirConta — card "Desativar ou Excluir Conta".
 * Junta duas caixas (AccountActionCard): desativação temporária e exclusão definitiva.
 * Os textos, ícones e cores já vêm definidos aqui dentro.
 *
 * COMO USAR:
 *   <FormCardExcluirConta @desativar="desativarConta" @excluir="excluirConta" />
 *
 * PROPS
 *   title  String  título do card (padrão: "Desativar ou Excluir Conta")
 *
 * EVENTOS
 *   @desativar  confirmou "Deixar Conta Inativa" (com "Estou Ciente" marcado)
 *   @excluir    confirmou "Excluir Conta" (com "Estou Ciente" marcado)
 *   O componente não chama a API: a página decide o que fazer em cada evento.
 */
defineProps({
  title: { type: String, default: 'Desativar ou Excluir Conta' },
})

const emit = defineEmits(['desativar', 'excluir'])

// ---- Ícones (caminho "d" de SVGs 24x24) ----
const icons = {
  pauseCircle: 'M14.25 9v6m-4.5 0V9M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z',
  pause: 'M15.75 5.25v13.5m-7.5-13.5v13.5',
  trash:
    'm14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0',
  // Triângulo de alerta PREENCHIDO (para a etiqueta "Ação Irreversível")
  warningSolid:
    'M9.401 3.003c1.155-2 4.043-2 5.197 0l7.355 12.748c1.154 2-.29 4.5-2.599 4.5H4.645c-2.309 0-3.752-2.5-2.598-4.5L9.4 3.003ZM12 8.25a.75.75 0 0 1 .75.75v3.75a.75.75 0 0 1-1.5 0V9a.75.75 0 0 1 .75-.75Zm0 8.25a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Z',
}
</script>

<template>
  <section class="flex flex-col gap-6 rounded-xl bg-white p-8 shadow-[0_2px_12px_rgba(11,47,91,0.08)]">
    <h2 v-if="title" class="text-2xl font-medium text-[#0b2f5b]">{{ title }}</h2>

    <AccountActionCard
      title="Desativação Temporária da Conta"
      description="Se você deseja fazer uma pausa, pode deixar sua conta inativa temporariamente. Seu histórico de consultas, receitas e dados médicos serão preservados com segurança e você poderá reativar seu acesso a qualquer momento."
      :icon="icons.pauseCircle"
      badge="Ação Reversível"
      button-label="Deixar Conta Inativa"
      :button-icon="icons.pause"
      @confirm="emit('desativar')"
    />

    <AccountActionCard
      tone="danger"
      title="Exclusão Definitiva da Conta"
      description="Ao confirmar a exclusão, todos os seus dados cadastrais, histórico de consultas e receitas serão removidos de forma definitiva e irrecuperável de acordo com as normas da LGPD."
      :icon="icons.trash"
      badge="Ação Irreversível"
      :badge-icon="icons.warningSolid"
      button-label="Excluir Conta"
      :button-icon="icons.trash"
      @confirm="emit('excluir')"
    />
  </section>
</template>
