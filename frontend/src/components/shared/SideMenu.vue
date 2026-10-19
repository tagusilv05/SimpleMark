<!-- Caminho: frontend\src\components\shared\SideMenu.vue -->

<script setup>
import { computed } from 'vue'


const defaultItems = [
  {
    key: 'dados',
    label: 'Dados Pessoais',
    icon: 'M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.5 20.118a7.5 7.5 0 0 1 15 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.5-1.632Z',
  },
  {
    key: 'endereco',
    label: 'Endereço',
    icon: 'M15 10.5a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1 1 15 0Z',
  },
  {
    key: 'seguranca',
    label: 'Segurança',
    icon: 'M9 12.75 11.25 15 15 9.75m-3-7.036A11.959 11.959 0 0 1 3.598 6 11.99 11.99 0 0 0 3 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285Z',
  },
  // Só aparece para profissionais
  {
    key: 'perfil',
    label: 'Perfil Profissional',
    roles: ['profissional'],
    icon: 'M11 2v2 M5 2v2 M5 3H4a2 2 0 0 0-2 2v4a6 6 0 0 0 12 0V5a2 2 0 0 0-2-2h-1 M8 15a6 6 0 0 0 12 0v-3 M18 10a2 2 0 1 0 4 0 2 2 0 1 0-4 0',
  },
  {
    key: 'excluir',
    label: 'Excluir Conta',
    danger: true,
    icon: 'm14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0',
  },
]

// items: lista própria (opcional) | role: 'paciente' | 'profissional'
const props = defineProps({
  items: { type: Array, default: null },
  role: { type: String, default: '' },
})

// Item ativo. Funciona COM v-model (a página acompanha a mudança)
// e SEM v-model (o menu guarda a seleção sozinho).
const active = defineModel({ type: String, default: 'dados' })

const emit = defineEmits(['select'])

const visibleItems = computed(() =>
  (props.items ?? defaultItems).filter(
    (item) => !item.roles || item.roles.includes(props.role)
  )
)

function choose(item) {
  active.value = item.key
  emit('select', item)
}
</script>

<template>
  <nav
    class="flex flex-col gap-1 rounded-xl bg-white p-2 shadow-[0_2px_12px_rgba(11,47,91,0.08)]"
    aria-label="Menu lateral"
  >
    <button
      v-for="item in visibleItems"
      :key="item.key"
      type="button"
      class="flex w-full cursor-pointer items-center gap-3 rounded-lg px-4 py-3 text-left text-sm font-semibold transition-colors"
      :class="
        item.key === active
          ? item.danger
            ? 'bg-red-700 text-white'
            : 'bg-[#042d5c] text-white'
          : item.danger
            ? 'text-red-700 hover:bg-red-50'
            : 'text-gray-600 hover:bg-[#f3f6fb]'
      "
      :aria-current="item.key === active ? 'page' : undefined"
      @click="choose(item)"
    >
      <svg
        v-if="item.icon"
        class="size-5 shrink-0"
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
  </nav>
</template>