<script setup>
/**
 * AvaliacoesProfissionalLayout — conteúdo da tela "Todas as avaliações" do profissional
 *
 * Junta os componentes de components/paciente:
 *   coluna esquerda: ResumoAvaliacoes (resumo com barras) + OpcoesOrdenacao (ordenar por)
 *   coluna direita : lista de CardAvaliacao + botão "Ver mais avaliações"
 *
 * A ordenação e o "ver mais" funcionam aqui mesmo, com os dados de exemplo.
 * Quando vier da API, troque `avaliacoes` e `resumo` pelos dados reais.
 */
import { computed, ref, watch } from 'vue'
import ResumoAvaliacoes from '@/components/paciente/ResumoAvaliacoes.vue'
import OpcoesOrdenacao from '@/components/paciente/OpcoesOrdenacao.vue'
import CardAvaliacao from '@/components/paciente/CardAvaliacao.vue'

const PAGINA = 5

// TODO: trocar pelos dados vindos da API
const resumo = ref({
  nota: 4.8,
  total: 124,
  distribuicao: [
    { stars: 5, count: 102 },
    { stars: 4, count: 15 },
    { stars: 3, count: 4 },
    { stars: 2, count: 2 },
    { stars: 1, count: 1 },
  ],
})

// Datas em ISO 'YYYY-MM-DD'
const avaliacoes = ref([
  {
    id: 1,
    nome: 'Nome do Paciente',
    data: '2024-05-12',
    nota: 5,
    texto: 'Profissional excepcional. Fui para um check-up de rotina e cada detalhe dos exames foi explicado com muita paciência. Me senti seguro e bem acolhido por toda a equipe da clínica. Com certeza voltarei.',
  },
  {
    id: 2,
    nome: 'Nome do Paciente',
    data: '2024-05-05',
    nota: 5,
    texto: 'Excelente atendimento! Realizei um ecocardiograma e o profissional foi extremamente minucioso. O consultório é impecável e pontual. Recomendo para quem busca um cardiologista atencioso.',
  },
  {
    id: 3,
    nome: 'Nome do Paciente',
    data: '2024-04-28',
    nota: 4,
    texto: 'Atendimento muito bom, profissional competente. Apenas achei um pouco difícil encontrar vaga de estacionamento próxima à clínica, mas o atendimento médico compensa o transtorno.',
  },
  {
    id: 4,
    nome: 'Nome do Paciente',
    data: '2024-04-20',
    nota: 5,
    texto: 'Melhor experiência que já tive com cardiologia. Além do conhecimento técnico evidente, tem uma empatia rara hoje em dia. Explicou meu tratamento de forma que eu finalmente entendi o que precisava fazer. Nota 10!',
  },
  {
    id: 5,
    nome: 'Nome do Paciente',
    data: '2024-04-15',
    nota: 5,
    texto: 'Muito atenciosa e direta. Resolveu minhas dúvidas sobre arritmia e me passou um protocolo de atividades físicas seguro. Gostei bastante da agilidade no agendamento pelo app Marque Fácil.',
  },
  {
    id: 6,
    nome: 'Nome do Paciente',
    data: '2024-04-08',
    nota: 3,
    texto: 'A consulta foi boa, mas precisei esperar mais de meia hora além do horário marcado.',
  },
  {
    id: 7,
    nome: 'Nome do Paciente',
    data: '2024-03-30',
    nota: 5,
    texto: 'Atendimento cuidadoso do começo ao fim. Voltarei para o acompanhamento.',
  },
])

// ---- Ordenação e paginação ----
const ordem = ref('recentes') // 'recentes' | 'melhores' | 'menores'
const visiveis = ref(PAGINA)

const ordenadas = computed(() => {
  const lista = [...avaliacoes.value]
  const maisRecente = (a, b) => b.data.localeCompare(a.data)

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
  // TODO: com a API, buscar a próxima página em vez de só mostrar mais itens
  visiveis.value += PAGINA
}
</script>

<template>
  <div class="grid grid-cols-1 items-start gap-6 lg:grid-cols-[22rem_minmax(0,1fr)]">
    <div class="flex flex-col gap-6">
      <ResumoAvaliacoes
        variant="full"
        :rating="resumo.nota"
        :total="resumo.total"
        :distribution="resumo.distribuicao"
      />

      <OpcoesOrdenacao v-model="ordem" />
    </div>

    <div class="flex flex-col gap-4">
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
    </div>
  </div>
</template>
