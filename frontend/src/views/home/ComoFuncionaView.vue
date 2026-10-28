<script setup>
/**
 * ComoFuncionaView — página "Como Funciona"
 *
 * Fluxo: home -> "Como Funciona" (cabeçalho) -> esta tela (rota `como-funciona`)
 *        -> Voltar -> home.
 *
 * Estrutura:
 *   - Cabeçalho (AppHeader) e link "Voltar"
 *   - Faixa de apresentação com as abas "Para Pacientes" e "Para Profissionais / Médicos"
 *   - "4 Passos para sua Consulta": um cartão por passo, conforme a aba escolhida
 */

import { computed, ref } from 'vue'
import AppHeader from '@/components/shared/AppHeader.vue'

// Caminhos "d" dos ícones (Heroicons 24x24, contorno)
const icons = {
  voltar: 'M10.5 19.5 3 12m0 0 7.5-7.5M3 12h18',
  paciente:
    'M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z',
  // Estetoscópio (desenho próprio: o Heroicons não tem esse ícone), mesmo estilo de contorno 24x24
  estetoscopio:
    'M5.5 4v5a4 4 0 0 0 8 0V4M4.5 4h2M12.5 4h2M9.5 13v3a4 4 0 0 0 8 0v-1M19.5 13a2 2 0 1 1-4 0 2 2 0 0 1 4 0Z',
  busca: 'm21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z',
  agenda:
    'M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 0 1 2.25-2.25h13.5A2.25 2.25 0 0 1 21 7.5v11.25m-18 0A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75m-18 0v-7.5A2.25 2.25 0 0 1 5.25 9h13.5A2.25 2.25 0 0 1 21 11.25v7.5m-9-6h.008v.008H12v-.008ZM12 15h.008v.008H12V15Zm0 2.25h.008v.008H12v-.008ZM9.75 15h.008v.008H9.75V15Zm0 2.25h.008v.008H9.75v-.008ZM7.5 15h.008v.008H7.5V15Zm0 2.25h.008v.008H7.5v-.008Zm6.75-4.5h.008v.008h-.008v-.008Zm0 2.25h.008v.008h-.008V15Zm0 2.25h.008v.008h-.008v-.008Zm2.25-4.5h.008v.008H16.5v-.008Zm0 2.25h.008v.008H16.5V15Z',
  escudo:
    'M9 12.75 11.25 15 15 9.75m-3-7.036A11.959 11.959 0 0 1 3.598 6 11.99 11.99 0 0 0 3 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285Z',
  video:
    'm15.75 10.5 4.72-4.72a.75.75 0 0 1 1.28.53v11.38a.75.75 0 0 1-1.28.53l-4.72-4.72M4.5 18.75h9a2.25 2.25 0 0 0 2.25-2.25v-9a2.25 2.25 0 0 0-2.25-2.25h-9A2.25 2.25 0 0 0 2.25 7.5v9a2.25 2.25 0 0 0 2.25 2.25Z',
  novoUsuario:
    'M18 7.5v3m0 0v3m0-3h3m-3 0h-3m-2.25-4.125a3.375 3.375 0 1 1-6.75 0 3.375 3.375 0 0 1 6.75 0ZM3 19.235v-.11a6.375 6.375 0 0 1 12.75 0v.109A12.318 12.318 0 0 1 9.374 21c-2.331 0-4.512-.645-6.374-1.766Z',
  sino: 'M14.857 17.082a23.848 23.848 0 0 0 5.454-1.31A8.967 8.967 0 0 1 18 9.75V9A6 6 0 0 0 6 9v.75a8.967 8.967 0 0 1-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 0 1-5.714 0m5.714 0a3 3 0 1 1-5.714 0',
}

// Conteúdo de cada aba. O texto da aba "Para Profissionais / Médicos" é uma proposta
// (o protótipo mostra apenas a aba de pacientes): ajuste conforme o fluxo real.
const abas = [
  { id: 'pacientes', label: 'Para Pacientes', icon: icons.paciente },
  { id: 'profissionais', label: 'Para Profissionais de Saúde', icon: icons.estetoscopio },
]

