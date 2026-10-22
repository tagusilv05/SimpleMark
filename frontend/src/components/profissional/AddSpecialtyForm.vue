<script setup>
/**
 * AddSpecialtyForm — formulário "Adicionar Nova Especialidade / Área de Atuação"
 *
 * COMO USAR (na página):
 *
 *   import AddSpecialtyForm from '@/components/professional/AddSpecialtyForm.vue'
 *
 *   <AddSpecialtyForm
 *     :options="['Cardiologia', 'Dermatologia', 'Pediatria']"
 *     @add="adicionar"
 *   />
 *
 *   function adicionar({ specialty, registration, price }) { ... }
 *
 * PROPS
 *   options  Array  (padrão: [])
 *              especialidades do select. Aceita ['Cardiologia', ...] ou
 *              [{ value, label }]. A primeira opção "Selecione..." é adicionada
 *              automaticamente.
 *
 * EVENTOS
 *   add   emitido ao clicar em "Adicionar Especialidade", com
 *         { specialty, registration, price } (todos String). Só dispara se os
 *         três campos estiverem preenchidos; depois o formulário é limpo.
 *
 * ESTILO
 *   Tailwind. Fundo azul bem claro; campos em grade que quebra no celular.
 *
 * DEPENDÊNCIAS
 *   - FormField e FormButton (shared)
 *   - Tailwind CSS
 */
import { computed, reactive } from 'vue'
import FormField from '@/components/shared/FormField.vue'
import FormButton from '@/components/shared/FormButton.vue'

const props = defineProps({
  options: { type: Array, default: () => [] },
})

const emit = defineEmits(['add'])

const form = reactive({ specialty: '', registration: '', price: '' })

const selectOptions = computed(() => [
  { value: '', label: 'Selecione uma especialidade...' },
  ...props.options.map((o) => (typeof o === 'object' ? o : { value: o, label: o })),
])

const canAdd = computed(
  () => form.specialty && form.registration.trim() && form.price.trim(),
)

function submit() {
  if (!canAdd.value) return
  emit('add', { ...form })
  form.specialty = ''
  form.registration = ''
  form.price = ''
}

const plusIcon = 'M12 4.5v15m7.5-7.5h-15'
</script>

<template>
  <div class="flex flex-col gap-5 rounded-2xl bg-[#f7f8ff] p-6">
    <FormField
      v-model="form.specialty"
      label="Especialidade / Área de Atuação"
      type="select"
      :options="selectOptions"
    />

    <div class="grid items-end gap-5 sm:grid-cols-[1fr_1fr_auto]">
      <FormField
        v-model="form.registration"
        label="Nº de Registro no Conselho e UF"
        placeholder="Ex.: CRM-PI 1234"
      />
      <FormField v-model="form.price" label="Valor" placeholder="R$ 0,00" />
      <FormButton variant="soft" :icon="plusIcon" :disabled="!canAdd" @click="submit">
        Adicionar Especialidade
      </FormButton>
    </div>
  </div>
</template>
