<script setup>
/**
 * DuvidasFrequentesView — página "Dúvidas Frequentes"
 *
 * Fluxo: home -> rodapé "Dúvidas Frequentes" -> esta tela (rota `duvidas-frequentes`)
 *        -> Voltar -> home.
 *
 * Estrutura:
 *   - Cabeçalho (AppHeader) e link "Voltar"
 *   - Busca + filtros por categoria
 *   - Lista de perguntas (sanfona: clique para abrir/fechar; várias podem ficar abertas)
 *   - Chamada para a Ouvidoria
 *
 * Para incluir uma pergunta, acrescente um item ao array `perguntas`:
 *   { id, categoria, pergunta, resposta, link? }
 *   `categoria` precisa ser um dos ids de `categorias`; `link` ({ to, label }) é opcional
 *   e aparece como atalho no fim da resposta.
 *
 * ⚠️ As respostas descrevem apenas o que a plataforma já comunica (agendamento, teleconsulta
 * no navegador, receitas digitais, Pix/cartão, validação de profissionais). Revise-as se as
 * regras do projeto mudarem.
 */

import { computed, ref } from 'vue'
import AppHeader from '@/components/shared/AppHeader.vue'
import FormField from '@/components/shared/FormField.vue'

// Caminhos "d" dos ícones (Heroicons 24x24, contorno)
const icons = {
  voltar: 'M10.5 19.5 3 12m0 0 7.5-7.5M3 12h18',
  busca: 'm21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z',
  seta: 'm19.5 8.25-7.5 7.5-7.5-7.5',
}

const categorias = [
  { id: 'todas', label: 'Todas' },
  { id: 'pacientes', label: 'Pacientes' },
  { id: 'profissionais', label: 'Profissionais' },
  { id: 'pagamentos', label: 'Pagamentos' },
  { id: 'seguranca', label: 'Segurança e Privacidade' },
]

