<script setup>
/**
 * CardAvaliacao — uma avaliação de paciente, em dois formatos
 *
 *   <CardAvaliacao variant="compact" name="Maria" date="2024-05-15" :rating="5" text="..." />
 *       linha enxuta, sem avatar, com divisória (perfil do profissional)
 *
 *   <CardAvaliacao variant="card" name="Maria" date="2024-05-12" :rating="5" text="..." />
 *       card branco com avatar (tela de todas as avaliações)
 *
 * PROPS
 *   name     String  nome do paciente
 *   date     String  data ISO 'YYYY-MM-DD' (o componente formata)
 *   rating   Number  nota de 0 a 5
 *   text     String  comentário
 *   variant  'card' | 'compact'
 *
 * DEPENDÊNCIA: @/components/shared/UserAvatar.vue (só no formato "card")
 */
import UserAvatar from '@/components/shared/UserAvatar.vue'
import EstrelasAvaliacao from '@/components/paciente/EstrelasAvaliacao.vue'
import { dataCurta, dataLonga } from '@/utils/datas'

defineProps({
  name: { type: String, required: true },
  date: { type: String, required: true },
  rating: { type: Number, required: true },
  text: { type: String, default: '' },
  variant: { type: String, default: 'card', validator: (v) => ['card', 'compact'].includes(v) },
})
</script>

<template>
  <!-- Compacto -->
  <article
    v-if="variant === 'compact'"
    class="flex flex-col gap-2 border-b border-gray-200 pb-5 last:border-b-0 last:pb-0"
  >
    <div class="flex items-start justify-between gap-4">
      <div class="flex flex-col gap-1">
        <h3 class="text-[15px] font-bold text-[#0b2f5b]">{{ name }}</h3>
        <EstrelasAvaliacao :rating="rating" size="sm" />
      </div>
      <time :datetime="date" class="text-sm font-semibold text-gray-500">{{ dataCurta(date) }}</time>
    </div>

    <p class="text-[15px] leading-relaxed text-gray-700">{{ text }}</p>
  </article>

  <!-- Card com avatar -->
  <article
    v-else
    class="rounded-xl bg-white p-8 shadow-[0_2px_12px_rgba(11,47,91,0.08)]"
  >
    <header class="flex items-start justify-between gap-4">
      <div class="flex items-center gap-4">
        <UserAvatar :name="name" class="size-12 text-sm font-bold" />

        <div class="flex flex-col leading-tight">
          <h3 class="text-lg text-[#0b2f5b]">{{ name }}</h3>
          <time :datetime="date" class="text-sm text-gray-500">Avaliado em {{ dataLonga(date) }}</time>
        </div>
      </div>

      <EstrelasAvaliacao :rating="rating" size="md" />
    </header>

    <p class="mt-4 leading-relaxed text-gray-800">{{ text }}</p>
  </article>
</template>
