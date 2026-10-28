<script setup>
/**
 * OuvidoriaView — página "Ouvidoria" (abertura de manifestação)
 *
 * Fluxo: home -> "Ouvidoria" (cabeçalho) -> esta tela (rota `ouvidoria`)
 *        -> Voltar -> home.
 *
 * O formulário reúne: identificação do solicitante, tipo de manifestação, código da
 * consulta (opcional), assunto, descrição (até 1500 caracteres), anexos (opcional) e o
 * aceite do tratamento de dados (LGPD).
 *
 * Componentes usados:
 *   - AppHeader, FormField (visual "filled"), FormTextarea (visual "filled"), FormButton
 */

import { reactive, ref } from 'vue'
import AppHeader from '@/components/shared/AppHeader.vue'
import FormField from '@/components/shared/FormField.vue'
import FormTextarea from '@/components/shared/FormTextarea.vue'
import FormButton from '@/components/shared/FormButton.vue'

// Caminhos "d" dos ícones (Heroicons 24x24, contorno)
const icons = {
  voltar: 'M10.5 19.5 3 12m0 0 7.5-7.5M3 12h18',
  paciente:
    'M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z',
  profissional:
    'M9 6.75V5.25A2.25 2.25 0 0 1 11.25 3h1.5A2.25 2.25 0 0 1 15 5.25v1.5M4.5 6.75h15a1.5 1.5 0 0 1 1.5 1.5v10.5a1.5 1.5 0 0 1-1.5 1.5h-15A1.5 1.5 0 0 1 3 18.75V8.25a1.5 1.5 0 0 1 1.5-1.5ZM12 10.5v6m-3-3h6',
  reclamacao:
    'M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.008v.008H12v-.008Z',
  teleconsulta:
    'm15.75 10.5 4.72-4.72a.75.75 0 0 1 1.28.53v11.38a.75.75 0 0 1-1.28.53l-4.72-4.72M12 18.75H4.5a2.25 2.25 0 0 1-2.25-2.25V9m12.841 9.091L16.5 19.5m-1.409-1.409c.407-.407.659-.97.659-1.591v-9a2.25 2.25 0 0 0-2.25-2.25h-9c-.621 0-1.184.252-1.591.659m12.182 12.182L2.909 5.909M1.5 4.5l1.409 1.409',
  sugestao:
    'M12 18v-5.25m0 0a6.01 6.01 0 0 0 1.5-.189m-1.5.189a6.01 6.01 0 0 1-1.5-.189m3.75 7.478a12.06 12.06 0 0 1-4.5 0m3.75 2.383a14.406 14.406 0 0 1-3 0M14.25 18v-.192c0-.983.658-1.823 1.508-2.316a7.5 7.5 0 1 0-7.517 0c.85.493 1.509 1.333 1.509 2.316V18',
  elogio:
    'M6.633 10.25c.806 0 1.533-.446 2.031-1.08a9.041 9.041 0 0 1 2.861-2.4c.723-.384 1.35-.956 1.653-1.715a4.498 4.498 0 0 0 .322-1.672V2.75a.75.75 0 0 1 .75-.75 2.25 2.25 0 0 1 2.25 2.25c0 1.152-.26 2.243-.723 3.218-.266.558.107 1.282.725 1.282m0 0h3.126c1.026 0 1.945.694 2.054 1.715.045.422.068.85.068 1.285a11.95 11.95 0 0 1-2.649 7.521c-.388.482-.987.729-1.605.729H13.48c-.483 0-.964-.078-1.423-.23l-3.114-1.04a4.501 4.501 0 0 0-1.423-.23H5.904m10.598-9.75H14.25M5.904 18.5c.083.205.173.405.27.602.197.4-.078.898-.523.898h-.908c-.889 0-1.713-.518-1.972-1.368a12 12 0 0 1-.521-3.507c0-1.553.295-3.036.831-4.398C3.387 9.953 4.167 9.5 5 9.5h1.053c.472 0 .745.556.5.96a8.958 8.958 0 0 0-1.302 4.665c0 1.194.232 2.333.654 3.375Z',
  duvida:
    'M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 5.25h.008v.008H12v-.008Z',
  ticket:
    'M16.5 6v.75m0 3v.75m0 3v.75m0 3V18m-9-5.25h5.25M7.5 15h3M3.375 5.25c-.621 0-1.125.504-1.125 1.125v3.026a2.999 2.999 0 0 1 0 5.198v3.026c0 .621.504 1.125 1.125 1.125h17.25c.621 0 1.125-.504 1.125-1.125v-3.026a2.999 2.999 0 0 1 0-5.198V6.375c0-.621-.504-1.125-1.125-1.125H3.375Z',
  assunto: 'M5.25 6h13.5M12 6v12.75',
  nuvem:
    'M12 16.5V9.75m0 0 3 3m-3-3-3 3M6.75 19.5a4.5 4.5 0 0 1-1.41-8.775 5.25 5.25 0 0 1 10.233-2.33 3 3 0 0 1 3.758 3.848A3.752 3.752 0 0 1 18 19.5H6.75Z',
  arquivo:
    'M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z',
  remover: 'M6 18 18 6M6 6l12 12',
  ok: 'M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z',
}

