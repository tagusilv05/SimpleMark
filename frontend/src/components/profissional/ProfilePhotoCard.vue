<script setup>
/**
 * ProfilePhotoCard — cartão com a foto de perfil e o botão "Carregar nova foto"
 *
 * COMO USAR (na página):
 *
 *   import ProfilePhotoCard from '@/components/professional/ProfilePhotoCard.vue'
 *
 *   <ProfilePhotoCard :photo="fotoUrl" @change="trocarFoto" />
 *   <ProfilePhotoCard
 *     photo="/img/medico.jpg"
 *     title="Sua foto de perfil profissional"
 *     description="Recomendamos foto com boa iluminação, com foco nítido"
 *     @change="(file) => enviar(file)"
 *   />
 *
 * PROPS
 *   photo        String  (padrão: '')
 *                  URL da foto atual. Vazio = mostra um avatar genérico.
 *   title        String  (padrão: 'Sua foto de perfil profissional')
 *   description  String  (padrão: 'Recomendamos foto com boa iluminação, com foco nítido')
 *   buttonLabel  String  (padrão: 'Carregar nova foto')
 *
 * EVENTOS
 *   change   emitido com o File escolhido (só imagens). O componente NÃO envia
 *            a foto para o servidor nem altera a prop `photo`: a página decide
 *            o que fazer (upload, preview com URL.createObjectURL etc.).
 *
 * ESTILO
 *   Tailwind. Foto redonda com borda branca, selo de câmera turquesa e fundo azul claro.
 *
 * DEPENDÊNCIAS
 *   - FormButton (shared)
 *   - Tailwind CSS
 */
import { ref } from 'vue'
import FormButton from '@/components/shared/FormButton.vue'

defineProps({
  photo: { type: String, default: '' },
  title: { type: String, default: 'Sua foto de perfil profissional' },
  description: {
    type: String,
    default: 'Recomendamos foto com boa iluminação, com foco nítido',
  },
  buttonLabel: { type: String, default: 'Carregar nova foto' },
})

const emit = defineEmits(['change'])

const fileInput = ref(null)

const uploadIcon =
  'M12 16.5V9.75m0 0 3 3m-3-3-3 3M6.75 19.5a4.5 4.5 0 0 1-1.41-8.775 5.25 5.25 0 0 1 10.233-2.33 3 3 0 0 1 3.758 3.848A3.752 3.752 0 0 1 18 19.5H6.75Z'

function onFileChange(event) {
  const file = event.target.files?.[0]
  if (file) emit('change', file)
  // permite escolher o mesmo arquivo de novo depois
  event.target.value = ''
}
</script>

<template>
  <div
    class="flex flex-wrap items-center gap-6 rounded-2xl bg-[#eef1fe] p-6"
  >
    <!-- Foto + selo de câmera -->
    <div class="relative shrink-0">
      <div class="size-28 overflow-hidden rounded-full border-4 border-white bg-white shadow-sm">
        <img v-if="photo" :src="photo" alt="Foto de perfil" class="size-full object-cover" />
        <svg
          v-else
          class="size-full p-6 text-gray-400"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke-width="1.5"
          stroke="currentColor"
          aria-hidden="true"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z"
          />
        </svg>
      </div>
      <span
        class="absolute bottom-1 right-1 flex size-8 items-center justify-center rounded-full border-2 border-white bg-[#0a9ba5] text-white"
      >
        <svg
          class="size-4"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke-width="2"
          stroke="currentColor"
          aria-hidden="true"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M6.827 6.175A2.31 2.31 0 0 1 5.186 7.23c-.38.054-.757.112-1.134.175C2.999 7.58 2.25 8.507 2.25 9.574V18a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18V9.574c0-1.067-.75-1.994-1.802-2.169a47.865 47.865 0 0 0-1.134-.175 2.31 2.31 0 0 1-1.64-1.055l-.822-1.316a2.192 2.192 0 0 0-1.736-1.039 48.774 48.774 0 0 0-5.232 0 2.192 2.192 0 0 0-1.736 1.039l-.821 1.316Z"
          />
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M16.5 12.75a4.5 4.5 0 1 1-9 0 4.5 4.5 0 0 1 9 0Z"
          />
        </svg>
      </span>
    </div>

    <!-- Texto -->
    <div class="min-w-48 flex-1">
      <p class="text-base font-bold text-[#0b2f5b]">{{ title }}</p>
      <p class="mt-1 text-[15px] text-gray-700">{{ description }}</p>
    </div>

    <!-- Botão de upload -->
    <FormButton :icon="uploadIcon" @click="fileInput.click()">{{ buttonLabel }}</FormButton>
    <input ref="fileInput" type="file" accept="image/*" class="hidden" @change="onFileChange" />
  </div>
</template>
