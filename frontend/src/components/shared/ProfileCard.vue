<script setup>
import { computed } from 'vue'
import UserAvatar from './UserAvatar.vue'
import RoleBadge from './RoleBadge.vue'

const props = defineProps({
  name: { type: String, required: true },
  role: { type: String, default: 'Paciente' },
  email: { type: String, default: '' },
  phone: { type: String, default: '' },
  memberSince: { type: String, default: '' },
  verified: { type: Boolean, default: false },
})

const icons = {
  email:
    'M21.75 6.75v10.5a2.25 2.25 0 0 1-2.25 2.25h-15a2.25 2.25 0 0 1-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0 0 19.5 4.5h-15a2.25 2.25 0 0 0-2.25 2.25m19.5 0v.243a2.25 2.25 0 0 1-1.07 1.916l-7.5 4.615a2.25 2.25 0 0 1-2.36 0L3.32 8.91a2.25 2.25 0 0 1-1.07-1.916V6.75',
  phone:
    'M10.5 1.5H8.25A2.25 2.25 0 0 0 6 3.75v16.5a2.25 2.25 0 0 0 2.25 2.25h7.5A2.25 2.25 0 0 0 18 20.25V3.75a2.25 2.25 0 0 0-2.25-2.25H13.5m-3 0V3h3V1.5m-3 0h3m-3 18.75h3',
}

const infos = computed(() =>
  [
    { key: 'email', icon: icons.email, text: props.email },
    { key: 'phone', icon: icons.phone, text: props.phone },
  ].filter((item) => item.text)
)
</script>

<template>
  <section class="mx-auto flex w-full items-center gap-6 rounded-xl bg-white p-8 shadow-[0_2px_12px_rgba(11,47,91,0.08)]">
    <!-- Avatar (tamanho definido aqui) + bolinha de verificado -->
    <div class="relative shrink-0">
      <UserAvatar :name="name" class="size-20 text-3xl font-medium" />

      <span
        v-if="verified"
        class="absolute -bottom-0.5 -right-0.5 flex size-6 items-center justify-center rounded-full border-2 border-white bg-[#0a9ba5] text-white"
        aria-label="Verificado"
      >
        <svg
          class="size-3.5"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke-width="3"
          stroke="currentColor"
          aria-hidden="true"
        >
          <path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" />
        </svg>
      </span>
    </div>

    <div class="flex min-w-0 flex-col gap-2">
      <div class="flex flex-wrap items-center gap-3">
        <h1 class="text-2xl font-medium text-[#0b2f5b]">{{ name }}</h1>
        <RoleBadge :label="role" />
      </div>

      <div class="flex flex-wrap items-center gap-x-4 gap-y-1">
        <template v-for="(item, index) in infos" :key="item.key">
          <span v-if="index > 0" class="size-1 rounded-full bg-gray-300" aria-hidden="true" />

          <!-- Antigo InfoItem -->
          <span class="inline-flex items-center gap-1.5 text-sm font-semibold text-gray-600">
            <svg
              class="size-4 shrink-0"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke-width="1.5"
              stroke="currentColor"
              aria-hidden="true"
            >
              <path stroke-linecap="round" stroke-linejoin="round" :d="item.icon" />
            </svg>
            {{ item.text }}
          </span>
        </template>
      </div>
    </div>
  </section>
</template>