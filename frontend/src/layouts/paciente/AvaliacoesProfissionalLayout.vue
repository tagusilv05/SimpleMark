<script setup>
/**
 * AvaliacoesProfissionalLayout — conteúdo da tela "Todas as avaliações" do profissional
 *
 * PROPS
 *   id  id_profissional (inteiro) ou id_usuario (UUID). Se não vier, usa route.params.id.
 *
 * Junta os componentes de components/paciente:
 *   coluna esquerda: ResumoAvaliacoes (resumo com barras) + OpcoesOrdenacao (ordenar por)
 *   coluna direita : lista de CardAvaliacao + botão "Ver mais avaliações"
 *
 * O backend devolve todas as avaliações de uma vez; ordenação e "ver mais" são feitos aqui.
 */
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import ResumoAvaliacoes from '@/components/paciente/ResumoAvaliacoes.vue'
import OpcoesOrdenacao from '@/components/paciente/OpcoesOrdenacao.vue'
import CardAvaliacao from '@/components/paciente/CardAvaliacao.vue'
import {
  buscarInfoProfissional,
  buscarAvaliacoesProfissional,
  calcularResumoAvaliacoes,
} from '@/services/profissionais'

const PAGINA = 5

const props = defineProps({
  id: { type: [String, Number], default: undefined },
})

const route = useRoute()
const identificador = computed(() => props.id ?? route.params.id)

const carregando = ref(true)
const erro = ref('')

const nomeProfissional = ref('')
const idUsuario = ref(null)
const especialidades = ref([]) // [{ id_especialidade, nome, ... }]
const especialidadeSelecionada = ref('') // '' = todas

const resumo = ref({ nota: 0, total: 0, distribuicao: [] })

// Datas em ISO 'YYYY-MM-DD'
const avaliacoes = ref([])

// ---- Carregamento ----
async function carregarAvaliacoes() {
  const res = await buscarAvaliacoesProfissional({
    id_usuario: idUsuario.value,
    id_especialidade: especialidadeSelecionada.value || undefined,
  })

  resumo.value = calcularResumoAvaliacoes(res.total, res.sub_total)
  avaliacoes.value = (res.avaliacao ?? []).map((a, i) => ({
    id: i + 1,
    nome: a.nome_paciente,
    data: a.data_consulta,
    nota: a.avaliacao,
    texto: a.feedback,
  }))
  visiveis.value = PAGINA
}

async function carregar() {
  carregando.value = true
  erro.value = ''
  try {
    if (!identificador.value) throw new Error('Profissional não informado.')

    const info = await buscarInfoProfissional(identificador.value)
    nomeProfissional.value = info.nome || ''
    idUsuario.value = info.id_usuario || identificador.value
    especialidades.value = info.especialidade ?? []
    especialidadeSelecionada.value = ''

    await carregarAvaliacoes()
  } catch (e) {
    erro.value = e.message || 'Erro ao carregar as avaliações.'
  } finally {
    carregando.value = false
  }
}

watch(identificador, carregar, { immediate: true })

// Trocar a especialidade refaz só a busca de avaliações
watch(especialidadeSelecionada, async () => {
  if (!idUsuario.value) return
  erro.value = ''
  try {
    await carregarAvaliacoes()
  } catch (e) {
    erro.value = e.message
  }
})

// ---- Ordenação e paginação ----
const ordem = ref('recentes') // 'recentes' | 'melhores' | 'menores'
const visiveis = ref(PAGINA)

const ordenadas = computed(() => {
  const lista = [...avaliacoes.value]
  const maisRecente = (a, b) => String(b.data ?? '').localeCompare(String(a.data ?? ''))

  if (ordem.value === 'melhores') lista.sort((a, b) => b.nota - a.nota || maisRecente(a, b))
  else if (ordem.value === 'menores') lista.sort((a, b) => a.nota - b.nota || maisRecente(a, b))
  else lista.sort(maisRecente)

  return lista
})

const lista = computed(() => ordenadas.value.slice(0, visiveis.value))
const temMais = computed(() => visiveis.value < ordenadas.value.length)

// Mudar a ordem volta para a primeira página
watch(ordem, () => {
  visiveis.value = PAGINA
})

function verMais() {
  visiveis.value += PAGINA
}
</script>

<template>
  <p v-if="carregando" class="p-8 text-center text-gray-500">Carregando avaliações...</p>

  <div v-else class="flex flex-col gap-4">
    <p v-if="erro" class="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{{ erro }}</p>

    <div v-if="nomeProfissional" class="mb-2">
      <h1 class="text-2xl font-bold text-[#0b2f5b]">Avaliações de {{ nomeProfissional }}</h1>
    </div>

    <div class="grid grid-cols-1 items-start gap-6 lg:grid-cols-[22rem_minmax(0,1fr)]">
      <div class="flex flex-col gap-6">
        <ResumoAvaliacoes
          variant="full"
          :rating="resumo.nota"
          :total="resumo.total"
          :distribution="resumo.distribuicao"
        />

        <!-- Só aparece quando o profissional tem mais de uma especialidade -->
        <label v-if="especialidades.length > 1" class="flex flex-col gap-2 text-sm text-gray-700">
          Especialidade
          <select
            v-model="especialidadeSelecionada"
            class="rounded-lg border border-gray-300 bg-white px-3 py-2"
          >
            <option value="">Todas</option>
            <option v-for="e in especialidades" :key="e.id_especialidade" :value="e.id_especialidade">
              {{ e.nome }}
            </option>
          </select>
        </label>

        <OpcoesOrdenacao v-model="ordem" />
      </div>

      <div class="flex flex-col gap-4">
        <div v-if="avaliacoes.length === 0" class="rounded-xl bg-white p-8 text-center text-gray-500 shadow-sm">
          Este profissional ainda não possui avaliações.
        </div>

        <template v-else>
          <CardAvaliacao
            v-for="a in lista"
            :key="a.id"
            variant="card"
            :name="a.nome"
            :date="a.data"
            :rating="a.nota"
            :text="a.texto"
          />

          <div v-if="temMais" class="mt-2 flex justify-center">
            <button
              type="button"
              class="inline-flex cursor-pointer items-center gap-2 rounded-lg bg-[#042d5c] px-8 py-3 font-semibold text-white transition-colors hover:bg-[#0b3f7a]"
              @click="verMais"
            >
              Ver mais avaliações
              <svg
                class="size-4"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke-width="3"
                stroke="currentColor"
                aria-hidden="true"
              >
                <path stroke-linecap="round" stroke-linejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" />
              </svg>
            </button>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>
