<script setup>
/**
 * DocumentoClinicoView — receita ou atestado emitido, pronto para abrir e baixar em PDF
 *
 * Rota /paciente/documentos/:id. Lê GET /api/v1/documentos/{id} (o paciente só vê
 * documentos das próprias consultas). "Baixar PDF" usa a impressão do navegador
 * (Salvar como PDF); na impressão só a folha do documento aparece.
 *
 * A folha traz: logo da SimpleMark, médico que emitiu (nome, especialidade e
 * conselho), paciente, conteúdo, assinatura eletrônica e QR-Code de validação.
 */
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import AppHeader from '@/components/shared/AppHeader.vue'
import BackLink from '@/components/shared/BackLink.vue'
import { api } from '@/services/api'
import logo from '@/assets/logo-simple-mark.png'

const route = useRoute()

const documento = ref(null)
const carregando = ref(true)
const erro = ref('')

const ehReceita = computed(() => documento.value?.tipo === 'RECEITA')
const titulo = computed(() => (ehReceita.value ? 'RECEITA MÉDICA' : 'ATESTADO MÉDICO'))

const dataBR = (iso) => (iso ? new Date(`${iso}T00:00:00`).toLocaleDateString('pt-BR') : '—')

const emitidoEm = computed(() =>
  documento.value
    ? new Date(documento.value.data_emissao).toLocaleString('pt-BR', { dateStyle: 'long', timeStyle: 'short' })
    : '',
)

// Até quando a receita vale (contada da emissão)
const validaAte = computed(() => {
  if (!documento.value?.validade_dias) return null
  const d = new Date(documento.value.data_emissao)
  d.setDate(d.getDate() + documento.value.validade_dias)
  return d.toLocaleDateString('pt-BR')
})

// Fim do afastamento do atestado (último dia)
const afastamentoAte = computed(() => {
  const doc = documento.value
  if (!doc?.data_inicio || !doc?.dias_afastamento) return null
  const d = new Date(`${doc.data_inicio}T00:00:00`)
  d.setDate(d.getDate() + doc.dias_afastamento - 1)
  return d.toLocaleDateString('pt-BR')
})

function baixarPdf() {
  const nomeArquivo = `${ehReceita.value ? 'receita' : 'atestado'}-simplemark-${documento.value.documento_id}`
  const tituloOriginal = document.title
  document.title = nomeArquivo // vira o nome sugerido do PDF
  window.print()
  document.title = tituloOriginal
}

onMounted(async () => {
  try {
    documento.value = await api.get(`/api/v1/documentos/${route.params.id}`)
  } catch (e) {
    erro.value = e.message || 'Não foi possível carregar o documento.'
  } finally {
    carregando.value = false
  }
})
</script>

