<script setup>
/**
 * AppHeader — cabeçalho do site (logo + links + área do usuário)
 *
 * COMO USAR (na página):
 *
 *   import AppHeader from '@/components/shared/AppHeader.vue'
 *
 *   const user = ref({ name: 'Nome Paciente', role: 'Paciente' })
 *   function logout() { user.value = null }
 *
 *   <AppHeader :user="user" @logout="logout" />   // logado
 *   <AppHeader />                                 // visitante
 *
 * PROPS
 *   user  Object | null  (padrão: null)
 *     null            -> visitante: mostra "Entrar" e "Cadastrar-se"
 *     { name, role }  -> logado: mostra avatar + nome + cargo e o menu ao passar o mouse
 *       name  String  nome exibido; as iniciais viram o avatar ("Nome Paciente" -> "NP")
 *       role  String  texto pequeno abaixo do nome (ex.: 'Paciente', 'Profissional')
 *
 * EVENTOS
 *   @logout  disparado ao clicar em "Sair" no menu do usuário.
 *            O componente NÃO desloga sozinho: o pai decide o que fazer
 *            (limpar o user, chamar a API, redirecionar...).
 *
 * O QUE JÁ VEM DEFINIDO AQUI DENTRO (edite os arrays abaixo para mudar)
 *   links  navegação central: Como Funciona (/como-funciona), Sobre Nós (/sobre-nos),
 *          Ouvidoria (/ouvidoria). O link da página atual fica sublinhado.
 *   items  menu do usuário: Minha Conta (/minha-conta), Agendamentos (/agendamentos),
 *          separador e Sair (vermelho, dispara @logout).
 *          Cada item aceita { label, to, icon, action, danger } ou { separator: true }
 *            to      rota do vue-router (navega com router.push)
 *            icon    caminho "d" de um SVG 24x24 de contorno
 *            action  'logout' dispara o evento @logout
 *            danger  true deixa o item vermelho
 *   Visitante: "Entrar" -> /login e "Cadastrar-se" -> /cadastro. O logo leva para "/".
 *
 * COMPORTAMENTO DO MENU
 *   Abre ao passar o mouse ou ao focar com o teclado (Tab) e fecha 150 ms depois de
 *   sair, para dar tempo de o mouse chegar no dropdown. Clicar em um item fecha o menu.
 *
 * DEPENDÊNCIAS
 *   - vue-router com as rotas acima registradas
 *   - @/components/shared/UserAvatar.vue (avatar com iniciais)
 *   - @/assets/logo-simple-mark.png (o arquivo precisa existir com esse nome)
 *   - Tailwind CSS
 */

import { ref } from 'vue'
import { useRouter } from 'vue-router'
import UserAvatar from '@/components/shared/UserAvatar.vue'
import logo from '@/assets/logo-simple-mark.png'

// user = null -> visitante | { name, role } -> logado
defineProps({
  user: { type: Object, default: null },
})

const emit = defineEmits(['logout'])

const router = useRouter()

// ---- Links de navegação ----
const links = [
  { label: 'Como Funciona', to: '/como-funciona' },
  { label: 'Sobre Nós', to: '/sobre-nos' },
  { label: 'Ouvidoria', to: '/ouvidoria' },
]

// ---- Menu do usuário (abre ao passar o mouse) ----
const open = ref(false)
let closeTimer = null

// Pequeno atraso ao sair com o mouse, para dar tempo de chegar no dropdown
function show() {
  clearTimeout(closeTimer)
  open.value = true
}

function hide() {
  closeTimer = setTimeout(() => (open.value = false), 150)
}

const items = [
  {
    label: 'Minha Conta',
    to: '/minha-conta',
    icon: 'M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.5 20.118a7.5 7.5 0 0 1 15 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.5-1.632Z',
  },
  {
    label: 'Agendamentos',
    to: '/agendamentos',
    icon: 'M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 0 1 2.25-2.25h13.5A2.25 2.25 0 0 1 21 7.5v11.25m-18 0A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75m-18 0v-7.5A2.25 2.25 0 0 1 5.25 9h13.5A2.25 2.25 0 0 1 21 11.25v7.5',
  },
  { separator: true },
  {
    label: 'Sair',
    action: 'logout',
    danger: true,
    icon: 'M15.75 9V5.25A2.25 2.25 0 0 0 13.5 3h-6a2.25 2.25 0 0 0-2.25 2.25v13.5A2.25 2.25 0 0 0 7.5 21h6a2.25 2.25 0 0 0 2.25-2.25V15m3 0 3-3m0 0-3-3m3 3H9',
  },
]

