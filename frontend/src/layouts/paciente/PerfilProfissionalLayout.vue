<script setup>
/**
 * PerfilProfissionalLayout — conteúdo da tela "Perfil do profissional" (visão do paciente)
 *
 * PROPS
 *   id  id_profissional (inteiro) ou id_usuario (UUID). Se não vier, usa route.params.id.
 *
 * EVENTOS
 *   @ver-avaliacoes  clique em "Ver todas as avaliações" (a view decide para onde ir)
 *
 * AGENDA
 *   Os dias e horários livres vêm de GET /api/v1/profissionais/busca (um item por
 *   especialidade do profissional, com horarios_disponiveis). Só os dias com horário
 *   livre ficam clicáveis. "Agendar Consulta" cria a consulta (POST /consultas/agendar,
 *   paciente logado) e leva para a confirmação e o pagamento.
 */
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useAgendamentoStore } from '@/stores/agendamento'
import CardCabecalhoProfissional from '@/components/paciente/CardCabecalhoProfissional.vue'
import CardSecao from '@/components/paciente/CardSecao.vue'
import ResumoAvaliacoes from '@/components/paciente/ResumoAvaliacoes.vue'
import CardAvaliacao from '@/components/paciente/CardAvaliacao.vue'
import PainelAgendamento from '@/components/paciente/PainelAgendamento.vue'
import { toISO } from '@/utils/datas'
import {
  buscarInfoProfissional,
  buscarAvaliacoesProfissional,
  calcularResumoAvaliacoes,
  obterUrlImagemProfissional,
  buscarProfissionais,
} from '@/services/profissionais'

const props = defineProps({
  id: { type: [String, Number], default: undefined },
})
const emit = defineEmits(['ver-avaliacoes'])

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const agendamento = useAgendamentoStore()
const identificador = computed(() => props.id ?? route.params.id)

const ICON_USER =
  'M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.5 20.118a7.5 7.5 0 0 1 15 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.5-1.632Z'
const ICON_STAR =
  'M11.48 3.499a.562.562 0 0 1 1.04 0l2.125 5.111a.563.563 0 0 0 .475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 0 0-.182.557l1.285 5.385a.562.562 0 0 1-.84.61l-4.725-2.885a.562.562 0 0 0-.586 0L6.982 20.54a.562.562 0 0 1-.84-.61l1.285-5.386a.562.562 0 0 0-.182-.557l-4.204-3.602a.563.563 0 0 1 .321-.988l5.518-.442a.563.563 0 0 0 .475-.345L11.48 3.5Z'

const moeda = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })

const carregando = ref(true)
const erro = ref('')
const erroAvaliacoes = ref(false)
const idProfissional = ref(null)

const profissional = ref({
  nome: '',
  crm: '',
  fotoUrl: '',
  verificado: true,
  nota: 0,
  totalAvaliacoes: 0,
  especialidades: [],
  sobre: '',
  valor: '',
})

// Últimas avaliações (data em ISO 'YYYY-MM-DD')
const avaliacoes = ref([])

// Só usa a foto se ela existir (o backend responde 404 quando não há)
function temImagem(url) {
  return new Promise((resolve) => {
    const img = new Image()
    img.onload = () => resolve(true)
    img.onerror = () => resolve(false)
    img.src = url
  })
}

