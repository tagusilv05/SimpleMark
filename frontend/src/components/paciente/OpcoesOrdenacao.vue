<script setup>
/**
 * OpcoesOrdenacao — card "ORDENAR POR" com a opção ativa em destaque
 *
 *   <OpcoesOrdenacao v-model="ordem" />
 *
 * PROPS
 *   modelValue  String  valor da opção selecionada (v-model)
 *   options     Array   [{ value, label }] — já vem com: recentes, melhores, menores
 */
defineProps({
  modelValue: { type: String, default: 'recentes' },
  options: {
    type: Array,
    default: () => [
      { value: 'recentes', label: 'Mais recentes' },
      { value: 'melhores', label: 'Melhores avaliadas' },
      { value: 'menores', label: 'Menores avaliadas' },
    ],
  },
})

const emit = defineEmits(['update:modelValue'])
</script>

<template>
  <section class="rounded-xl bg-white p-6 shadow-[0_2px_12px_rgba(11,47,91,0.08)]">
    <h3 class="mb-4 text-xs font-bold uppercase tracking-wider text-gray-600">Ordenar por</h3>

    <div class="flex flex-col gap-2" role="radiogroup" aria-label="Ordenar avaliações">
      <button
        v-for="op in options"
        :key="op.value"
        type="button"
        role="radio"
        :aria-checked="op.value === modelValue"
        class="flex w-full cursor-pointer items-center justify-between rounded-lg border px-3 py-3 text-left text-[15px] transition-colors"
        :class="
          op.value === modelValue
            ? 'border-[#0b9aa3] bg-[#0b9aa3] text-white'
            : 'border-gray-300 bg-white text-gray-800 hover:bg-[#f3f6fb]'
        "
        @click="emit('update:modelValue', op.value)"
      >
        <span>{{ op.label }}</span>

        <svg
          v-if="op.value === modelValue"
          class="size-4"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke-width="2.5"
          stroke="currentColor"
          aria-hidden="true"
        >
          <path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" />
        </svg>
      </button>
    </div>
  </section>
</template>
