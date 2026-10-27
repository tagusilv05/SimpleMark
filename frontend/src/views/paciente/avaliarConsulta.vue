<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const consulta = {
  data: '14 de Outubro, 2023',
  especialidade: 'Cardiologia',
  profissional: { nome: 'Dr. Nome do Profissional', crm: '12345-SP', iniciais: 'NP' },
}

const nota = ref(0)
const comentario = ref('')

function enviar() {
  console.log('Avaliação enviada:', { nota: nota.value, comentario: comentario.value.trim() })
  router.push({ name: 'meusAgendamentos' })
}
</script>

<template>
  <section class="mx-auto flex w-full max-w-125 flex-col gap-4 rounded-xl bg-white p-6 shadow-sm">
    <div class="flex items-center gap-3">
      <div
        class="flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-[#0b2f5b] text-lg font-bold text-white"
      >
        {{ consulta.profissional.iniciais }}
      </div>
      <div>
        <h1 class="text-xl font-semibold text-[#0b2f5b]">{{ consulta.profissional.nome }}</h1>
        <p class="text-sm text-gray-600">
          {{ consulta.especialidade }} • CRM {{ consulta.profissional.crm }}
        </p>
        <p class="text-xs font-semibold text-[#1a9aa6]">
          Consulta realizada em {{ consulta.data }}
        </p>
      </div>
    </div>

    <hr class="border-gray-100" />

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

    <button
      type="button"
      :disabled="!nota"
      class="flex cursor-pointer items-center justify-center gap-2 rounded-lg bg-[#0b2f5b] px-5 py-3 text-sm font-semibold text-white transition hover:bg-[#12407a] disabled:cursor-not-allowed disabled:opacity-50"
      @click="enviar"
    >
      <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" />
      </svg>
      Enviar Avaliação
    </button>
  </section>
</template>