<script setup>
/**
 * PerfilProfissionalLayout — conteúdo da tela "Perfil do profissional" (visão do paciente)
 *
 * Junta os componentes de components/paciente:
 *   coluna esquerda: CardCabecalhoProfissional, "Sobre o Médico", "Avaliações e Comentários"
 *   coluna direita : PainelAgendamento (calendário, horários, valor e botão de agendar)
 *
 * EVENTOS
 *   @ver-avaliacoes  clique em "Ver todas as avaliações" (a view decide para onde ir)
 *   @agendar         clique em "Agendar Consulta", com { data, horario }
 */
import { computed, ref, watch } from 'vue'
import CardCabecalhoProfissional from '@/components/paciente/CardCabecalhoProfissional.vue'
import CardSecao from '@/components/paciente/CardSecao.vue'
import ResumoAvaliacoes from '@/components/paciente/ResumoAvaliacoes.vue'
import CardAvaliacao from '@/components/paciente/CardAvaliacao.vue'
import PainelAgendamento from '@/components/paciente/PainelAgendamento.vue'
import { toISO, fromISO } from '@/utils/datas'

const emit = defineEmits(['ver-avaliacoes', 'agendar'])

const ICON_USER =
  'M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.5 20.118a7.5 7.5 0 0 1 15 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.5-1.632Z'
const ICON_STAR =
  'M11.48 3.499a.562.562 0 0 1 1.04 0l2.125 5.111a.563.563 0 0 0 .475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 0 0-.182.557l1.285 5.385a.562.562 0 0 1-.84.61l-4.725-2.885a.562.562 0 0 0-.586 0L6.982 20.54a.562.562 0 0 1-.84-.61l1.285-5.386a.562.562 0 0 0-.182-.557l-4.204-3.602a.562.562 0 0 1 .321-.988l5.518-.442a.563.563 0 0 0 .475-.345L11.48 3.5Z'

// TODO: trocar pelos dados vindos da API
const profissional = ref({
  nome: 'Dr. Nome Profissional',
  crm: 'CRM 123456/SP',
  fotoUrl: '',
  verificado: true,
  nota: 4.8,
  totalAvaliacoes: 124,
  especialidades: ['Cardiologia Clínica'],
  sobre:
    'Especialista em diagnósticos complexos e prevenção de doenças coronárias, combina tecnologia de ponta com um atendimento humanizado e focado no bem-estar integral do paciente. Sua abordagem clínica prioriza a escuta ativa e a educação continuada sobre hábitos de vida saudáveis.',
  valor: 'R$ 250,00',
})

// Últimas avaliações (data em ISO 'YYYY-MM-DD')
const avaliacoes = ref([
  {
    id: 1,
    nome: 'Nome do Paciente',
    data: '2024-05-15',
    nota: 5,
    texto: 'Excelente profissional, muito atenciosa e explicou tudo com detalhes. Senti muita segurança no diagnóstico e no plano de tratamento proposto.',
  },
  {
    id: 2,
    nome: 'Nome do Paciente',
    data: '2024-05-02',
    nota: 4,
    texto: 'O atendimento foi pontual e o profissional é extremamente humano. O consultório é muito bem equipado e a equipe da recepção também é nota dez.',
  },
  {
    id: 3,
    nome: 'Nome do Paciente',
    data: '2024-04-28',
    nota: 5,
    texto: 'Fiz meu check-up anual e recomendo a todos. Muito criterioso nos exames e passa muita tranquilidade durante a consulta.',
  },
])

// ---- Agendamento ----
const data = ref(toISO(new Date()))
const horario = ref('')

// Trocar de dia limpa o horário escolhido
watch(data, () => {
  horario.value = ''
})

// TODO: buscar na API os horários livres do dia. Por enquanto, domingo sem horários.
const horarios = computed(() =>
  fromISO(data.value).getDay() === 0 ? [] : ['09:00', '10:30', '11:15', '14:00', '15:45'],
)

function agendar() {
  emit('agendar', { data: data.value, horario: horario.value })
}
</script>

<template>
  <div class="grid grid-cols-1 items-start gap-6 lg:grid-cols-[minmax(0,1fr)_24rem]">
    <div class="flex flex-col gap-6">
      <CardCabecalhoProfissional
        :name="profissional.nome"
        :crm="profissional.crm"
        :photo="profissional.fotoUrl"
        :verified="profissional.verificado"
        :rating="profissional.nota"
        :review-count="profissional.totalAvaliacoes"
        :specialties="profissional.especialidades"
        @ver-avaliacoes="emit('ver-avaliacoes')"
      />

      <CardSecao title="Sobre o Médico" :icon="ICON_USER">
        <p class="leading-relaxed text-gray-700">{{ profissional.sobre }}</p>
      </CardSecao>

      <CardSecao title="Avaliações e Comentários" :icon="ICON_STAR">
        <template #aside>
          <ResumoAvaliacoes
            variant="badge"
            :rating="profissional.nota"
            :total="profissional.totalAvaliacoes"
            @ver-avaliacoes="emit('ver-avaliacoes')"
          />
        </template>

        <div class="flex flex-col gap-5">
          <CardAvaliacao
            v-for="a in avaliacoes"
            :key="a.id"
            variant="compact"
            :name="a.nome"
            :date="a.data"
            :rating="a.nota"
            :text="a.texto"
          />
        </div>

        <button
          type="button"
          class="mt-6 w-full cursor-pointer rounded-lg border border-[#0b2f5b] py-3 text-sm font-semibold text-[#0b2f5b] transition-colors hover:bg-[#f3f6fb]"
          @click="emit('ver-avaliacoes')"
        >
          Ver todas as avaliações
        </button>
      </CardSecao>
    </div>

    <PainelAgendamento
      v-model:date="data"
      v-model:time="horario"
      :horarios="horarios"
      :price="profissional.valor"
      @agendar="agendar"
    />
  </div>
</template>