const solicitantes = [
  { id: 'paciente', label: 'Sou Paciente', icon: icons.paciente },
  { id: 'profissional', label: 'Sou Profissional de Saúde', icon: icons.profissional },
]

const tipos = [
  { id: 'reclamacao', label: 'Reclamação', icon: icons.reclamacao },
  { id: 'teleconsulta', label: 'Problema em Teleconsulta', icon: icons.teleconsulta },
  { id: 'sugestao', label: 'Sugestão', icon: icons.sugestao },
  { id: 'elogio', label: 'Elogio', icon: icons.elogio },
  { id: 'duvida', label: 'Dúvida', icon: icons.duvida },
]

/* ---------- Limites ---------- */
const DESCRICAO_MAX = 1500
const ARQUIVOS_MAX = 5
const TAMANHO_MAX = 10 * 1024 * 1024 // 10 MB por arquivo
const EXTENSOES = ['pdf', 'png', 'jpg', 'jpeg']

/* ---------- Estado ---------- */
const solicitante = ref('paciente')
const tipo = ref('reclamacao')
const form = reactive({ codigo: '', assunto: '', descricao: '' })
const aceite = ref(false)
const arquivos = ref([]) // [{ id, file }]
const errors = reactive({})
const carregando = ref(false)
const enviado = ref(false)

/* ---------- Filtros de digitação ---------- */
const filtros = {
  // Código da consulta: letras (maiúsculas), números e hífen — ex.: SM-8942-SP
  codigo: (v) => v.toUpperCase().replace(/[^A-Z0-9-]/g, '').slice(0, 20),
  assunto: (v) => v.replace(/^\s/, '').replace(/\s{2,}/g, ' ').slice(0, 100),
  descricao: (v) => v.slice(0, DESCRICAO_MAX),
}

function atualizar(campo, valor) {
  form[campo] = filtros[campo](valor)
  delete errors[campo]
}

/* ---------- Anexos ---------- */
const inputArquivo = ref(null)
const arrastando = ref(false)
let proximoId = 0

const extensao = (nome) => nome.split('.').pop().toLowerCase()

function tamanhoLegivel(bytes) {
  return bytes < 1024 * 1024
    ? `${Math.max(1, Math.round(bytes / 1024))} KB`
    : `${(bytes / (1024 * 1024)).toFixed(1).replace('.', ',')} MB`
}

function adicionarArquivos(lista) {
  const problemas = []
  for (const file of lista) {
    if (arquivos.value.length >= ARQUIVOS_MAX) {
      problemas.push(`Limite de ${ARQUIVOS_MAX} arquivos.`)
      break
    }
    if (!EXTENSOES.includes(extensao(file.name))) {
      problemas.push(`"${file.name}": formato não aceito (use PDF, PNG, JPG ou JPEG).`)
    } else if (file.size > TAMANHO_MAX) {
      problemas.push(`"${file.name}": maior que 10 MB.`)
    } else if (arquivos.value.some((a) => a.file.name === file.name && a.file.size === file.size)) {
      problemas.push(`"${file.name}": já foi adicionado.`)
    } else {
      arquivos.value.push({ id: ++proximoId, file })
    }
  }
  errors.arquivos = problemas.join(' ')
  if (!problemas.length) delete errors.arquivos
}

function aoEscolherArquivos(event) {
  adicionarArquivos(Array.from(event.target.files ?? []))
  event.target.value = '' // permite escolher o mesmo arquivo de novo
}

function aoSoltarArquivos(event) {
  arrastando.value = false
  adicionarArquivos(Array.from(event.dataTransfer?.files ?? []))
}

function removerArquivo(id) {
  arquivos.value = arquivos.value.filter((a) => a.id !== id)
  delete errors.arquivos
}

