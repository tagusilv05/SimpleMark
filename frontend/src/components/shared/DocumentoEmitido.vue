<script setup>
/**
 * DocumentoEmitido — confirmação de receita/atestado emitido, com QR-Code de validação
 *
 *   <DocumentoEmitido :documento="receitaEmitida" titulo="Receita emitida" />
 *
 * PROPS
 *   documento  Object  resposta de POST /api/v1/receitas ou /api/v1/atestados
 *                      (usa codigo_verificacao, url_validacao, qr_code_base64,
 *                       data_emissao e paciente.nome)
 *   titulo     String  texto do cabeçalho
 */
import { computed } from 'vue'

const props = defineProps({
  documento: { type: Object, required: true },
  titulo: { type: String, default: 'Documento emitido' },
})

const emitidoEm = computed(() =>
  new Date(props.documento.data_emissao).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' }),
)
</script>

<template>
  <section
    class="mx-auto flex w-full max-w-180 flex-col items-center gap-6 rounded-xl border border-[#bfe5e2] bg-white p-6 shadow-[0_2px_12px_rgba(11,47,91,0.06)] sm:flex-row"
    role="status"
  >
    <img
      :src="`data:image/png;base64,${documento.qr_code_base64}`"
      alt="QR-Code para validar o documento"
      class="size-36 shrink-0 rounded-lg border border-gray-200"
    />

    <div class="flex min-w-0 flex-1 flex-col gap-2 text-sm text-gray-800">
      <p class="flex items-center gap-2 text-base font-semibold text-[#0b6e66]">
        <span aria-hidden="true">✓</span> {{ titulo }}
      </p>
      <p>Paciente: <strong>{{ documento.paciente?.nome }}</strong></p>
      <p>Emitido em {{ emitidoEm }}</p>
      <p>
        Código de verificação:
        <span class="font-mono font-semibold tracking-wider text-[#08283a]">{{ documento.codigo_verificacao }}</span>
      </p>
      <a
        :href="documento.url_validacao"
        target="_blank"
        rel="noopener"
        class="truncate text-[#0a9ba5] underline"
      >
        Validar documento
      </a>
    </div>
  </section>
</template>