async function carregar() {
  carregando.value = true
  erro.value = ''
  erroAvaliacoes.value = false

  try {
    if (!identificador.value) throw new Error('Profissional não informado.')

    const info = await buscarInfoProfissional(identificador.value)
    const esp = info.especialidade ?? []
    const primeira = esp[0]

    let nomeMedico = info.nome
    if (!nomeMedico) {
      // Fallback: se o backend não enviou nome, tenta pelo catálogo da busca
      try {
        const busca = await buscarProfissionais({ id_especialidade: primeira?.id_especialidade })
        const match = busca.find(
          (m) =>
            String(m.id_profissional) === String(info.id_profissional) ||
            String(m.id_usuario) === String(info.id_usuario),
        )
        if (match?.nome) nomeMedico = match.nome
      } catch {
        nomeMedico = 'Profissional de Saúde'
      }
    }

    const crmTexto = primeira
      ? `${primeira.conselho ? primeira.conselho + ' ' : ''}${primeira.numero_conselho || ''}`.trim()
      : '—'

    idProfissional.value = info.id_profissional
    profissional.value = {
      ...profissional.value,
      nome: nomeMedico || 'Profissional de Saúde',
      crm: crmTexto || '—',
      fotoUrl: '',
      especialidades: esp.map((e) => e.nome),
      sobre: info.info_profissional ?? 'Informações profissionais não cadastradas.',
      valor: primeira ? moeda.format(primeira.valor) : 'Consulte',
    }
    carregando.value = false

    // Agenda real do profissional (não trava o perfil se falhar)
    carregarAgenda(info.id_profissional)

    // Foto: valida existência sem travar a tela
    const urlFoto = obterUrlImagemProfissional(info.id_usuario || info.id_profissional)
    temImagem(urlFoto).then((ok) => {
      if (ok) profissional.value.fotoUrl = urlFoto
    })

    // Avaliações: se falhar, o perfil continua aparecendo
    try {
      const res = await buscarAvaliacoesProfissional({
        id_usuario: info.id_usuario || identificador.value,
      })
      const { nota, total } = calcularResumoAvaliacoes(res.total, res.sub_total)
      profissional.value.nota = nota
      profissional.value.totalAvaliacoes = total

      avaliacoes.value = [...(res.avaliacao ?? [])]
        .sort((a, b) => String(b.data_consulta ?? '').localeCompare(String(a.data_consulta ?? '')))
        .slice(0, 3)
        .map((a, i) => ({
          id: i + 1,
          nome: a.nome_paciente,
          data: a.data_consulta,
          nota: a.avaliacao ?? null,
          texto: a.feedback,
        }))
    } catch {
      erroAvaliacoes.value = true
      avaliacoes.value = []
    }
  } catch (e) {
    erro.value = e.message || 'Erro ao carregar os dados do profissional.'
  } finally {
    carregando.value = false
  }
}

watch(identificador, carregar, { immediate: true })

// ---- Agenda real (horários livres da busca pública) ----
const vinculos = ref([]) // um por especialidade: { id_esp_prof, especialidade, valor_consulta, horarios_disponiveis }
const idEspProf = ref(null)
const carregandoAgenda = ref(false)
const erroAgenda = ref('')
const aviso = ref('')
const precisaLogin = ref(false)
const agendando = ref(false)
const data = ref('')
const horario = ref('')

const vinculo = computed(() => vinculos.value.find((v) => v.id_esp_prof === idEspProf.value) ?? null)

// Horários livres da especialidade escolhida: { id_horario, data, inicio, fim }
const slots = computed(() =>
  (vinculo.value?.horarios_disponiveis ?? []).map((h) => ({
    id_horario: h.id_horario,
    data: h.data_consulta,
    inicio: h.hora_inicio.slice(0, 5),
    fim: h.hora_fim.slice(0, 5),
  })),
)
const diasDisponiveis = computed(() => [...new Set(slots.value.map((s) => s.data))].sort())
const horarios = computed(() =>
  slots.value
    .filter((s) => s.data === data.value)
    .map((s) => s.inicio)
    .sort(),
)
const valorAgenda = computed(() =>
  vinculo.value ? moeda.format(vinculo.value.valor_consulta) : profissional.value.valor,
)

// Abre o calendário no primeiro dia com horário livre
function irParaPrimeiroDia() {
  if (!diasDisponiveis.value.includes(data.value)) data.value = diasDisponiveis.value[0] ?? toISO(new Date())
}

async function carregarAgenda(idProf) {
  carregandoAgenda.value = true
  erroAgenda.value = ''
  try {
    const lista = await buscarProfissionais()
    vinculos.value = lista.filter((m) => String(m.id_profissional) === String(idProf))
  } catch {
    vinculos.value = []
    erroAgenda.value = 'Não foi possível carregar a agenda deste profissional.'
  } finally {
    carregandoAgenda.value = false
  }
  if (!vinculos.value.some((v) => v.id_esp_prof === idEspProf.value)) {
    idEspProf.value = vinculos.value[0]?.id_esp_prof ?? null
  }
  irParaPrimeiroDia()
}

// Trocar de especialidade ou de dia limpa o horário escolhido
watch(idEspProf, () => {
  horario.value = ''
  irParaPrimeiroDia()
})
watch(data, () => {
  horario.value = ''
})

const avisoPainel = computed(() => {
  if (aviso.value) return aviso.value
  if (erroAgenda.value) return erroAgenda.value
  if (!carregandoAgenda.value && !diasDisponiveis.value.length) return 'Este profissional não tem horários livres no momento.'
  return ''
})