function limparErroAceite() {
  delete errors.aceite
}

/* ---------- Validação e envio ---------- */
function validar() {
  const e = {}
  if (form.assunto.trim().length < 5) e.assunto = 'Informe o assunto (mínimo de 5 caracteres).'
  if (form.descricao.trim().length < 20) {
    e.descricao = 'Descreva os fatos com mais detalhes (mínimo de 20 caracteres).'
  }
  if (!aceite.value) e.aceite = 'É necessário aceitar o termo para enviar a manifestação.'

  const arquivosErro = errors.arquivos
  Object.keys(errors).forEach((k) => delete errors[k])
  Object.assign(errors, e)
  if (arquivosErro) errors.arquivos = arquivosErro
  return Object.keys(e).length === 0
}

function reiniciar() {
  solicitante.value = 'paciente'
  tipo.value = 'reclamacao'
  form.codigo = ''
  form.assunto = ''
  form.descricao = ''
  arquivos.value = []
  aceite.value = false
  Object.keys(errors).forEach((k) => delete errors[k])
}

async function enviar() {
  if (carregando.value) return
  enviado.value = false
  if (!validar()) {
    // O formulário é longo: leva o foco até o primeiro problema
    document.querySelector('[aria-invalid="true"], [data-erro="true"]')?.focus()
    return
  }

  carregando.value = true
  try {
    // TODO: enviar a manifestação para o backend, por exemplo:
    // const dados = new FormData()
    // dados.append('solicitante', solicitante.value)
    // dados.append('tipo', tipo.value)
    // dados.append('codigo_consulta', form.codigo)
    // dados.append('assunto', form.assunto.trim())
    // dados.append('descricao', form.descricao.trim())
    // arquivos.value.forEach((a) => dados.append('anexos', a.file))
    // await ouvidoriaService.abrirManifestacao(dados)

    reiniciar()
    enviado.value = true
    window.scrollTo({ top: 0, behavior: 'smooth' })
  } catch {
    errors.geral = 'Não foi possível enviar a manifestação. Tente novamente.'
  } finally {
    carregando.value = false
  }
}
</script>