function onSelect(item) {
  open.value = false
  if (item.action === 'logout') emit('logout')
  else if (item.to) router.push(item.to)
}
</script>

<template>
  <header class="w-full bg-[#f8faff]">
    <div class="mx-auto flex h-32 max-w-500 items-center justify-between gap-8 px-12">
      <!-- Logo -->
      <RouterLink
        to="/"
        class="inline-flex items-center"
        aria-label="Simple Mark - Página inicial"
      >
        <img :src="logo" alt="Simple Mark" class="block h-18 w-auto pl-10" />
      </RouterLink>

      <!-- Links -->
        <nav class="flex items-center gap-10 lg:gap-24 xl:gap-60" aria-label="Navegação principal">
        <RouterLink
          v-for="link in links"
          :key="link.label"
          :to="link.to"
          class="rounded-lg px-4 py-2 text-[15px] font-semibold text-[#0b2f5b] transition-colors hover:opacity-70"
          active-class="bg-[#e1e8fb]"
        >
          {{ link.label }}
        </RouterLink>
      </nav>

      <!-- Logado: avatar + dropdown -->
      <div
        v-if="user"
        class="relative"
        @mouseenter="show"
        @mouseleave="hide"
        @focusin="show"
        @focusout="hide"
      >
        <button
          type="button"
          class="flex cursor-pointer items-center gap-3 text-left"
          aria-haspopup="menu"
          :aria-expanded="open"
        >
          <UserAvatar :name="user.name" class="size-12 text-sm font-bold" />

          <span class="flex flex-col leading-tight">
            <span class="text-[15px] font-bold text-[#0b2f5b]">{{ user.name }}</span>
            <span class="text-xs text-gray-500">{{ user.role }}</span>
          </span>

          <svg
            class="size-3 text-[#0b2f5b] transition-transform duration-200"
            :class="{ 'rotate-180': open }"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="3"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path stroke-linecap="round" stroke-linejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" />
          </svg>
        </button>

        <Transition
          enter-active-class="transition duration-150"
          leave-active-class="transition duration-150"
          enter-from-class="-translate-y-1 opacity-0"
          leave-to-class="-translate-y-1 opacity-0"
        >
          <ul
            v-if="open"
            class="absolute right-0 top-full z-50 mt-1 min-w-52 rounded-xl bg-white py-2 shadow-[0_8px_24px_rgba(11,47,91,0.12)]"
            role="menu"
          >
            <template v-for="(item, index) in items" :key="index">
              <li v-if="item.separator" class="my-1.5 h-px bg-gray-200" role="separator" />

              <li v-else role="none">
                <button
                  type="button"
                  role="menuitem"
                  class="flex w-full cursor-pointer items-center gap-3 px-5 py-3 text-left text-[15px] transition-colors"
                  :class="
                    item.danger
                      ? 'text-red-700 hover:bg-red-50'
                      : 'text-gray-800 hover:bg-[#f3f6fb]'
                  "
                  @click="onSelect(item)"
                >
                  <svg
                    class="size-5"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke-width="1.5"
                    stroke="currentColor"
                    aria-hidden="true"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" :d="item.icon" />
                  </svg>
                  <span>{{ item.label }}</span>
                </button>
              </li>
            </template>
          </ul>
        </Transition>
      </div>

      <!-- Visitante: Entrar / Cadastrar-se -->
      <div v-else class="flex items-center gap-8">
        <RouterLink
          to="/login"
          class="text-sm font-semibold text-[#0b2f5b] transition-opacity hover:opacity-70"
        >
          Entrar
        </RouterLink>

        <RouterLink
          to="/cadastro"
          class="rounded-lg bg-[#042d5c] px-6 py-2 text-sm font-semibold text-white transition-colors hover:bg-[#0b3f7a]"
        >
          Cadastrar-se
        </RouterLink>
      </div>
    </div>
  </header>
</template>