const perguntas = [
  {
    id: 'agendar',
    categoria: 'pacientes',
    pergunta: 'Como agendo uma consulta?',
    resposta:
      'Busque o profissional pela especialidade, visualize a agenda dele em tempo real, escolha o melhor dia e horário e confirme o pagamento. Tudo é feito online, em poucos cliques.',
  },
  {
    id: 'aplicativo',
    categoria: 'pacientes',
    pergunta: 'Preciso baixar algum aplicativo para a teleconsulta?',
    resposta:
      'Não. A teleconsulta acontece direto no navegador, pelo link seguro da sala virtual, no computador ou no celular.',
  },
  {
    id: 'receitas',
    categoria: 'pacientes',
    pergunta: 'Como recebo receitas, pedidos de exames e atestados?',
    resposta:
      'Ao final do atendimento, o profissional pode emitir esses documentos digitalmente. Eles são disponibilizados na tela, após a consulta.',
  },
  {
    id: 'senha',
    categoria: 'pacientes',
    pergunta: 'Esqueci minha senha. O que faço?',
    resposta:
      'Na tela de login, clique em "Esqueceu a senha?", informe o seu e-mail e digite o código de recuperação que você receber. Depois, crie uma nova senha.',
  },
  {
    id: 'emergencia',
    categoria: 'pacientes',
    pergunta: 'Posso usar a plataforma em caso de emergência?',
    resposta:
      'Não. A teleconsulta não substitui o atendimento de urgência ou emergência. Em situações de risco, procure um pronto atendimento ou ligue para o SAMU (192).',
  },
  {
    id: 'cadastro-prof',
    categoria: 'profissionais',
    pergunta: 'Como me cadastro como profissional de saúde?',
    resposta:
      'Crie a sua conta na opção de cadastro para profissionais e informe seus dados pessoais e o registro profissional. O perfil passa por uma validação da nossa equipe antes de ser liberado.',
    link: { to: { name: 'cadastro/profissional' }, label: 'Cadastrar como profissional' },
  },
  {
    id: 'agenda',
    categoria: 'profissionais',
    pergunta: 'Como configuro a minha agenda?',
    resposta:
      'No seu painel, acesse a configuração de agenda e defina os dias e horários de atendimento. Os pacientes enxergam apenas os horários disponíveis.',
  },
  {
    id: 'atender',
    categoria: 'profissionais',
    pergunta: 'Como realizo o atendimento?',
    resposta:
      'Você atende pelo navegador, em uma sala virtual segura, e pode emitir receitas e atestados digitais ao final da consulta.',
  },
  {
    id: 'formas-pagamento',
    categoria: 'pagamentos',
    pergunta: 'Quais formas de pagamento são aceitas?',
    resposta:
      'Você pode pagar por Pix, com confirmação imediata, ou por cartão de crédito, em ambiente criptografado.',
  },
  {
    id: 'confirmacao',
    categoria: 'pagamentos',
    pergunta: 'Quando a minha consulta é confirmada?',
    resposta:
      'A consulta é confirmada após a confirmação do pagamento. As regras de cancelamento e remarcação são apresentadas no momento do agendamento.',
  },
  {
    id: 'dados',
    categoria: 'seguranca',
    pergunta: 'Meus dados estão seguros?',
    resposta:
      'Tratamos os dados pessoais em conformidade com a LGPD, e as teleconsultas acontecem em ambiente privativo e criptografado. Você encontra todos os detalhes na Política de Privacidade.',
    link: { to: { name: 'privacidade' }, label: 'Ler a Política de Privacidade' },
  },
  {
    id: 'direitos',
    categoria: 'seguranca',
    pergunta: 'Como exerço meus direitos sobre os meus dados?',
    resposta:
      'Você pode solicitar acesso, correção ou eliminação dos seus dados, entre outros direitos previstos na LGPD, pela página de Ouvidoria.',
    link: { to: { name: 'ouvidoria' }, label: 'Ir para a Ouvidoria' },
  },
  {
    id: 'reclamacao',
    categoria: 'seguranca',
    pergunta: 'Como faço uma reclamação, sugestão ou elogio?',
    resposta:
      'Use a página de Ouvidoria: escolha o tipo de manifestação, descreva os fatos e, se quiser, anexe comprovantes.',
    link: { to: { name: 'ouvidoria' }, label: 'Abrir uma manifestação' },
  },
]

/* ---------- Filtros ---------- */
const categoriaAtiva = ref('todas')
const busca = ref('')
const abertas = ref([]) // ids das perguntas abertas

// Compara sem acento e sem diferenciar maiúsculas (ex.: "duvida" acha "dúvida")
const normalizar = (t) =>
  t
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()

const filtradas = computed(() => {
  const termo = normalizar(busca.value.trim())
  return perguntas.filter((p) => {
    const daCategoria = categoriaAtiva.value === 'todas' || p.categoria === categoriaAtiva.value
    const doTexto = !termo || normalizar(`${p.pergunta} ${p.resposta}`).includes(termo)
    return daCategoria && doTexto
  })
})

function alternar(id) {
  abertas.value = abertas.value.includes(id)
    ? abertas.value.filter((x) => x !== id)
    : [...abertas.value, id]
}

const filtroBusca = (v) => v.replace(/^\s/, '').slice(0, 80)
</script>

