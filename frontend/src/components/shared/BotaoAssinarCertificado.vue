<script setup>
/**
 * BotaoAssinarCertificado — botão escuro "Assinar com Certificado Digital e Emitir ..."
 *
 * COMO USAR (na página):
 *
 *   import BotaoAssinarCertificado from '@/components/shared/BotaoAssinarCertificado.vue'
 *
 *   <BotaoAssinarCertificado documento="Receita" @click="emitir" />
 *   <BotaoAssinarCertificado documento="Atestado" :disabled="enviando" />
 *
 * PROPS
 *   documento  String  (obrigatória)  nome do documento no final do texto.
 *   disabled   Boolean (padrão: false)
 *
 * EVENTOS
 *   Nenhum declarado: @click cai direto no <button> (fallthrough).
 *
 * DEPENDÊNCIAS
 *   - Tailwind CSS
 */

defineProps({
  documento: { type: String, required: true },
  disabled: { type: Boolean, default: false },
})
</script>

<template>
  <button
    type="button"
    :disabled="disabled"
    class="mx-auto inline-flex h-13 w-full max-w-130 cursor-pointer items-center justify-center gap-3 rounded-lg bg-[#08283a] px-6 text-sm font-medium text-white shadow-[0_4px_12px_rgba(8,40,58,0.25)] transition-colors hover:bg-[#0d3a52] disabled:cursor-not-allowed disabled:opacity-50"
  >
    <!-- Caneta de assinatura -->
    <svg
      class="size-5 text-[#14a39a]"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      stroke-width="1.8"
      stroke="currentColor"
      aria-hidden="true"
    >
      <path
        stroke-linecap="round"
        stroke-linejoin="round"
        d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931ZM3 21h4M3 13l4-4m-1 7 7-7"
      />
    </svg>
    Assinar com Certificado Digital e Emitir {{ documento }}
  </button>
</template>
