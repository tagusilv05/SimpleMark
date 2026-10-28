<script setup>
/**
 * QuemSomosView — página "Quem Somos"
 *
 * Fluxo: home -> rodapé "Quem Somos" -> esta tela (rota `quem-somos`) -> Voltar -> home.
 *
 * Foco: a identidade da Simple Mark (missão, visão e valores). O detalhe de como a
 * plataforma funciona fica em "Sobre Nós" e "Como Funciona", com atalhos no fim da página.
 *
 * ⚠️ Os textos são uma PROPOSTA com base no que a plataforma já comunica. Ajuste-os para a
 * realidade do projeto (não há nomes de equipe, datas ou números inventados).
 *
 * Estrutura:
 *   - Cabeçalho (AppHeader) e link "Voltar"
 *   - Apresentação
 *   - Missão e Visão
 *   - Valores (cartões)
 *   - Atalhos para outras páginas
 */

import AppHeader from '@/components/shared/AppHeader.vue'

// Caminhos "d" dos ícones (Heroicons 24x24, contorno)
const icons = {
  voltar: 'M10.5 19.5 3 12m0 0 7.5-7.5M3 12h18',
  coracao:
    'M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12Z',
  escudo:
    'M9 12.75 11.25 15 15 9.75m-3-7.036A11.959 11.959 0 0 1 3.598 6 11.99 11.99 0 0 0 3 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285Z',
  olho: 'M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z',
  globo:
    'M12 21a9.004 9.004 0 0 0 8.716-6.747M12 21a9.004 9.004 0 0 1-8.716-6.747M12 21c2.485 0 4.5-4.03 4.5-9S14.485 3 12 3m0 18c-2.485 0-4.5-4.03-4.5-9S9.515 3 12 3m0 0a8.997 8.997 0 0 1 7.843 4.582M12 3a8.997 8.997 0 0 0-7.843 4.582m15.686 0A11.953 11.953 0 0 1 12 10.5c-2.998 0-5.74-1.1-7.843-2.918m15.686 0A8.959 8.959 0 0 1 21 12c0 .778-.099 1.533-.284 2.253m0 0A17.919 17.919 0 0 1 12 16.5c-3.162 0-6.133-.815-8.716-2.247m0 0A9.015 9.015 0 0 1 3 12c0-1.605.42-3.113 1.157-4.418',
  id: 'M15 9h3.75M15 12h3.75M15 15h3.75M4.5 19.5h15a2.25 2.25 0 0 0 2.25-2.25V6.75A2.25 2.25 0 0 0 19.5 4.5h-15a2.25 2.25 0 0 0-2.25 2.25v10.5A2.25 2.25 0 0 0 4.5 19.5Zm6-10.125a1.875 1.875 0 1 1-3.75 0 1.875 1.875 0 0 1 3.75 0Zm1.294 6.336a6.721 6.721 0 0 1-3.17.789 6.721 6.721 0 0 1-3.168-.789 3.376 3.376 0 0 1 6.338 0Z',
  relogio: 'M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z',
}

const valores = [
  {
    titulo: 'Cuidado Humano',
    texto: 'Tecnologia a serviço da empatia: atendimento calmo, acolhedor e contínuo.',
    icon: icons.coracao,
  },
  {
    titulo: 'Segurança e Privacidade',
    texto:
      'Chamadas privativas e criptografadas e tratamento de dados em conformidade com a LGPD.',
    icon: icons.escudo,
  },
  {
    titulo: 'Transparência',
    texto: 'Horários, valores e regras claros antes de qualquer confirmação.',
    icon: icons.olho,
  },
  {
    titulo: 'Acesso para Todos',
    texto: 'Levar referências médicas a quem mora longe dos grandes centros.',
    icon: icons.globo,
  },
  {
    titulo: 'Profissionais Verificados',
    texto: 'Cada perfil profissional passa por validação da nossa equipe antes de ser liberado.',
    icon: icons.id,
  },
  {
    titulo: 'Agilidade',
    texto: 'Menos filas e prazos: consultas rápidas e orientações em questão de horas.',
    icon: icons.relogio,
  },
]

const atalhos = [
  { label: 'Sobre Nós', to: { name: 'sobre-nos' } },
  { label: 'Como Funciona', to: { name: 'como-funciona' } },
  { label: 'Ouvidoria', to: { name: 'ouvidoria' } },
]
</script>

