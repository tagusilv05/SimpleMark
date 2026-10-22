<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import UserAvatar from '@/components/shared/UserAvatar.vue'
import logo from '@/assets/logo-simple-mark.png'

const props = defineProps({ user: { type: Object, default: null } })
const emit = defineEmits(['logout'])
const route = useRoute()
const router = useRouter()
const currentUser = computed(
  () => props.user ?? { name: 'Administrador Geral', role: 'Administrador' },
)
const active = (path) => route.path === path
const menuOpen = ref(false)
let closeTimer = null

function showMenu() {
  clearTimeout(closeTimer)
  menuOpen.value = true
}

function hideMenu() {
  closeTimer = setTimeout(() => {
    menuOpen.value = false
  }, 150)
}

function logout() {
  hideMenu()
  emit('logout')
  router.push('/administracao/usuarios')
}
</script>

<template>
  <header class="w-full border-b border-[#dce5ee] bg-white">
    <div class="mx-auto flex h-32 max-w-500 items-center justify-between gap-8 px-12">
      <RouterLink
        to="/administracao/usuarios"
        class="inline-flex items-center"
        aria-label="SimpleMark"
      >
        <img :src="logo" alt="SimpleMark" class="block h-18 w-auto pl-10" />
      </RouterLink>

      <nav class="flex items-center gap-1 rounded-xl bg-[#f1f5f9] p-1" aria-label="Administração">
        <RouterLink
          to="/administracao/validacao-profissionais"
          class="flex items-center gap-1.5 rounded-lg px-4 py-2 text-xs font-semibold"
          :class="
            active('/administracao/validacao-profissionais')
              ? 'bg-white text-[#073b57] shadow-sm'
              : 'text-[#61738a]'
          "
        >
          <svg
            class="size-3.5"
            :class="active('/administracao/validacao-profissionais') ? 'text-[#006b88]' : ''"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="1.8"
            aria-hidden="true"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M12 3 5 6v5c0 4.5 2.9 8.5 7 10 4.1-1.5 7-5.5 7-10V6l-7-3Z"
            />
            <path stroke-linecap="round" stroke-linejoin="round" d="m9 12 2 2 4-4" />
          </svg>
          Validação Profissional
        </RouterLink>
        <RouterLink
          to="/administracao/usuarios"
          class="flex items-center gap-1.5 rounded-lg px-4 py-2 text-xs font-semibold"
          :class="
            active('/administracao/usuarios')
              ? 'bg-white text-[#073b57] shadow-sm'
              : 'text-[#61738a]'
          "
        >
          <svg
            class="size-3.5"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="1.8"
            aria-hidden="true"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M16 20v-1.5a4.5 4.5 0 0 0-4.5-4.5h-3A4.5 4.5 0 0 0 4 18.5V20"
            />
            <circle cx="10" cy="7" r="3" />
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M16 11a3 3 0 1 0 0-6M16 14h1a4 4 0 0 1 4 4v2"
            />
          </svg>
          Gestão de Usuários
        </RouterLink>
      </nav>
      <div
        class="relative"
        @mouseenter="showMenu"
        @mouseleave="hideMenu"
        @focusin="showMenu"
        @focusout="hideMenu"
      >
        <div>
          <button
            type="button"
            class="flex cursor-pointer items-center gap-3 text-left"
            aria-haspopup="menu"
            :aria-expanded="menuOpen"
            @click="menuOpen = !menuOpen"
          >
            <UserAvatar :name="currentUser.name" class="size-12 text-sm font-bold" />
            <span class="flex flex-col leading-tight">
              <span class="text-[15px] font-bold text-[#073b57]">{{ currentUser.name }}</span>
              <span class="text-xs text-gray-500">{{ currentUser.role }}</span>
            </span>
            <svg
              class="size-3 text-[#073b57] transition-transform duration-200"
              :class="{ 'rotate-180': menuOpen }"
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
              v-if="menuOpen"
              class="absolute right-0 top-full z-50 mt-1 min-w-52 rounded-xl bg-white py-2 shadow-[0_8px_24px_rgba(11,47,91,0.12)]"
              role="menu"
            >
              <li role="none">
                <button
                  type="button"
                  role="menuitem"
                  class="flex w-full cursor-pointer items-center gap-3 px-5 py-3 text-left text-[15px] text-gray-800 transition-colors hover:bg-[#f3f6fb]"
                  @click="menuOpen = false"
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
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      d="M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.5 20.118a7.5 7.5 0 0 1 15 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.5-1.632Z"
                    />
                  </svg>
                  <span>Minha Conta</span>
                </button>
              </li>
              <li class="my-1.5 h-px bg-gray-200" role="separator" />
              <li role="none">
                <button
                  type="button"
                  role="menuitem"
                  class="flex w-full cursor-pointer items-center gap-3 px-5 py-3 text-left text-[15px] text-red-700 transition-colors hover:bg-red-50"
                  @click="logout"
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
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      d="M15.75 9V5.25A2.25 2.25 0 0 0 13.5 3h-6a2.25 2.25 0 0 0-2.25 2.25v13.5A2.25 2.25 0 0 0 7.5 21h6a2.25 2.25 0 0 0 2.25-2.25V15m3 0 3-3m0 0-3-3m3 3H9"
                    />
                  </svg>
                  <span>Sair</span>
                </button>
              </li>
            </ul>
          </Transition>
        </div>
      </div>
    </div>
  </header>
</template>
