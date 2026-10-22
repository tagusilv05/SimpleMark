<script setup>
/**
 * AppFooter — rodapé do site (logo + links institucionais + direitos reservados)
 *
 * COMO USAR (na página):
 *
 *   import AppFooter from '@/components/shared/AppFooter.vue'
 *
 *   <AppFooter />
 *
 * O QUE JÁ VEM DEFINIDO AQUI DENTRO (edite o array abaixo para mudar)
 *   columns  colunas de links: Quem Somos (/quem-somos), Termos e Condições (/termos),
 *            Política de Privacidade (/privacidade) e Dúvidas Frequentes (/duvidas-frequentes).
 *   O logo leva para "/".
 *
 * DEPENDÊNCIAS
 *   - vue-router
 *   - @/assets/logo-simple-mark.png
 *   - Tailwind CSS
 */

import logo from '@/assets/logo-simple-mark.png'

const columns = [
  [
    { label: 'Quem Somos', to: '/quem-somos' },
    { label: 'Termos e Condições', to: '/termos' },
    { label: 'Política de Privacidade', to: '/privacidade' },
  ],
  [{ label: 'Dúvidas Frequentes', to: '/duvidas-frequentes' }],
]
</script>

<template>
  <footer class="w-full border-t border-gray-200 bg-[#f8faff]">
    <div class="mx-auto flex max-w-300 flex-col gap-8 px-12 pt-8 pb-4">
      <div class="flex flex-col gap-8 sm:flex-row sm:items-start sm:gap-10">
        <RouterLink to="/" class="inline-flex shrink-0" aria-label="Simple Mark - Página inicial">
          <img :src="logo" alt="Simple Mark" class="block h-16 w-auto" />
        </RouterLink>

        <nav class="flex gap-10" aria-label="Links institucionais">
          <ul v-for="(column, index) in columns" :key="index" class="flex flex-col gap-2">
            <li v-for="link in column" :key="link.label">
              <RouterLink
                :to="link.to"
                class="text-xs text-[#0b2f5b] transition-opacity hover:opacity-70"
              >
                {{ link.label }}
              </RouterLink>
            </li>
          </ul>
        </nav>
      </div>

      <p class="text-center text-[11px] text-gray-600">Todos os direitos reservados à Simple Mark</p>
    </div>
  </footer>
</template>
