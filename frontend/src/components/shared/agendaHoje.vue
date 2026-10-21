<script setup>
defineProps({
  dataTexto: { type: String, required: true },
  agenda: { type: Array, default: () => [] },
  carregando: Boolean,
})

const hora = (iso) => iso.slice(11, 16)
const rotuloTipo = {
  teleconsulta: 'Teleconsulta',
  online: 'Teleconsulta',
  consulta: 'Consulta',
  retorno: 'Retorno',
  presencial: 'Presencial',
}
const rotuloStatus = {
  agendada: 'Agendada',
  agendado: 'Agendada',
  confirmada: 'Confirmada',
  pendente: 'Pendente',
  cancelada: 'Cancelada',
  cancelado: 'Cancelada',
  realizada: 'Realizada',
  realizado: 'Realizada',
}

const atual = (item) => {
  const agora = Date.now()
  return agora >= new Date(item.inicio).getTime() && agora < new Date(item.fim).getTime()
}
</script>

<template>
  <section class="rounded-xl border border-[#e5e9f2] bg-white p-5">
    <div class="mb-4 flex items-start justify-between gap-4">
      <div>
        <h3 class="font-bold text-[#0b2f5b]">Agenda de Atendimentos</h3>
        <p class="mt-0.5 text-[11px] text-gray-500">
          {{ dataTexto }} • {{ agenda.length }}
          {{ agenda.length === 1 ? 'Horário Marcado' : 'Horários Marcados' }}
        </p>
      </div>
      <!-- TODO: ajustar para o nome real da rota da agenda completa -->
      <RouterLink
        :to="{ name: 'agendamentosDoProfissional' }"
        class="shrink-0 text-[11px] font-bold text-[#0b2f5b] hover:underline"
      >
        Ver agenda completa ›
      </RouterLink>
    </div>

    <p v-if="carregando" class="text-sm text-gray-500">Carregando...</p>

    <!-- Estado vazio -->
    <div
      v-else-if="!agenda.length"
      class="flex min-h-52 flex-col items-center justify-center rounded-xl bg-[#f1f4fa] px-6 py-10 text-center"
    >
      <div class="mb-3 flex h-10 w-10 items-center justify-center rounded-lg bg-white text-[#0b2f5b] shadow-sm">
        <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="4" width="18" height="18" rx="2" /><path d="M16 2v4M8 2v4M3 10h18" /><path d="m9 16 2 2 4-4" />
        </svg>
      </div>
      <h4 class="text-sm font-bold text-[#0b2f5b]">Sua agenda está livre hoje</h4>
      <p class="mt-1 max-w-xs text-[11px] leading-relaxed text-gray-500">
        Nenhum paciente agendado para esta data. Você pode disponibilizar novos horários de
        atendimento ou agendar uma consulta manualmente.
      </p>
    </div>

    <ul v-else class="flex flex-col gap-2.5">
      <li
        v-for="item in agenda"
        :key="item.id"
        class="flex items-center gap-3.5 rounded-lg border p-2.5"
        :class="atual(item) ? 'border-indigo-200 bg-indigo-50' : 'border-transparent'"
      >
        <div
          class="flex min-w-13 flex-col items-center rounded-md p-1.5"
          :class="atual(item) ? 'bg-[#0b2f5b] text-white' : 'bg-slate-100 text-[#0b2f5b]'"
        >
          <strong class="text-sm">{{ hora(item.inicio) }}</strong>
          <span class="text-[10px] opacity-80">{{ atual(item) ? 'Atual' : hora(item.fim) }}</span>
        </div>

        <div class="flex flex-1 flex-col gap-0.5">
          <span class="text-sm font-semibold text-[#0b2f5b]">
            {{ item.paciente_nome }}
            <span class="ml-1.5 rounded-md bg-teal-600 px-2 py-0.5 text-[10px] font-medium text-white">
              {{ rotuloTipo[item.tipo] ?? item.tipo }}
            </span>
          </span>
          <span class="text-[11px] text-gray-500">Informações do paciente</span>
        </div>

        <span class="rounded-lg bg-[#0b2f5b] px-3.5 py-1.5 text-xs text-white">
          {{ rotuloStatus[item.status] ?? item.status }}
        </span>
      </li>
    </ul>
  </section>
</template>