async function agendar() {
  const slot = slots.value.find((s) => s.data === data.value && s.inicio === horario.value)
  if (!slot || agendando.value) return
  aviso.value = ''
  precisaLogin.value = false

  if (!auth.logado) {
    precisaLogin.value = true
    aviso.value = 'Entre com sua conta de paciente para agendar.'
    return
  }
  if (auth.perfil !== 'paciente') {
    aviso.value = 'Somente pacientes podem agendar consultas.'
    return
  }

  agendando.value = true
  try {
    const consulta = await agendamento.agendar({ id_horario: slot.id_horario, inicio: slot.inicio, fim: slot.fim })
    router.push({ name: 'confirmacaoAgendamento', params: { idConsulta: consulta.id_consulta } })
  } catch (e) {
    aviso.value = e.message || 'Não foi possível agendar a consulta.'
    // Horário reservado por outra pessoa nesse meio-tempo: atualiza a agenda
    if (e.status === 409) await carregarAgenda(idProfissional.value)
  } finally {
    agendando.value = false
  }
}
</script>

<template>
  <p v-if="carregando" class="p-8 text-center text-gray-500">Carregando dados do profissional...</p>

  <p v-else-if="erro" class="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">
    {{ erro }}
  </p>

  <div v-else class="grid grid-cols-1 items-start gap-6 lg:grid-cols-[minmax(0,1fr)_24rem]">
    <div class="flex flex-col gap-6">
      <CardCabecalhoProfissional
        :name="profissional.nome"
        :crm="profissional.crm"
        :photo="profissional.fotoUrl"
        :verified="profissional.verificado"
        :rating="profissional.nota"
        :review-count="profissional.totalAvaliacoes"
        :specialties="profissional.especialidades"
        @ver-avaliacoes="emit('ver-avaliacoes', idProfissional)"
      />

      <CardSecao title="Sobre o Médico" :icon="ICON_USER">
        <p class="leading-relaxed text-gray-700 whitespace-pre-line">{{ profissional.sobre }}</p>
      </CardSecao>

      <CardSecao title="Avaliações e Comentários" :icon="ICON_STAR">
        <template #aside>
          <ResumoAvaliacoes
            variant="badge"
            :rating="profissional.nota"
            :total="profissional.totalAvaliacoes"
            @ver-avaliacoes="emit('ver-avaliacoes', idProfissional)"
          />
        </template>

        <p v-if="erroAvaliacoes" class="text-sm text-red-700">
          Não foi possível carregar as avaliações.
        </p>
        <p v-else-if="avaliacoes.length === 0" class="text-sm text-gray-500">
          Este profissional ainda não possui avaliações.
        </p>

        <div v-else class="flex flex-col gap-5">
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
          v-if="profissional.totalAvaliacoes > 0"
          type="button"
          class="mt-6 w-full cursor-pointer rounded-lg border border-[#0b2f5b] py-3 text-sm font-semibold text-[#0b2f5b] transition-colors hover:bg-[#f3f6fb]"
          @click="emit('ver-avaliacoes', idProfissional)"
        >
          Ver todas as avaliações ({{ profissional.totalAvaliacoes }})
        </button>
      </CardSecao>
    </div>

    <PainelAgendamento
      v-model:date="data"
      v-model:time="horario"
      :horarios="horarios"
      :disponiveis="diasDisponiveis"
      :price="valorAgenda"
      :agendando="agendando"
      :aviso="avisoPainel"
      @agendar="agendar"
    >
      <template v-if="vinculos.length > 1" #antes>
        <label class="flex flex-col gap-2 text-sm font-bold text-[#0b2f5b]">
          Especialidade
          <select
            v-model="idEspProf"
            class="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm font-normal text-[#0b2f5b]"
          >
            <option v-for="v in vinculos" :key="v.id_esp_prof" :value="v.id_esp_prof">
              {{ v.especialidade }} · {{ moeda.format(v.valor_consulta) }}
            </option>
          </select>
        </label>
      </template>
      <template v-if="precisaLogin" #aviso>
        <RouterLink
          :to="{ name: 'login/paciente', query: { redirect: route.fullPath } }"
          class="font-semibold underline"
        >Entrar</RouterLink>
      </template>
    </PainelAgendamento>
  </div>
</template>
