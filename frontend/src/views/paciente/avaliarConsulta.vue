<script setup>
/**
 * Avaliar Consulta — o paciente dá de 1 a 5 estrelas e um comentário opcional
 *
 * API:
 *   GET  /consultas/minhas/{id}                          dados da consulta (profissional, data, pode_avaliar)
 *   POST /api/v1/avaliacoes/consultas/{id}/avaliacao     { nota, feedback }
 *
 * Só consulta realizada e ainda não avaliada pode ser avaliada (o backend responde
 * 409 nos outros casos). Se já houver avaliação, a tela a mostra sem o formulário.
 */
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '@/services/api'

const route = useRoute()
const router = useRouter()

const MESES = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

const consulta = ref(null)
const carregando = ref(true)
const enviando = ref(false)
const erro = ref('')
const nota = ref(0)
const comentario = ref('')

const iniciais = (nome) =>
  nome
    .replace(/^dra?\.?\s+/i, '')
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((p) => p[0].toUpperCase())
    .join('')

const dataTexto = computed(() => {
  if (!consulta.value) return ''
  const [ano, mes, dia] = consulta.value.data.split('-')
  return `${Number(dia)} de ${MESES[Number(mes) - 1]}, ${ano}`
})

// Motivo para não mostrar o formulário (null = pode avaliar)
const bloqueio = computed(() => {
  const c = consulta.value
  if (!c || c.pode_avaliar) return null
  if (c.avaliacao) return 'avaliada'
  if (c.status === 'cancelada') return 'Esta consulta foi cancelada e não pode ser avaliada.'
  return 'A avaliação fica disponível depois que a consulta for realizada.'
})

async function carregar() {
  carregando.value = true
  erro.value = ''
  try {
    consulta.value = await api.get(`/consultas/minhas/${route.params.id}`)
  } catch (e) {
    erro.value = e.message || 'Não foi possível carregar a consulta.'
  } finally {
    carregando.value = false
  }
}

async function enviar() {
  if (!nota.value || enviando.value) return
  enviando.value = true
  erro.value = ''
  try {
    await api.post(`/api/v1/avaliacoes/consultas/${route.params.id}/avaliacao`, {
      nota: nota.value,
      feedback: comentario.value.trim() || null,
    })
    router.push({ name: 'meusAgendamentos' })
  } catch (e) {
    erro.value = e.message || 'Não foi possível enviar a avaliação. Tente novamente.'
    // 409: já avaliada ou ainda não realizada -> recarrega para mostrar o estado real
    if (e.status === 409) await carregar()
  } finally {
    enviando.value = false
  }
}

onMounted(carregar)
</script>

<template>
  <p v-if="carregando" class="mx-auto text-sm text-gray-500">Carregando consulta...</p>

  <p
    v-else-if="!consulta"
    class="mx-auto w-full max-w-125 rounded-xl bg-white p-6 text-sm font-medium text-red-700 shadow-sm"
    role="alert"
  >
    {{ erro }}
  </p>

  <section v-else class="mx-auto flex w-full max-w-125 flex-col gap-4 rounded-xl bg-white p-6 shadow-sm">
    <div class="flex items-center gap-3">
      <div
        class="flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-[#0b2f5b] text-lg font-bold text-white"
      >
        {{ iniciais(consulta.profissional.nome) }}
      </div>
      <div>
        <h1 class="text-xl font-semibold text-[#0b2f5b]">{{ consulta.profissional.nome }}</h1>
        <p class="text-sm text-gray-600">
          {{ consulta.profissional.especialidade }}
        </p>
        <p class="text-xs font-semibold text-[#1a9aa6]">
          Consulta de {{ dataTexto }}
        </p>
      </div>
    </div>

    <hr class="border-gray-100" />

    <!-- Já avaliada: mostra a avaliação enviada -->
    <div v-if="bloqueio === 'avaliada'" class="flex flex-col items-center gap-2 text-center" role="status">
      <p class="text-xs font-semibold tracking-wide text-gray-700">VOCÊ JÁ AVALIOU ESTA CONSULTA</p>
      <div v-if="consulta.avaliacao.avaliacao" class="flex gap-1.5 text-[#1a9aa6]">
        <svg
          v-for="i in 5"
          :key="i"
          class="h-7 w-7"
          :class="i <= consulta.avaliacao.avaliacao ? '' : 'text-gray-300'"
          viewBox="0 0 24 24"
          fill="currentColor"
          aria-hidden="true"
        >
          <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
        </svg>
      </div>
      <p v-if="consulta.avaliacao.feedback" class="text-sm text-gray-600">
        “{{ consulta.avaliacao.feedback }}”
      </p>
    </div>

    <p v-else-if="bloqueio" class="text-center text-sm text-gray-600" role="status">{{ bloqueio }}</p>

    <template v-else>
    <div class="flex flex-col items-center gap-2">
      <p class="text-xs font-semibold tracking-wide text-gray-700">COMO FOI SUA EXPERIÊNCIA?</p>
      <div class="flex gap-1.5">
        <button
          v-for="i in 5"
          :key="i"
          type="button"
          :aria-label="`${i} ${i === 1 ? 'estrela' : 'estrelas'}`"
          class="cursor-pointer text-gray-500"
          :class="{ 'text-[#1a9aa6]': i <= nota }"
          @click="nota = i"
        >
          <svg class="h-7 w-7" viewBox="0 0 24 24" :fill="i <= nota ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round">
            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
          </svg>
        </button>
      </div>
    </div>

    <label class="flex flex-col gap-2 text-sm font-semibold text-gray-700">
      Deixe um comentário (opcional)
      <textarea
        v-model="comentario"
        rows="4"
        maxlength="500"
        placeholder="Conte-nos um pouco mais sobre o atendimento..."
        class="resize-none rounded-lg border border-gray-300 bg-[#eef1fc] p-3 text-sm font-normal outline-none placeholder:text-gray-400 focus:border-[#0b2f5b]"
      />
    </label>

    <p v-if="erro" class="text-sm font-medium text-red-700" role="alert">{{ erro }}</p>

    <button
      type="button"
      :disabled="!nota || enviando"
      class="flex cursor-pointer items-center justify-center gap-2 rounded-lg bg-[#0b2f5b] px-5 py-3 text-sm font-semibold text-white transition hover:bg-[#12407a] disabled:cursor-not-allowed disabled:opacity-50"
      @click="enviar"
    >
      <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" />
      </svg>
      {{ enviando ? 'Enviando...' : 'Enviar Avaliação' }}
    </button>
    </template>
  </section>
</template>