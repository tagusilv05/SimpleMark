<script setup>
/**
 * CardCabecalhoProfissional — card do topo do perfil: foto, selo, nome, CRM, especialidades e nota
 *
 *   <CardCabecalhoProfissional
 *     name="Dr. Nome Profissional"
 *     crm="CRM 123456/SP"
 *     :photo="fotoUrl"
 *     verified
 *     :rating="4.8"
 *     :review-count="124"
 *     :specialties="['Cardiologia Clínica']"
 *   />
 *
 * PROPS
 *   name, crm       String
 *   photo           String   URL da foto (sem foto mostra um espaço reservado)
 *   verified        Boolean  mostra o selo "Verificado" sobre a foto
 *   rating          Number   nota média
 *   reviewCount     Number   total de avaliações
 *   specialties     Array    lista de nomes de especialidades
 *
 * EVENTOS
 *   @ver-avaliacoes  clique nas estrelas / nota / "(N avaliações)" no canto direito do card
 */
import EstrelasAvaliacao from '@/components/paciente/EstrelasAvaliacao.vue'

defineProps({
  name: { type: String, required: true },
  crm: { type: String, default: '' },
  photo: { type: String, default: '' },
  verified: { type: Boolean, default: false },
  rating: { type: Number, default: 0 },
  reviewCount: { type: Number, default: 0 },
  specialties: { type: Array, default: () => [] },
})

const emit = defineEmits(['ver-avaliacoes'])

const ICON_DOC =
  'M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z'
const ICON_CLIPBOARD =
  'M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 0 0 2.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 0 0-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 0 0 .75-.75 2.25 2.25 0 0 0-.1-.664m-5.8 0A2.251 2.251 0 0 1 13.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25Z'
const ICON_USER =
  'M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.5 20.118a7.5 7.5 0 0 1 15 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.5-1.632Z'
</script>

<template>
  <section
    class="flex flex-col gap-8 rounded-xl bg-white p-8 shadow-[0_2px_12px_rgba(11,47,91,0.08)] sm:flex-row"
  >
    <!-- Foto + selo -->
    <div class="relative h-52 w-52 shrink-0 self-center sm:self-start">
      <img v-if="photo" :src="photo" :alt="name" class="size-full rounded-lg object-cover" />
      <div
        v-else
        class="flex size-full items-center justify-center rounded-lg bg-[#eef2fb] text-[#0b2f5b]/30"
      >
        <svg
          class="size-24"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke-width="1"
          stroke="currentColor"
          aria-hidden="true"
        >
          <path stroke-linecap="round" stroke-linejoin="round" :d="ICON_USER" />
        </svg>
      </div>

      <span
        v-if="verified"
        class="absolute -bottom-3 left-1/2 inline-flex -translate-x-1/2 items-center gap-1.5 rounded-full bg-[#0b9aa3] px-3 py-1.5 text-sm font-semibold text-white shadow-md"
      >
        <svg class="size-4" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <circle cx="12" cy="12" r="10" fill="currentColor" />
          <path
            d="m7.5 12.5 3 3 6-6.5"
            stroke="#0b9aa3"
            stroke-width="2.2"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
        </svg>
        Verificado
      </span>
    </div>

    <!-- Dados -->
    <div class="flex flex-1 flex-col gap-6">
      <div class="flex flex-wrap items-start justify-between gap-4">
        <div class="flex flex-col gap-2">
          <h1 class="text-3xl font-bold text-[#0b2f5b]">{{ name }}</h1>

          <span
            v-if="crm"
            class="inline-flex w-fit items-center gap-1.5 rounded bg-[#eef2fb] px-2 py-1 text-xs font-semibold text-[#0b2f5b]"
          >
            <svg
              class="size-3.5"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke-width="1.8"
              stroke="currentColor"
              aria-hidden="true"
            >
              <path stroke-linecap="round" stroke-linejoin="round" :d="ICON_DOC" />
            </svg>
            {{ crm }}
          </span>
        </div>

        <button
          type="button"
          class="flex cursor-pointer flex-col items-end gap-1 transition-opacity hover:opacity-70"
          aria-label="Ver todas as avaliações"
          @click="emit('ver-avaliacoes')"
        >
          <div class="flex items-center gap-2">
            <EstrelasAvaliacao :rating="rating" size="md" />
            <span class="font-bold text-[#0b2f5b]">{{ rating.toFixed(1) }}</span>
          </div>
          <span class="text-sm text-gray-500">({{ reviewCount }} avaliações)</span>
        </button>
      </div>

      <div v-if="specialties.length" class="flex flex-col gap-3">
        <h2 class="flex items-center gap-2 text-lg font-semibold text-[#0b2f5b]">
          <svg
            class="size-6 text-[#0b9aa3]"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="1.5"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path stroke-linecap="round" stroke-linejoin="round" :d="ICON_CLIPBOARD" />
          </svg>
          Especialidades
        </h2>

        <ul class="flex flex-wrap gap-2">
          <li
            v-for="esp in specialties"
            :key="esp"
            class="rounded-full border border-[#b8cdf0] bg-[#e8f0fe] px-4 py-1.5 text-[#4a6fa5]"
          >
            {{ esp }}
          </li>
        </ul>
      </div>
    </div>
  </section>
</template>