const conteudo = {
  pacientes: {
    resumo:
      'Em apenas 4 passos rápidos, você encontra especialistas qualificados, agenda no horário ideal e realiza sua teleconsulta sem sair de casa.',
    tituloPassos: 'Passo a Passo Para Sua Consulta',
    passos: [
      {
        titulo: 'Encontre o Especialista',
        texto: 'Busque por especialidade médica.',
        icon: icons.busca,
      },
      {
        titulo: 'Escolha Data & Horário',
        texto:
          'Visualize a agenda em tempo real do profissional. Selecione o melhor dia e horário para a sua rotina com apenas um clique.',
        icon: icons.agenda,
      },
      {
        titulo: 'Confirmação & Pagamento',
        texto:
          'Pague via Pix com confirmação imediata ou cartão de crédito em ambiente criptografado.',
        icon: icons.escudo,
      },
      {
        titulo: 'Teleconsulta no Navegador',
        texto:
          'Acesse o link seguro da sala virtual sem baixar nada. Receba receita e atestados digitais válidos em farmácias de todo o Brasil.',
        icon: icons.video,
      },
    ],
  },
  profissionais: {
    resumo:
      'Em apenas 4 passos, você cadastra seu perfil, organiza sua agenda e atende seus pacientes por teleconsulta, sem sair do consultório ou do conforto de sua casa.',
    tituloPassos: 'Passo a Passo Para Atender Seus Pacientes',
    passos: [
      {
        titulo: 'Cadastre-se & Valide seu Perfil',
        texto: 'Crie sua conta e envie seus dados profissionais para validação da nossa equipe.',
        icon: icons.novoUsuario,
      },
      {
        titulo: 'Configure sua Agenda',
        texto:
          'Defina seus dias e horários de atendimento. Os pacientes enxergam apenas os horários disponíveis.',
        icon: icons.agenda,
      },
      {
        titulo: 'Receba Agendamentos',
        texto: 'Acompanhe as consultas marcadas e as confirmações de pagamento no seu painel.',
        icon: icons.sino,
      },
      {
        titulo: 'Atenda por Vídeo',
        texto:
          'Realize a teleconsulta pelo navegador e emita receitas e atestados digitais ao final do atendimento.',
        icon: icons.video,
      },
    ],
  },
}

const abaAtiva = ref('pacientes')
const atual = computed(() => conteudo[abaAtiva.value])
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

      <!-- Apresentação + abas -->
      <section class="mt-5 rounded-2xl bg-[#eff2fd] px-6 py-8 sm:px-12">
        
        <h2 class="mt-3 text-3xl font-bold leading-tight text-[#00436b] sm:text-[40px]">
          Cuidar De Sua Saúde Nunca Foi Tão Simples
        </h2>
        <p class="mt-5 max-w-4xl text-lg leading-7 text-gray-700">{{ atual.resumo }}</p>

        <div
          class="mt-6 inline-flex max-w-full flex-wrap gap-1 rounded-xl border border-[#dbe3f7] bg-[#e6ecfb] p-1"
          role="tablist"
          aria-label="Como funciona para"
        >
          <button
            v-for="aba in abas"
            :id="`aba-${aba.id}`"
            :key="aba.id"
            type="button"
            role="tab"
            :aria-selected="abaAtiva === aba.id"
            :aria-controls="`painel-${aba.id}`"
            class="inline-flex h-10 cursor-pointer items-center gap-2 rounded-lg px-5 text-sm font-semibold transition-colors"
            :class="
              abaAtiva === aba.id
                ? 'bg-[#00436b] text-white'
                : 'text-gray-600 hover:text-[#00436b]'
            "
            @click="abaAtiva = aba.id"
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
              <path stroke-linecap="round" stroke-linejoin="round" :d="aba.icon" />
            </svg>
            {{ aba.label }}
          </button>
        </div>
      </section>

      <!-- Passos -->
      <section
        :id="`painel-${abaAtiva}`"
        class="mt-20"
        role="tabpanel"
        :aria-labelledby="`aba-${abaAtiva}`"
      >
        <h2 class="text-2xl font-medium text-[#0b2f5b]">{{ atual.tituloPassos }}</h2>

        <ol class="mt-5 grid grid-cols-1 items-start gap-6 sm:grid-cols-2 lg:grid-cols-4">
          <li
            v-for="(passo, i) in atual.passos"
            :key="passo.titulo"
            class="rounded-xl bg-white p-6 shadow-[0_1px_4px_rgba(11,47,91,0.06)]"
          >
            <div class="flex items-center justify-between">
              <span
                class="grid size-10 place-items-center rounded-lg bg-[#00436b] text-xs font-bold text-white"
              >
                {{ String(i + 1).padStart(2, '0') }}
              </span>

              <span class="grid size-10 place-items-center rounded-lg bg-[#e1e8fb] text-[#00436b]">
                <svg
                  class="size-5"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke-width="1.75"
                  stroke="currentColor"
                  aria-hidden="true"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" :d="passo.icon" />
                </svg>
              </span>
            </div>

            <h3 class="mt-4 text-lg leading-7 font-medium text-[#0b2f5b]">{{ passo.titulo }}</h3>
            <p class="mt-3 text-sm leading-6 text-gray-600">{{ passo.texto }}</p>
          </li>
        </ol>
      </section>
    </main>
  </div>
</template>