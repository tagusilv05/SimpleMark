<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// status: 'confirmado' | 'realizada' | 'expirado'
const agendamentos = ref([
  {
    id: 1,
    data: '08 Nov 2024',
    horario: '10:00 - 10:30',
    tipo: 'Teleconsulta',
    especialidade: 'Cardiologia',
    status: 'confirmado',
    profissional: { id: 1, nome: 'Dr. Nome do Profissional', nota: 4.8 },
  },
  {
    id: 2,
    data: '12 Nov 2024',
    horario: '14:30 - 15:00',
    tipo: 'Teleconsulta',
    especialidade: 'Ortopedia e Traumatologia',
    status: 'realizada',
    profissional: { id: 2, nome: 'Dr. Nome do Profissional', nota: 4.8 },
  },
  {
    id: 3,
    data: '20 Nov 2024',
    horario: '11:15 - 12:00',
    tipo: 'Teleconsulta',
    especialidade: 'Dermatologia',
    status: 'expirado',
    profissional: { id: 3, nome: 'Dra. Nome do Profissional', nota: 4.8 },
  },
])

const iniciais = (nome) =>
  nome
    .replace(/^dra?\.?\s+/i, '')
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((p) => p[0].toUpperCase())
    .join('')

const entrarNaChamada = (id) => console.log('Entrar na chamada', id)

function cancelar(id) {
  if (!window.confirm('Deseja realmente cancelar esta consulta?')) return
  agendamentos.value = agendamentos.value.filter((a) => a.id !== id)
}

const verMedico = (id) => router.push({ name: 'perfilProfissional', params: { id } })
const verDetalhes = (id) => router.push({ name: 'detalhesConsulta', params: { id } })
const avaliar = (id) => router.push({ name: 'avaliarConsulta', params: { id } })
</script>