<template>
  <div class="flex min-h-screen flex-col bg-[#f8faff]">
    <AppHeader />

    <main class="flex-1">
      <!-- Apresentação -->
      <section class="mx-auto w-full max-w-7xl px-6 pb-16 sm:px-12">
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

        <h1
          class="mt-8 max-w-4xl text-3xl font-bold leading-tight tracking-tight text-[#00436b] sm:text-[40px]"
        >
          Quem Somos
        </h1>
        <p class="mt-5 max-w-3xl text-lg leading-7 text-gray-700">
          A Simple Mark nasceu para tornar o cuidado com a saúde mais simples, próximo e acessível.
          Conectamos pessoas a profissionais de saúde qualificados, com segurança e acolhimento, onde
          quer que elas estejam.
        </p>
      </section>

      <!-- Missão e Visão -->
      <section class="bg-white py-16" aria-label="Missão e visão">
        <div class="mx-auto grid w-full max-w-7xl grid-cols-1 gap-6 px-6 sm:px-12 md:grid-cols-2">
          <article class="rounded-2xl bg-[#eff2fd] p-8">
            <h2 class="text-2xl font-bold tracking-tight text-[#00436b]">Nossa Missão</h2>
            <p class="mt-4 text-base leading-7 text-gray-700">
              Democratizar o acesso à saúde especializada no Brasil, reduzindo custos de
              deslocamento, acabando com as filas de espera e aproximando boas equipes médicas de
              qualquer cidadão.
            </p>
          </article>

          <article class="rounded-2xl bg-[#eff2fd] p-8">
            <h2 class="text-2xl font-bold tracking-tight text-[#00436b]">Nossa Visão</h2>
            <p class="mt-4 text-base leading-7 text-gray-700">
              Ser a plataforma de referência em teleconsultas, reconhecida pela confiança, pela
              qualidade do atendimento e pelo cuidado humano em cada interação, em escala nacional.
            </p>
          </article>
        </div>
      </section>

      <!-- Valores -->
      <section class="py-16" aria-labelledby="titulo-valores">
        <div class="mx-auto w-full max-w-7xl px-6 sm:px-12">
          <h2
            id="titulo-valores"
            class="text-3xl font-bold tracking-tight text-[#00436b] sm:text-[36px]"
          >
            Nossos Valores
          </h2>
          <p class="mt-4 max-w-3xl text-base leading-7 text-gray-700">
            Os princípios que guiam as nossas decisões, do desenvolvimento da plataforma ao
            relacionamento com pacientes e profissionais.
          </p>

          <ul class="mt-8 grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
            <li
              v-for="valor in valores"
              :key="valor.titulo"
              class="rounded-xl bg-white p-6 shadow-[0_1px_4px_rgba(11,47,91,0.06)]"
            >
              <span
                class="grid size-12 place-items-center rounded-xl bg-[#e1e8fb] text-[#00436b]"
              >
                <svg
                  class="size-6"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke-width="1.5"
                  stroke="currentColor"
                  aria-hidden="true"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" :d="valor.icon" />
                </svg>
              </span>
              <h3 class="mt-4 text-xl leading-7 font-medium text-[#0b2f5b]">{{ valor.titulo }}</h3>
              <p class="mt-2 text-sm leading-6 text-gray-600">{{ valor.texto }}</p>
            </li>
          </ul>
        </div>
      </section>

      <!-- Atalhos -->
      <section class="pb-24">
        <div class="mx-auto w-full max-w-7xl px-6 sm:px-12">
          <div
            class="flex flex-col items-start gap-5 rounded-2xl bg-[#eff2fd] p-8 sm:flex-row sm:items-center sm:justify-between"
          >
            <div>
              <h2 class="text-xl font-medium text-[#0b2f5b]">Quer saber mais?</h2>
              <p class="mt-1 text-sm leading-6 text-gray-600">
                Veja como a plataforma funciona ou fale diretamente com a nossa Ouvidoria.
              </p>
            </div>

            <nav class="flex flex-wrap gap-3" aria-label="Páginas relacionadas">
              <RouterLink
                v-for="atalho in atalhos"
                :key="atalho.label"
                :to="atalho.to"
                class="inline-flex h-11 items-center rounded-lg border-2 border-[#042d5c] bg-white px-5 text-sm font-bold text-[#042d5c] transition-colors hover:bg-[#042d5c] hover:text-white"
              >
                {{ atalho.label }}
              </RouterLink>
            </nav>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>