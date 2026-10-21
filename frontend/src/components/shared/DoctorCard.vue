<script setup>
/**
 * DoctorCard — cartão de profissional (foto, nome, especialidade, nota e botão "Ver Perfil")
 *
 * COMO USAR (na página):
 *
 *   import DoctorCard from '@/components/shared/DoctorCard.vue'
 *
 *   <DoctorCard
 *     name="Dr. Nome Profissional"
 *     specialty="Cardiologia"
 *     :rating="5.0"
 *     @view="router.push({ name: 'perfil-profissional', params: { id: 1 } })"
 *   />
 *
 *   <DoctorCard name="Maria Souza" specialty="Pediatria" photo="https://.../foto.jpg"
 *               :rating="4.8" :count="82" />
 *
 * PROPS
 *   name       String  (obrigatória)  nome exibido; sem foto, as iniciais viram o avatar.
 *   specialty  String  (padrão: '')   especialidade, em cinza abaixo do nome.
 *   photo      String  (padrão: '')   URL da foto. Vazio (ou imagem que falhe) = avatar com iniciais.
 *   rating     Number | null  (padrão: null)  nota de 0 a 5 (ver StarRating).
 *   count      Number | null  (padrão: null)  total de avaliações (ver StarRating).
 *
 * EVENTOS
 *   @view  disparado ao clicar em "Ver Perfil". O pai decide para onde navegar.
 *
 * DEPENDÊNCIAS
 *   - @/components/shared/UserAvatar.vue, StarRating.vue e FormButton.vue
 *   - Tailwind CSS
 */

import { ref, watch } from 'vue'
import UserAvatar from '@/components/shared/UserAvatar.vue'
import StarRating from '@/components/shared/StarRating.vue'
import FormButton from '@/components/shared/FormButton.vue'

const props = defineProps({
  name: { type: String, required: true },
  specialty: { type: String, default: '' },
  photo: { type: String, default: '' },
  rating: { type: Number, default: null },
  count: { type: Number, default: null },
})

defineEmits(['view'])

// Se a foto não carregar, cai no avatar com iniciais
const photoFailed = ref(false)
watch(
  () => props.photo,
  () => (photoFailed.value = false),
)
</script>

<template>
  <article
    class="flex flex-col items-center gap-3 rounded-xl border border-gray-200 bg-white p-3.5 shadow-[0_1px_4px_rgba(11,47,91,0.06)]"
  >
    <img
      v-if="photo && !photoFailed"
      :src="photo"
      :alt="`Foto de ${name}`"
      class="size-14 rounded-full object-cover"
      @error="photoFailed = true"
    />
    <UserAvatar v-else :name="name" class="size-14 text-base font-bold" />

    <div class="flex w-full flex-col items-center gap-1 text-center">
      <h3 class="w-full truncate text-sm font-medium text-[#0b2f5b]" :title="name">{{ name }}</h3>
      <p class="text-[11px] font-semibold text-gray-500">{{ specialty }}</p>
    </div>

    <StarRating :value="rating" :count="count" />

    <FormButton class="h-8! w-full text-xs" @click="$emit('view')">Ver Perfil</FormButton>
  </article>
</template>
