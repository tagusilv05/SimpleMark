<script setup>
/**
 * DocumentoInstitucional — página de texto longo com índice lateral (Termos, Privacidade...)
 *
 * Já inclui o AppHeader, o link "Voltar" (para a home), o título e o resumo.
 *
 * COMO USAR (na página):
 *
 *   import DocumentoInstitucional from '@/components/shared/DocumentoInstitucional.vue'
 *
 *   const secoes = [
 *     { titulo: 'Aceitação', paragrafos: ['Texto...'], itens: ['Item A', 'Item B'], fechamento: ['Texto depois da lista'] },
 *   ]
 *
 *   <DocumentoInstitucional
 *     titulo="Termos e Condições"
 *     resumo="Leia com atenção antes de usar a plataforma."
 *     atualizado-em="28 de outubro de 2026"
 *     :secoes="secoes"
 *   />
 *
 * PROPS
 *   titulo        String (obrigatória)  título principal (h1).
 *   resumo        String (padrão: '')   frase de apresentação abaixo do título.
 *   atualizadoEm  String (padrão: '')   data da última atualização ("Atualizado em ...").
 *   secoes        Array  (obrigatória)  lista de seções, cada uma com:
 *                   titulo      String    título da seção (a numeração "1.", "2."... é automática)
 *                   paragrafos  String[]  parágrafos exibidos primeiro (opcional)
 *                   itens       String[]  lista com marcadores, depois dos parágrafos (opcional)
 *                   fechamento  String[]  parágrafos exibidos depois da lista (opcional)
 *
 * O índice ("Neste documento") fica ao lado no desktop (fixo ao rolar) e vira um bloco
 * no topo no celular. Clicar num item rola suavemente até a seção.
 */

import AppHeader from '@/components/shared/AppHeader.vue'

defineProps({
  titulo: { type: String, required: true },
  resumo: { type: String, default: '' },
  atualizadoEm: { type: String, default: '' },
  secoes: { type: Array, required: true },
})

const voltarIcon = 'M10.5 19.5 3 12m0 0 7.5-7.5M3 12h18'

function irParaSecao(indice) {
  document
    .getElementById(`secao-${indice + 1}`)
    ?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}
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
          <path stroke-linecap="round" stroke-linejoin="round" :d="voltarIcon" />
        </svg>
        Voltar
      </RouterLink>

      <!-- Título -->
      <header class="mt-6">
        <h1 class="text-3xl font-bold leading-tight tracking-tight text-[#00436b] sm:text-[40px]">
          {{ titulo }}
        </h1>
        <p v-if="resumo" class="mt-4 max-w-3xl text-lg leading-7 text-gray-700">{{ resumo }}</p>
        <p v-if="atualizadoEm" class="mt-3 text-sm text-gray-500">Atualizado em {{ atualizadoEm }}</p>
      </header>

      <div class="mt-10 grid grid-cols-1 items-start gap-8 lg:grid-cols-[260px_minmax(0,1fr)]">
        <!-- Índice -->
        <nav
          class="rounded-xl bg-white p-5 shadow-[0_1px_4px_rgba(11,47,91,0.06)] lg:sticky lg:top-6"
          aria-label="Neste documento"
        >
          <p class="text-sm font-bold text-gray-900">Neste documento</p>
          <ol class="mt-3 flex flex-col gap-1">
            <li v-for="(secao, i) in secoes" :key="secao.titulo">
              <a
                :href="`#secao-${i + 1}`"
                class="block rounded-md px-2 py-1.5 text-sm leading-5 text-[#0b2f5b] transition-colors hover:bg-[#eef1fe]"
                @click.prevent="irParaSecao(i)"
              >
                {{ i + 1 }}. {{ secao.titulo }}
              </a>
            </li>
          </ol>
        </nav>

        <!-- Texto -->
        <article
          class="rounded-2xl bg-white p-6 shadow-[0_2px_12px_rgba(11,47,91,0.06)] sm:p-10"
        >
          <section
            v-for="(secao, i) in secoes"
            :id="`secao-${i + 1}`"
            :key="secao.titulo"
            class="scroll-mt-6 border-b border-gray-100 py-8 first:pt-0 last:border-b-0 last:pb-0"
          >
            <h2 class="text-xl font-medium text-[#0b2f5b]">{{ i + 1 }}. {{ secao.titulo }}</h2>

            <p
              v-for="(texto, j) in secao.paragrafos"
              :key="`p-${j}`"
              class="mt-3 text-[15px] leading-7 text-gray-700"
            >
              {{ texto }}
            </p>

            <ul
              v-if="secao.itens?.length"
              class="mt-3 flex list-disc flex-col gap-2 pl-6 text-[15px] leading-7 text-gray-700 marker:text-[#00436b]"
            >
              <li v-for="item in secao.itens" :key="item">{{ item }}</li>
            </ul>

            <p
              v-for="(texto, j) in secao.fechamento"
              :key="`f-${j}`"
              class="mt-3 text-[15px] leading-7 text-gray-700"
            >
              {{ texto }}
            </p>
          </section>
        </article>
      </div>
    </main>
  </div>
</template>