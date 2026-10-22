<script setup>
/**
 * ProfessionalManagement — painel "Gerenciamento Profissional"
 *
 * Junta: foto de perfil, apresentação, especialidades ativas e o formulário de
 * nova especialidade, mais o botão "Salvar Alterações".
 *
 * COMO USAR (na página):
 *
 *   import ProfessionalManagement from '@/components/professional/ProfessionalManagement.vue'
 *
 *   <ProfessionalManagement
 *     v-model:bio="profissional.apresentacao"
 *     v-model:specialties="profissional.especialidades"
 *     :photo="profissional.fotoUrl"
 *     :verified="profissional.verificado"
 *     :specialty-options="['Cardiologia', 'Dermatologia']"
 *     @photo-change="enviarFoto"
 *     @save="salvar"
 *   />
 *
 * PROPS
 *   photo             String   (padrão: '')     URL da foto atual.
 *   verified          Boolean  (padrão: false)  mostra o selo "Verificado".
 *   bio               String   (padrão: '')     texto de apresentação. v-model:bio.
 *   specialties       Array    (padrão: [])     v-model:specialties. Cada item:
 *                       { id, name, registration, price }
 *   specialtyOptions  Array    (padrão: [])     opções do select de nova especialidade.
 *   saving            Boolean  (padrão: false)  desabilita o botão salvar enquanto grava.
 *
 * EVENTOS
 *   update:bio, update:specialties   para os v-models acima.
 *   photo-change   File escolhido no cartão da foto.
 *   edit-specialty Item clicado no lápis (a edição em si fica com a página).
 *   save           clique em "Salvar Alterações".
 *
 * OBSERVAÇÕES
 *   - Ao adicionar, o novo item recebe id = Date.now(); o backend deve
 *     validar o registro no conselho.
 *   - A apresentação usa <FormField type="textarea">: o FormField precisa ter
 *     essa variante (veja a nota no fim da resposta).
 *
 * DEPENDÊNCIAS
 *   - ProfilePhotoCard, SpecialtyItem, AddSpecialtyForm
 *   - FormField e FormButton (shared)
 *   - Tailwind CSS
 */
import ProfilePhotoCard from './ProfilePhotoCard.vue'
import SpecialtyItem from './SpecialtyItem.vue'
import AddSpecialtyForm from './AddSpecialtyForm.vue'
import FormField from '@/components/shared/FormField.vue'
import FormButton from '@/components/shared/FormButton.vue'

const props = defineProps({
  photo: { type: String, default: '' },
  verified: { type: Boolean, default: false },
  bio: { type: String, default: '' },
  specialties: { type: Array, default: () => [] },
  specialtyOptions: { type: Array, default: () => [] },
  saving: { type: Boolean, default: false },
})

const emit = defineEmits(['update:bio', 'update:specialties', 'photo-change', 'edit-specialty', 'save'])

function updatePrice(id, price) {
  emit(
    'update:specialties',
    props.specialties.map((s) => (s.id === id ? { ...s, price } : s)),
  )
}

function removeSpecialty(id) {
  emit(
    'update:specialties',
    props.specialties.filter((s) => s.id !== id),
  )
}

function addSpecialty({ specialty, registration, price }) {
  emit('update:specialties', [
    ...props.specialties,
    { id: Date.now(), name: specialty, registration, price },
  ])
}

const checkIcon = 'm4.5 12.75 6 6 9-13.5'
</script>

<template>
  <section class="flex flex-col gap-8 rounded-2xl bg-white p-8 shadow-sm">
    <!-- Cabeçalho -->
    <header class="flex items-center justify-between gap-4">
      <h1 class="text-2xl font-bold text-[#0b2f5b]">Gerenciamento Profissional</h1>
      <span
        v-if="verified"
        class="inline-flex items-center gap-2 rounded-full bg-[#0a9ba5] px-4 py-2 text-xs font-bold text-white"
      >
        <svg class="size-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" :d="checkIcon" />
        </svg>
        Verificado
      </span>
    </header>

    <!-- Foto de perfil -->
    <div class="flex flex-col gap-4">
      <h2 class="text-base font-bold text-[#0b2f5b]">Foto de Perfil</h2>
      <ProfilePhotoCard :photo="photo" @change="emit('photo-change', $event)" />
    </div>

    <!-- Apresentação -->
    <FormField
      label="Apresentação do Profissional"
      type="textarea"
      variant="white"
      :model-value="bio"
      @update:model-value="emit('update:bio', $event)"
    />

    <!-- Especialidades ativas -->
    <div class="flex flex-col gap-4">
      <h2 class="text-base font-bold text-[#0b2f5b]">Especialidades Ativas &amp; Valores por Consulta</h2>
      <SpecialtyItem
        v-for="s in specialties"
        :key="s.id"
        :name="s.name"
        :registration="s.registration"
        :model-value="s.price"
        @update:model-value="updatePrice(s.id, $event)"
        @edit="emit('edit-specialty', s)"
        @remove="removeSpecialty(s.id)"
      />
      <p v-if="!specialties.length" class="text-sm text-gray-500">Nenhuma especialidade cadastrada.</p>
    </div>

    <!-- Nova especialidade -->
    <div class="flex flex-col gap-4">
      <h2 class="text-base font-bold text-[#0b2f5b]">Adicionar Nova Especialidade / Área de Atuação</h2>
      <AddSpecialtyForm :options="specialtyOptions" @add="addSpecialty" />
    </div>

    <!-- Salvar -->
    <div class="flex justify-end">
      <FormButton :icon="checkIcon" :disabled="saving" @click="emit('save')">Salvar Alterações</FormButton>
    </div>
  </section>
</template>