<template>
  <div class="flex min-h-screen flex-col bg-[#f8faff] print:bg-white">
    <div class="print:hidden">
      <AppHeader />
      <BackLink :to="{ name: 'meusAgendamentos' }" />
    </div>

    <main class="mx-auto w-full max-w-[820px] flex-1 px-6 pb-12 pt-4 print:max-w-none print:p-0">
      <p v-if="carregando" class="text-center text-sm text-gray-500">Carregando documento...</p>
      <p v-else-if="erro" class="rounded-lg bg-red-50 p-4 text-center text-sm text-red-700" role="alert">{{ erro }}</p>

      <template v-else-if="documento">
        <div class="mb-4 flex justify-end print:hidden">
          <button
            type="button"
            class="cursor-pointer rounded-lg bg-[#0b2f5b] px-5 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-[#0b417d]"
            @click="baixarPdf"
          >
            ⤓ Baixar PDF
          </button>
        </div>

        <!-- Folha do documento -->
        <article class="folha rounded-xl border border-gray-200 bg-white p-10 text-gray-900 shadow-sm print:rounded-none print:border-0 print:p-0 print:shadow-none">
          <!-- Cabeçalho: logo + médico -->
          <header class="flex items-start justify-between gap-6 border-b-2 border-[#0b2f5b] pb-5">
            <img :src="logo" alt="Simple Mark" class="h-16 w-auto" />
            <div class="text-right">
              <p class="text-lg font-bold text-[#0b2f5b]">{{ documento.profissional }}</p>
              <p class="text-sm text-gray-700">{{ documento.especialidade }}</p>
              <p v-if="documento.conselho" class="text-sm font-semibold text-gray-700">{{ documento.conselho }}</p>
              <p class="mt-1 text-xs text-gray-500">Teleconsulta · SimpleMark</p>
            </div>
          </header>

          <h1 class="my-6 text-center text-xl font-bold tracking-widest text-[#0b2f5b]">{{ titulo }}</h1>

          <!-- Paciente -->
          <section class="mb-6 grid gap-2 rounded-lg bg-[#f3f6fd] p-4 text-sm sm:grid-cols-3 print:bg-transparent print:border print:border-gray-300">
            <p><span class="text-gray-500">Paciente:</span> <strong>{{ documento.paciente.nome }}</strong></p>
            <p><span class="text-gray-500">CPF:</span> {{ documento.paciente.cpf }}</p>
            <p><span class="text-gray-500">Nascimento:</span> {{ dataBR(documento.paciente.data_nascimento) }}</p>
          </section>

          <!-- Receita -->
          <section v-if="ehReceita" class="mb-6">
            <ol class="flex flex-col gap-4">
              <li v-for="(m, i) in documento.medicamentos" :key="i" class="border-b border-dashed border-gray-300 pb-3">
                <p class="font-semibold">
                  {{ i + 1 }}. {{ m.medicamento }} <span class="font-normal text-gray-700">— {{ m.dosagem }}</span>
                </p>
                <p class="mt-1 text-sm"><span class="text-gray-500">Posologia:</span> {{ m.posologia }}</p>
                <p class="text-sm">
                  <span class="text-gray-500">Quantidade:</span> {{ m.quantidade }}
                  <template v-if="m.duracao_dias"> · <span class="text-gray-500">Duração:</span> {{ m.duracao_dias }} dias</template>
                </p>
              </li>
            </ol>
            <p v-if="documento.observacoes" class="mt-5 whitespace-pre-line text-sm">
              <span class="font-semibold">Recomendações:</span> {{ documento.observacoes }}
            </p>
            <p v-if="validaAte" class="mt-3 text-sm text-gray-700">
              Válida por {{ documento.validade_dias }} dias (até {{ validaAte }}).
            </p>
          </section>

          <!-- Atestado -->
          <section v-else class="mb-6 text-sm leading-relaxed">
            <p v-if="documento.observacoes" class="whitespace-pre-line">{{ documento.observacoes }}</p>
            <p class="mt-4">
              <span class="text-gray-500">Afastamento:</span>
              {{ documento.dias_afastamento }} {{ documento.dias_afastamento === 1 ? 'dia' : 'dias' }},
              de {{ dataBR(documento.data_inicio) }} a {{ afastamentoAte }}
            </p>
            <p v-if="documento.cid"><span class="text-gray-500">CID:</span> {{ documento.cid }}</p>
            <p v-if="documento.finalidade"><span class="text-gray-500">Finalidade:</span> {{ documento.finalidade }}</p>
          </section>

          <!-- Assinatura -->
          <section class="mt-10 flex flex-col items-center text-center text-sm">
            <span class="mb-1 w-72 border-t border-gray-500" aria-hidden="true" />
            <p class="font-semibold">{{ documento.profissional }}</p>
            <p class="text-gray-700">{{ documento.especialidade }}<template v-if="documento.conselho"> · {{ documento.conselho }}</template></p>
            <p class="mt-1 text-xs text-gray-500">Assinado eletronicamente em {{ emitidoEm }}</p>
          </section>

          <!-- Validação -->
          <footer class="mt-8 flex items-center gap-5 border-t border-gray-200 pt-5">
            <img
              :src="`data:image/png;base64,${documento.qr_code_base64}`"
              alt="QR-Code de validação"
              class="size-28 shrink-0"
            />
            <div class="min-w-0 text-xs text-gray-700">
              <p class="font-semibold text-[#0b2f5b]">Valide a autenticidade deste documento</p>
              <p class="mt-1">Aponte a câmera para o QR-Code ou acesse:</p>
              <p class="break-all text-[#0a9ba5]">{{ documento.url_validacao }}</p>
              <p class="mt-1">
                Código de verificação: <span class="font-mono font-semibold">{{ documento.codigo_verificacao }}</span>
              </p>
              <p class="mt-2 flex items-center gap-1 text-gray-500">
                <img :src="logo" alt="" class="h-4 w-auto" /> Documento emitido pela plataforma SimpleMark
              </p>
            </div>
          </footer>
        </article>
      </template>
    </main>
  </div>
</template>

<style scoped>
@media print {
  @page {
    size: A4;
    margin: 18mm;
  }
  /* Mantém cores e a logo na impressão */
  .folha {
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
}
</style>
