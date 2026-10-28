<script setup>
/**
 * SobreNosView — página "Sobre Nós"
 *
 * Fluxo: home -> "Sobre Nós" (cabeçalho) -> esta tela (rota `sobre-nos`)
 *        -> Voltar -> home.
 *
 * Estrutura:
 *   - Cabeçalho (AppHeader) e link "Voltar"
 *   - Apresentação da plataforma
 *   - "O Sistema Simple Mark": três cartões com os recursos principais
 *   - "Finalidade da Plataforma": texto + três cartões com os objetivos
 */

import AppHeader from '@/components/shared/AppHeader.vue'

// Caminhos "d" dos ícones (Heroicons 24x24, contorno)
const icons = {
  voltar: 'M10.5 19.5 3 12m0 0 7.5-7.5M3 12h18',
  agenda:
    'M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 0 1 2.25-2.25h13.5A2.25 2.25 0 0 1 21 7.5v11.25m-18 0A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75m-18 0v-7.5A2.25 2.25 0 0 1 5.25 9h13.5A2.25 2.25 0 0 1 21 11.25v7.5m-9-6h.008v.008H12v-.008ZM12 15h.008v.008H12V15Zm0 2.25h.008v.008H12v-.008ZM9.75 15h.008v.008H9.75V15Zm0 2.25h.008v.008H9.75v-.008ZM7.5 15h.008v.008H7.5V15Zm0 2.25h.008v.008H7.5v-.008Zm6.75-4.5h.008v.008h-.008v-.008Zm0 2.25h.008v.008h-.008V15Zm0 2.25h.008v.008h-.008v-.008Zm2.25-4.5h.008v.008H16.5v-.008Zm0 2.25h.008v.008H16.5V15Z',
  video:
    'm15.75 10.5 4.72-4.72a.75.75 0 0 1 1.28.53v11.38a.75.75 0 0 1-1.28.53l-4.72-4.72M4.5 18.75h9a2.25 2.25 0 0 0 2.25-2.25v-9a2.25 2.25 0 0 0-2.25-2.25h-9A2.25 2.25 0 0 0 2.25 7.5v9a2.25 2.25 0 0 0 2.25 2.25Z',
  documento:
    'M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z',
  globo:
    'M12 21a9.004 9.004 0 0 0 8.716-6.747M12 21a9.004 9.004 0 0 1-8.716-6.747M12 21c2.485 0 4.5-4.03 4.5-9S14.485 3 12 3m0 18c-2.485 0-4.5-4.03-4.5-9S9.515 3 12 3m0 0a8.997 8.997 0 0 1 7.843 4.582M12 3a8.997 8.997 0 0 0-7.843 4.582m15.686 0A11.953 11.953 0 0 1 12 10.5c-2.998 0-5.74-1.1-7.843-2.918m15.686 0A8.959 8.959 0 0 1 21 12c0 .778-.099 1.533-.284 2.253m0 0A17.919 17.919 0 0 1 12 16.5c-3.162 0-6.133-.815-8.716-2.247m0 0A9.015 9.015 0 0 1 3 12c0-1.605.42-3.113 1.157-4.418',
  relogio: 'M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z',
  coracao:
    'M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12Z',
}

// "O Sistema Simple Mark"
const recursos = [
  {
    titulo: 'Agendamento Online Inteligente',
    texto:
      'Encontre médicos de diversas especialidades, escolha o melhor dia e horário de acordo com a sua rotina e receba lembretes automáticos para não esquecer a sua consulta.',
    icon: icons.agenda,
  },
  {
    titulo: 'Teleconsulta com Vídeo HD Criptografada',
    texto:
      'Atendimento na palma da mão, de onde você estiver. A chamada é privativa, com áudio e vídeo de alta qualidade para você conversar com tranquilidade.',
    icon: icons.video,
  },
  {
    titulo: 'Prescrição Receitas',
    texto: 'Receba suas receitas, pedidos de exames e atestados direto no seu endereço eletrônico após a consulta.',
    icon: icons.documento,
  },
]

