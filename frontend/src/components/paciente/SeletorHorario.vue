<script setup>
/**
 * SeletorHorario — botões de horário disponíveis para o dia escolhido
 *
 *   <SeletorHorario v-model="horario" :horarios="['09:00', '10:30']" title="Horários para Terça, 21 de Maio" />
 *
 * PROPS
 *   modelValue  String  horário selecionado (v-model)
 *   horarios    Array   lista de strings 'HH:MM'
 *   title       String  título acima dos botões
 */
defineProps({
  modelValue: { type: String, default: '' },
  horarios: { type: Array, default: () => [] },
  title: { type: String, default: 'Horários disponíveis' },
})

const emit = defineEmits(['update:modelValue'])
</script>

<template>
  <div>
    <h3 class="mb-3 text-sm font-bold text-[#0b2f5b]">{{ title }}</h3>

    <div v-if="horarios.length" class="grid grid-cols-3 gap-3" role="radiogroup" :aria-label="title">
      <button
        v-for="h in horarios"
        :key="h"
        type="button"
        role="radio"
        :aria-checked="h === modelValue"
        class="cursor-pointer rounded-lg border px-3 py-2 text-sm font-semibold text-[#0b2f5b] transition-colors"
        :class="
          h === modelValue
            ? 'border-[#0b2f5b] ring-1 ring-[#0b2f5b]'
            : 'border-gray-300 hover:border-[#0b2f5b]'
        "
        @click="emit('update:modelValue', h)"
      >
        {{ h }}
      </button>
    </div>

    <p v-else class="text-sm text-gray-500">Não há horários disponíveis neste dia.</p>
  </div>
</template>
