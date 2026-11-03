<script setup>
/**
 * PerfilProfissionalLayout — conteúdo da tela "Perfil do profissional" (visão do paciente)
 *
 * PROPS
 *   id  id_profissional (inteiro) ou id_usuario (UUID). Se não vier, usa route.params.id.
 *
 * EVENTOS
 *   @ver-avaliacoes  clique em "Ver todas as avaliações" (a view decide para onde ir)
 *   @agendar         clique em "Agendar Consulta", com { data, horario, idProfissional }
 */
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import CardCabecalhoProfissional from '@/components/paciente/CardCabecalhoProfissional.vue'
import CardSecao from '@/components/paciente/CardSecao.vue'
import ResumoAvaliacoes from '@/components/paciente/ResumoAvaliacoes.vue'
import CardAvaliacao from '@/components/paciente/CardAvaliacao.vue'
import PainelAgendamento from '@/components/paciente/PainelAgendamento.vue'
import { toISO, fromISO } from '@/utils/datas'
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
const emit = defineEmits(['ver-avaliacoes', 'agendar'])

const route = useRoute()
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
          nota: a.avaliacao,
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
  emit('agendar', { data: data.value, horario: horario.value, idProfissional: idProfissional.value })
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
      :price="profissional.valor"
      @agendar="agendar"
    />
  </div>
</template>
