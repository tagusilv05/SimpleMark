<script setup>
import { computed } from 'vue'

// O tamanho NÃO é definido aqui: quem usa o componente passa as classes.
// Ex.: <UserAvatar :name="nome" class="size-12 text-sm font-bold" />
const props = defineProps({
  name: { type: String, required: true },
})

// "Nome Paciente" -> "NP"
const initials = computed(() =>
  props.name
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() ?? '')
    .join('')
)
</script>

<template>
  <div
    class="flex shrink-0 select-none items-center justify-center rounded-full bg-[#042d5c] text-white"
    aria-hidden="true"
  >
    {{ initials }}
  </div>
</template>