// "Finalidade da Plataforma"
const objetivos = [
  {
    titulo: 'Eliminação de Barreiras Geográficas',
    texto:
      'Permitir que moradores de pequenas cidades e regiões remotas consultem referências médicas sem precisar viajar horas.',
    icon: icons.globo,
  },
  {
    titulo: 'Agilidade e Menos Tempo de Espera',
    texto:
      'Substituir prazos de semanas por consultas rápidas e orientações preventivas em questão de horas.',
    icon: icons.relogio,
  },
  {
    titulo: 'Humanização e Cuidado Contínuo',
    texto:
      'Tecnologia aplicada a serviço da empatia, com diálogo calmo, acolhedor e continuidade assistencial.',
    icon: icons.coracao,
  },
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
          Conheça a Plataforma que Redefine o Acesso à Saúde
        </h1>
        <p class="mt-5 max-w-3xl text-lg leading-7 text-gray-700">
          Um ecossistema digital desenvolvido para aproximar pessoas e profissionais de saúde com
          segurança, transparência tecnológica e acolhimento humano em escala nacional.
        </p>
      </section>

      <!-- O Sistema Simple Mark -->
      <section class="bg-white py-16" aria-labelledby="titulo-sistema">
        <div class="mx-auto w-full max-w-7xl px-6 sm:px-12">
          <h2
            id="titulo-sistema"
            class="text-3xl font-bold tracking-tight text-[#00436b] sm:text-[36px]"
          >
            O Sistema Simple Mark
          </h2>

          <ul class="mt-12 grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
            <li v-for="recurso in recursos" :key="recurso.titulo" class="rounded-2xl bg-[#eff2fd] p-6">
              <div class="flex items-center gap-4">
                <span
                  class="grid size-12 shrink-0 place-items-center rounded-xl bg-[#e1e8fb] text-[#00436b]"
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
                    <path stroke-linecap="round" stroke-linejoin="round" :d="recurso.icon" />
                  </svg>
                </span>
                <h3 class="text-xl leading-7 font-medium text-[#0b2f5b]">{{ recurso.titulo }}</h3>
              </div>
              <p class="mt-4 text-sm leading-6 text-gray-600">{{ recurso.texto }}</p>
            </li>
          </ul>
        </div>
      </section>

      <!-- Finalidade da Plataforma -->
      <section class="py-16" aria-labelledby="titulo-finalidade">
        <div class="mx-auto w-full max-w-7xl px-6 sm:px-12">
          <h2
            id="titulo-finalidade"
            class="text-3xl font-bold tracking-tight text-[#00436b] sm:text-[36px]"
          >
            Finalidade da Plataforma
          </h2>
          <p class="mt-4 max-w-4xl text-base leading-7 text-gray-700">
            A Simple Mark foi concebida com o objetivo central de democratizar o acesso à saúde
            especializada no Brasil, reduzindo custos de deslocamento, acabando com as filas de
            espera e aproximando as melhores equipes médicas de qualquer cidadão.
          </p>

          <ul class="mt-8 grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
            <li
              v-for="objetivo in objetivos"
              :key="objetivo.titulo"
              class="rounded-xl bg-white p-6 shadow-[0_1px_4px_rgba(11,47,91,0.06)]"
            >
              <div class="flex items-start gap-3">
                <svg
                  class="mt-1 size-6 shrink-0 text-[#00436b]"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke-width="1.5"
                  stroke="currentColor"
                  aria-hidden="true"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" :d="objetivo.icon" />
                </svg>

                <div>
                  <h3 class="text-xl leading-7 font-medium text-[#0b2f5b]">{{ objetivo.titulo }}</h3>
                  <p class="mt-3 text-sm leading-6 text-gray-600">{{ objetivo.texto }}</p>
                </div>
              </div>
            </li>
          </ul>
        </div>
      </section>
    </main>
  </div>
</template>