<template>
  <div class="flex min-h-screen flex-col bg-[#f8faff]">
    <AppHeader />

    <main class="mx-auto w-full max-w-7xl flex-1 px-6 pb-24 sm:px-12">
      <!-- Voltar -->
      <RouterLink
        :to="{ name: 'home' }"
        class="inline-flex items-center gap-1.5 py-2 text-sm font-bold text-[#0b2f5b] transition-opacity hover:opacity-70"
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

      <header class="mx-auto mt-6 max-w-3xl text-center">
        <h1 class="text-3xl font-bold leading-tight tracking-tight text-[#00436b] sm:text-[40px]">
          Dúvidas Frequentes
        </h1>
        <p class="mt-4 max-w-3xl text-lg leading-7 text-gray-700">
          Encontre respostas rápidas sobre agendamento, teleconsultas, pagamentos e segurança dos
          seus dados.
        </p>
      </header>

      <!-- Busca + categorias -->
      <section class="mx-auto mt-8 max-w-3xl" aria-label="Filtrar dúvidas">
        <FormField
          label="Buscar nas dúvidas"
          placeholder="Ex.: pagamento, receita, senha..."
          :icon="icons.busca"
          :model-value="busca"
          @update:model-value="busca = filtroBusca($event)"
        />

        <div class="mt-4 flex flex-wrap justify-center gap-3" role="group" aria-label="Categorias">
          <button
            v-for="cat in categorias"
            :key="cat.id"
            type="button"
            :aria-pressed="categoriaAtiva === cat.id"
            class="inline-flex h-9 cursor-pointer items-center rounded-full px-4 text-sm font-semibold transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0a9ba5]"
            :class="
              categoriaAtiva === cat.id
                ? 'bg-[#00436b] text-white'
                : 'bg-[#eef1fe] text-gray-700 hover:text-[#00436b]'
            "
            @click="categoriaAtiva = cat.id"
          >
            {{ cat.label }}
          </button>
        </div>
      </section>

      <!-- Perguntas -->
      <section class="mx-auto mt-8 max-w-3xl" aria-label="Perguntas e respostas">
        <ul v-if="filtradas.length" class="flex flex-col gap-3">
          <li
            v-for="p in filtradas"
            :key="p.id"
            class="rounded-xl bg-white shadow-[0_1px_4px_rgba(11,47,91,0.06)]"
          >
            <h2>
              <button
                :id="`pergunta-${p.id}`"
                type="button"
                class="flex w-full cursor-pointer items-center justify-between gap-4 rounded-xl px-5 py-4 text-left text-base font-medium text-[#0b2f5b] focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0a9ba5]"
                :aria-expanded="abertas.includes(p.id)"
                :aria-controls="`resposta-${p.id}`"
                @click="alternar(p.id)"
              >
                {{ p.pergunta }}
                <svg
                  class="size-5 shrink-0 text-[#00436b] transition-transform"
                  :class="abertas.includes(p.id) ? 'rotate-180' : ''"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke-width="2"
                  stroke="currentColor"
                  aria-hidden="true"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" :d="icons.seta" />
                </svg>
              </button>
            </h2>

            <div
              v-show="abertas.includes(p.id)"
              :id="`resposta-${p.id}`"
              role="region"
              :aria-labelledby="`pergunta-${p.id}`"
              class="px-5 pb-5"
            >
              <p class="text-[15px] leading-7 text-gray-700">{{ p.resposta }}</p>
              <RouterLink
                v-if="p.link"
                :to="p.link.to"
                class="mt-3 inline-block text-sm font-bold text-[#0b6b62] underline underline-offset-2 hover:opacity-80"
              >
                {{ p.link.label }}
              </RouterLink>
            </div>
          </li>
        </ul>

        <p v-else class="rounded-xl bg-white p-6 text-center text-[15px] text-gray-600" role="status">
          Nenhuma dúvida encontrada para essa busca.
        </p>
      </section>

      <!-- Chamada para a Ouvidoria -->
      <section
        class="mx-auto mt-12 flex max-w-3xl flex-col items-start gap-4 rounded-2xl bg-[#eff2fd] p-6 sm:flex-row sm:items-center sm:justify-between"
      >
        <div>
          <h2 class="text-lg font-medium text-[#0b2f5b]">Não encontrou o que procurava?</h2>
          <p class="mt-1 text-sm leading-6 text-gray-600">
            Envie a sua dúvida para a nossa Ouvidoria.
          </p>
        </div>
        <RouterLink
          :to="{ name: 'ouvidoria' }"
          class="inline-flex h-11 shrink-0 items-center rounded-lg bg-[#00436b] px-6 text-sm font-bold text-white transition-opacity hover:opacity-90"
        >
          Falar com a Ouvidoria
        </RouterLink>
      </section>
    </main>
  </div>
</template>