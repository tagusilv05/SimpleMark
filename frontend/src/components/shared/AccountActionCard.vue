<script setup>
import { ref } from 'vue'
import RoleBadge from './RoleBadge.vue'
import FormButton from './FormButton.vue'

/**
 * AccountActionCard — uma caixa de ação com confirmação ("Estou Ciente").
 * O botão só é liberado depois de marcar a caixa de confirmação.
 *
 * COMO USAR:
 *   <AccountActionCard
 *     title="Exclusão Definitiva da Conta"
 *     description="Ao confirmar a exclusão..."
 *     :icon="iconeLixeira"
 *     badge="Ação Irreversível"
 *     button-label="Excluir Conta"
 *     tone="danger"
 *     @confirm="excluir"
 *   />
 *
 * PROPS
 *   title        String   título da caixa (obrigatório)
 *   description  String   texto explicativo
 *   icon         String   ícone do título: caminho "d" de SVG 24x24 de contorno
 *   badge        String   texto da etiqueta à direita (ex.: "Ação Reversível")
 *   badgeIcon    String   ícone da etiqueta (SVG 24x24 PREENCHIDO). Sem valor = verificado
 *   buttonLabel  String   texto do botão
 *   buttonIcon   String   ícone do botão: caminho "d" de SVG 24x24 de contorno
 *   checkLabel   String   texto da confirmação (padrão: "Estou Ciente")
 *   tone         'default' | 'danger'   muda as cores do ícone, da etiqueta e do botão
 *
 * EVENTOS
 *   @confirm   clicou no botão (só é possível com "Estou Ciente" marcado)
 */

defineProps({
  title: { type: String, required: true },
  description: { type: String, default: '' },
  icon: { type: String, default: '' },
  badge: { type: String, default: '' },
  badgeIcon: { type: String, default: undefined },
  buttonLabel: { type: String, required: true },
  buttonIcon: { type: String, default: '' },
  checkLabel: { type: String, default: 'Estou Ciente' },
  tone: { type: String, default: 'default', validator: (v) => ['default', 'danger'].includes(v) },
})

const emit = defineEmits(['confirm'])

const ciente = ref(false)

// Classes completas (o Tailwind precisa enxergar o texto inteiro)
const iconBox = {
  default: 'bg-[#dce6fb] text-[#0b2f5b]',
  danger: 'bg-red-100 text-red-700',
}
const badgeTone = { default: 'teal', danger: 'danger' }
const buttonVariant = { default: 'soft', danger: 'danger' }

function confirmar() {
  emit('confirm')
  ciente.value = false // exige marcar de novo para repetir a ação
}
</script>

<template>
  <section class="flex flex-col gap-4 rounded-xl border border-[#d5dbf0] bg-[#eef1fe] p-6">
    <header class="flex items-center justify-between gap-4">
      <div class="flex items-center gap-4">
        <span
          v-if="icon"
          class="flex size-10 shrink-0 items-center justify-center rounded-lg"
          :class="iconBox[tone]"
        >
          <svg
            class="size-5"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke-width="1.5"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path stroke-linecap="round" stroke-linejoin="round" :d="icon" />
          </svg>
        </span>

        <h3 class="text-xl font-medium text-[#0b2f5b]">{{ title }}</h3>
      </div>

      <RoleBadge v-if="badge" :label="badge" :icon="badgeIcon" :tone="badgeTone[tone]" />
    </header>

    <p v-if="description" class="text-sm font-semibold leading-relaxed text-gray-600">
      {{ description }}
    </p>

    <footer class="flex items-center justify-between gap-4 border-t border-[#d5dbf0] pt-4">
      <label class="inline-flex cursor-pointer items-center gap-2.5 text-sm font-bold text-gray-800">
        <input v-model="ciente" type="checkbox" class="size-4 cursor-pointer accent-[#042d5c]" />
        {{ checkLabel }}
      </label>

      <FormButton :variant="buttonVariant[tone]" :icon="buttonIcon" :disabled="!ciente" @click="confirmar">
        {{ buttonLabel }}
      </FormButton>
    </footer>
  </section>
</template>
