<script setup>
defineProps({
  horarios: { type: Array, default: () => [] }, // [{ id, inicio, fim, especialidade }]
  carregando: Boolean,
})
const emit = defineEmits(['bloquear'])
</script>

<template>
  <div>
    <h3 class="text-xs font-bold text-[#0b2f5b]">Horários Agendados</h3>
    <p class="mt-1 mb-3 text-[11px] text-gray-500">
      Clique em um horário para bloquear pontualmente caso tenha compromisso.
    </p>

    <p v-if="carregando" class="text-xs text-gray-500">Carregando...</p>
    <p v-else-if="!horarios.length" class="rounded-lg bg-[#f1f4fa] p-4 text-center text-[11px] text-gray-500">
      Nenhum horário disponível neste dia. Defina uma faixa de atendimento acima.
    </p>

    <ul v-else class="flex flex-col gap-2">
      <li v-for="h in horarios" :key="h.id">
        <button
          type="button"
          class="flex w-full cursor-pointer items-center justify-between rounded-md bg-[#eef2ff] px-4 py-3 text-left transition hover:bg-[#e3e9fb]"
          :aria-label="`Bloquear horário ${h.inicio} - ${h.fim}`"
          @click="emit('bloquear', h)"
        >
          <span class="text-[11px] font-bold text-[#0b2f5b]">{{ h.inicio }} - {{ h.fim }}</span>
          <span class="flex items-center gap-3">
            <span class="rounded-md bg-[#f6f8fe] px-2 py-0.5 text-[10px] text-slate-600">
              {{ h.especialidade }}
            </span>
            <span class="text-sm leading-none text-gray-500">×</span>
          </span>
        </button>
      </li>
    </ul>
  </div>
</template>