<template>
  <div class="flex min-h-screen flex-col bg-[#f8faff]">
    <AppHeader />

    <main class="mx-auto w-full max-w-7xl flex-1 px-6 pb-20 sm:px-12">
      <!-- No desktop: "Voltar" fica à esquerda e o conteúdo numa coluna central de 812px -->
      <div class="lg:grid lg:grid-cols-[1fr_minmax(0,812px)_1fr] lg:gap-x-6">
        <!-- Voltar -->
        <RouterLink
          :to="{ name: 'home' }"
          class="inline-flex items-center gap-1.5 self-start justify-self-start py-2 text-sm font-bold text-[#0b2f5b] transition-opacity hover:opacity-70 lg:mt-1"
        >
          <svg
            class="size-4"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="2"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path stroke-linecap="round" stroke-linejoin="round" :d="icons.voltar" />
          </svg>
          Voltar
        </RouterLink>

        <div class="min-w-0">
          

          <section
            class="mt-10 rounded-2xl bg-white p-6 shadow-[0_2px_12px_rgba(11,47,91,0.06)] sm:p-8 lg:mt-16"
            aria-labelledby="titulo-manifestacao"
          >
            <!-- Confirmação de envio -->
            <div
              v-if="enviado"
              class="mb-6 flex items-start gap-3 rounded-xl bg-[#cdf7e8] p-4 text-[#00436b]"
              role="status"
            >
              <svg
                class="size-6 shrink-0"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke-width="1.5"
                stroke="currentColor"
                aria-hidden="true"
              >
                <path stroke-linecap="round" stroke-linejoin="round" :d="icons.ok" />
              </svg>
              <p class="text-sm leading-6">
                <strong class="font-bold">Manifestação enviada com sucesso!</strong>
                Nossa equipe fará a análise e retornará o mais breve possível.
              </p>
            </div>

            <h2 id="titulo-manifestacao" class="text-2xl font-medium text-[#0b2f5b]">
              Abertura de Manifestação
            </h2>
            <p class="mt-1 max-w-xl text-[15px] leading-6 text-gray-700">
              Informe a nossa equipe sobre qualquer dúvida, reclamação ou sugestão que você possa ter.
              Preencha os dados com o máximo de precisão para agilizar a análise técnica.
            </p>

            <form class="mt-8 flex flex-col gap-6" novalidate @submit.prevent="enviar">
              <!-- Identificação do solicitante -->
              <div>
                <p id="rotulo-solicitante" class="text-sm font-bold text-gray-900">
                  Identificação do Solicitante
                </p>
                <div
                  class="mt-2 grid grid-cols-1 gap-1 rounded-xl bg-[#eef1fe] p-1 sm:grid-cols-2"
                  role="radiogroup"
                  aria-labelledby="rotulo-solicitante"
                >
                  <button
                    v-for="op in solicitantes"
                    :key="op.id"
                    type="button"
                    role="radio"
                    :aria-checked="solicitante === op.id"
                    class="inline-flex h-11 cursor-pointer items-center justify-center gap-2 rounded-lg px-4 text-sm font-semibold transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0a9ba5]"
                    :class="
                      solicitante === op.id
                        ? 'bg-[#00436b] text-white'
                        : 'text-gray-600 hover:text-[#00436b]'
                    "
                    @click="solicitante = op.id"
                  >
                    <svg
                      class="size-4"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke-width="1.75"
                      stroke="currentColor"
                      aria-hidden="true"
                    >
                      <path stroke-linecap="round" stroke-linejoin="round" :d="op.icon" />
                    </svg>
                    {{ op.label }}
                  </button>
                </div>
              </div>

              <!-- Tipo de manifestação -->
              <div>
                <p id="rotulo-tipo" class="text-sm font-bold text-gray-900">Tipo de Manifestação</p>
                <div
                  class="mt-2 flex flex-wrap gap-3"
                  role="radiogroup"
                  aria-labelledby="rotulo-tipo"
                >
                  <button
                    v-for="op in tipos"
                    :key="op.id"
                    type="button"
                    role="radio"
                    :aria-checked="tipo === op.id"
                    class="inline-flex h-9 cursor-pointer items-center gap-2 rounded-full px-4 text-sm font-semibold transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0a9ba5]"
                    :class="
                      tipo === op.id
                        ? 'bg-[#0b6b62] text-white'
                        : 'bg-[#eef1fe] text-gray-700 hover:text-[#00436b]'
                    "
                    @click="tipo = op.id"
                  >
                    <svg
                      class="size-4"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke-width="1.75"
                      stroke="currentColor"
                      aria-hidden="true"
                    >
                      <path stroke-linecap="round" stroke-linejoin="round" :d="op.icon" />
                    </svg>
                    {{ op.label }}
                  </button>
                </div>
              </div>

              <!-- Código da consulta (opcional) + assunto -->
              <div class="grid grid-cols-1 gap-6 md:grid-cols-2">
                <FormField
                  label="Código da Consulta / Atendimento (Opcional)"
                  placeholder="Ex.: SM-8942-SP"
                  :icon="icons.ticket"
                  :model-value="form.codigo"
                  :error="errors.codigo"
                  @update:model-value="atualizar('codigo', $event)"
                />

                <FormField
                  label="Assunto Resumido"
                  placeholder="Ex.: Dificuldade de conexão no link da videochamada"
                  :icon="icons.assunto"
                  :model-value="form.assunto"
                  :error="errors.assunto"
                  @update:model-value="atualizar('assunto', $event)"
                />
              </div>

              <!-- Descrição detalhada -->
              <FormTextarea
                label="Descrição Detalhada dos Fatos"
                variant="filled"
                placeholder="Descreva com detalhes o ocorrido, data, hora, profissional envolvido e impacto gerado..."
                :rows="3"
                :maxlength="DESCRICAO_MAX"
                :counter="false"
                :model-value="form.descricao"
                :error="errors.descricao"
                @update:model-value="atualizar('descricao', $event)"
              >
                <template #hint>
                  <span class="text-xs text-gray-600">
                    {{ form.descricao.length }} / {{ DESCRICAO_MAX }} caracteres
                  </span>
                </template>
              </FormTextarea>

              <!-- Anexos -->
              <div>
                <p id="rotulo-anexos" class="text-sm font-bold text-gray-900">
                  Comprovantes, Laudos ou Capturas de Tela (Opcional)
                </p>

                <div
                  class="mt-2 flex flex-col items-center gap-3 rounded-xl px-4 py-6 text-center transition-colors"
                  :class="
                    arrastando
                      ? 'bg-[#e1e8fb] outline-2 outline-dashed outline-[#0b6b62]'
                      : 'bg-[#eef1fe]'
                  "
                  @dragover.prevent="arrastando = true"
                  @dragleave.prevent="arrastando = false"
                  @drop.prevent="aoSoltarArquivos"
                >
                  <span class="grid size-12 place-items-center rounded-full bg-white text-[#00436b]">
                    <svg
                      class="size-6"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke-width="1.5"
                      stroke="currentColor"
                      aria-hidden="true"
                    >
                      <path stroke-linecap="round" stroke-linejoin="round" :d="icons.nuvem" />
                    </svg>
                  </span>

                  <p class="text-sm font-bold text-gray-900">
                    Arraste e solte arquivos aqui, ou
                    <button
                      type="button"
                      class="cursor-pointer font-bold text-[#0b6b62] underline underline-offset-2 hover:opacity-80 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0a9ba5]"
                      aria-describedby="rotulo-anexos"
                      @click="inputArquivo.click()"
                    >
                      procure no dispositivo
                    </button>
                  </p>
                  <p class="text-xs text-gray-600">
                    Formatos aceitos: PDF, PNG, JPG ou JPEG (máx. 10MB por arquivo)
                  </p>

                  <input
                    ref="inputArquivo"
                    type="file"
                    class="hidden"
                    multiple
                    accept=".pdf,.png,.jpg,.jpeg,application/pdf,image/png,image/jpeg"
                    @change="aoEscolherArquivos"
                  />
                </div>

                <p v-if="errors.arquivos" class="mt-2 text-xs font-medium text-red-600" role="alert">
                  {{ errors.arquivos }}
                </p>

                <ul v-if="arquivos.length" class="mt-3 flex flex-col gap-2">
                  <li
                    v-for="item in arquivos"
                    :key="item.id"
                    class="flex items-center gap-3 rounded-lg border border-gray-200 bg-white px-3 py-2"
                  >
                    <svg
                      class="size-5 shrink-0 text-[#00436b]"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke-width="1.5"
                      stroke="currentColor"
                      aria-hidden="true"
                    >
                      <path stroke-linecap="round" stroke-linejoin="round" :d="icons.arquivo" />
                    </svg>
                    <span class="min-w-0 flex-1 truncate text-sm text-gray-800">
                      {{ item.file.name }}
                    </span>
                    <span class="shrink-0 text-xs text-gray-500">
                      {{ tamanhoLegivel(item.file.size) }}
                    </span>
                    <button
                      type="button"
                      class="grid size-7 shrink-0 cursor-pointer place-items-center rounded-md text-gray-500 transition-colors hover:bg-[#eef1fe] hover:text-[#00436b] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0a9ba5]"
                      :aria-label="`Remover ${item.file.name}`"
                      @click="removerArquivo(item.id)"
                    >
                      <svg
                        class="size-4"
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke-width="2"
                        stroke="currentColor"
                        aria-hidden="true"
                      >
                        <path stroke-linecap="round" stroke-linejoin="round" :d="icons.remover" />
                      </svg>
                    </button>
                  </li>
                </ul>
              </div>

              <!-- Aceite (LGPD) -->
              <div>
                <label
                  class="flex cursor-pointer items-start gap-3 rounded-xl bg-[#eef1fe] p-4"
                  :class="errors.aceite ? 'ring-2 ring-red-400' : ''"
                >
                  <input
                    v-model="aceite"
                    type="checkbox"
                    class="mt-0.5 size-4 shrink-0 cursor-pointer accent-[#00436b]"
                    :data-erro="!!errors.aceite"
                    @change="limparErroAceite"
                  />
                  <span class="text-xs leading-5 text-gray-700">
                    Declaro que as informações prestadas são verídicas e autorizo o tratamento dos
                    dados pessoais e sensíveis compartilhados estritamente para a finalidade de
                    mediação desta demanda pela Ouvidoria do Simple Mark, nos termos da Lei Geral de
                    Proteção de Dados (Lei nº 13.709/2018) e resoluções do CFM.
                  </span>
                </label>
                <p v-if="errors.aceite" class="mt-2 text-xs font-medium text-red-600" role="alert">
                  {{ errors.aceite }}
                </p>
              </div>

              <p v-if="errors.geral" class="text-sm font-medium text-red-600" role="alert">
                {{ errors.geral }}
              </p>

              <div class="flex justify-center">
                <FormButton type="submit" class="h-12! px-8" :disabled="carregando">
                  {{ carregando ? 'Enviando...' : 'Enviar Manifestação' }}
                </FormButton>
              </div>
            </form>
          </section>
        </div>
      </div>
    </main>
  </div>
</template>