<template>
  <h1 class="text-4xl font-bold text-[#0b2f5b]">Meus Agendamentos</h1>

  <p v-if="!agendamentos.length" class="text-sm text-gray-500">
    Você ainda não possui agendamentos.
  </p>

  <div class="flex max-w-215 flex-col gap-4">
    <article
      v-for="ag in agendamentos"
      :key="ag.id"
      class="rounded-xl bg-white px-4 py-5 shadow-sm"
    >
      <div class="flex items-start justify-between gap-4">
        <div class="flex items-start gap-3">
          <div
            class="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-[#0b2f5b] text-sm font-bold text-white"
          >
            {{ iniciais(ag.profissional.nome) }}
          </div>

          <div class="flex flex-col gap-1">
            <div class="flex items-center gap-2">
              <h2 class="text-xl font-semibold text-[#0b2f5b]">{{ ag.profissional.nome }}</h2>
              <div class="flex items-center gap-1 text-xs font-semibold text-gray-700">
                <span class="flex text-[#1a9aa6]">
                  <svg
                    v-for="i in 5"
                    :key="i"
                    class="h-3 w-3"
                    :class="i <= Math.round(ag.profissional.nota) ? 'opacity-100' : 'opacity-25'"
                    viewBox="0 0 24 24"
                    fill="currentColor"
                  >
                    <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
                  </svg>
                </span>
                {{ ag.profissional.nota.toFixed(1) }}
              </div>
            </div>

            <p class="text-sm text-gray-500">{{ ag.especialidade }}</p>

            <div class="flex items-center gap-2">
              <span class="rounded bg-[#1a9aa6] px-2 py-0.5 text-[10px] font-bold uppercase text-white">
                {{ ag.tipo }}
              </span>

              <span
                v-if="ag.status === 'confirmado'"
                class="flex items-center gap-1 rounded bg-green-100 px-2 py-0.5 text-[10px] font-semibold text-green-700"
              >
                <svg class="h-3 w-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="12" cy="12" r="10" /><path d="M8 12l3 3 5-6" />
                </svg>
                Confirmado
              </span>
              <span
                v-else-if="ag.status === 'realizada'"
                class="flex items-center gap-1 rounded bg-blue-50 px-2 py-0.5 text-[10px] font-semibold text-[#0b2f5b]"
              >
                <svg class="h-3 w-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="12" cy="12" r="10" /><path d="M8 12l3 3 5-6" />
                </svg>
                Realizada
              </span>
              <span
                v-else
                class="flex items-center gap-1 rounded bg-red-100 px-2 py-0.5 text-[10px] font-semibold text-red-700"
              >
                <svg class="h-3 w-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="12" cy="12" r="10" /><path d="M12 8v4M12 16h.01" />
                </svg>
                Prazo Expirado
              </span>
            </div>
          </div>
        </div>

        <div class="flex flex-col gap-2 text-sm font-medium text-[#0b2f5b]">
          <div class="flex items-center gap-2">
            <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="3" y="4" width="18" height="18" rx="2" /><path d="M16 2v4M8 2v4M3 10h18" />
            </svg>
            {{ ag.data }}
          </div>
          <div class="flex items-center gap-2">
            <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10" /><path d="M12 6v6l4 2" />
            </svg>
            {{ ag.horario }}
          </div>
        </div>
      </div>

      <hr class="my-4 border-gray-100" />

      <div class="grid grid-cols-3 gap-4">
        <button
          type="button"
          class="flex cursor-pointer items-center justify-center gap-2 rounded-lg border border-[#0b2f5b] bg-white px-4 py-2 text-xs font-semibold text-[#0b2f5b] transition hover:bg-blue-50"
          @click="verMedico(ag.profissional.id)"
        >
          <svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="8" r="4" /><path d="M4 21c0-4 4-6 8-6s8 2 8 6" />
          </svg>
          Ver informações do médico
        </button>

        <button
          type="button"
          class="flex cursor-pointer items-center justify-center gap-2 rounded-lg border border-[#0b2f5b] bg-white px-4 py-2 text-xs font-semibold text-[#0b2f5b] transition hover:bg-blue-50"
          @click="verDetalhes(ag.id)"
        >
          <svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10" /><path d="M12 16v-4M12 8h.01" />
          </svg>
          Detalhes da consulta
        </button>

        <button
          v-if="ag.status === 'confirmado'"
          type="button"
          class="flex cursor-pointer items-center justify-center gap-2 rounded-lg bg-[#0b2f5b] px-4 py-2 text-xs font-semibold text-white transition hover:bg-[#12407a]"
          @click="entrarNaChamada(ag.id)"
        >
          <svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="2" y="6" width="14" height="12" rx="2" /><path d="M16 10l6-3v10l-6-3z" />
          </svg>
          Entrar na Chamada
        </button>
        <button
          v-else-if="ag.status === 'realizada'"
          type="button"
          class="flex cursor-pointer items-center justify-center gap-2 rounded-lg bg-[#0b2f5b] px-4 py-2 text-xs font-semibold text-white transition hover:bg-[#12407a]"
          @click="avaliar(ag.id)"
        >
          <svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
          </svg>
          Avaliar Atendimento
        </button>
        <button
          v-else
          type="button"
          disabled
          class="flex cursor-not-allowed items-center justify-center gap-2 rounded-lg bg-[#eef2fb] px-4 py-2 text-xs font-semibold text-gray-400"
        >
          <svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M10 13a5 5 0 007 0l3-3a5 5 0 00-7-7l-1 1M14 11a5 5 0 00-7 0l-3 3a5 5 0 007 7l1-1M3 3l18 18" />
          </svg>
          Link Expirado
        </button>
      </div>

      <div v-if="ag.status === 'confirmado'" class="mt-4 text-center">
        <button
          type="button"
          class="cursor-pointer text-xs font-semibold text-red-700 hover:underline"
          @click="cancelar(ag.id)"
        >
          Cancelar
        </button>
      </div>
    </article>
  </div>
</template>