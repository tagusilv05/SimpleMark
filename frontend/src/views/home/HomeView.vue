<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import AppHeader from '@/components/shared/AppHeader.vue'
import AppFooter from '@/components/shared/AppFooter.vue'
import SpecialtySearch from '@/components/shared/SpecialtySearch.vue'
import SectionTitle from '@/components/shared/SectionTitle.vue'
import FeatureItem from '@/components/shared/FeatureItem.vue'
import SpecialtyChip from '@/components/shared/SpecialtyChip.vue'
import DoctorCard from '@/components/shared/DoctorCard.vue'
import { listarEspecialidades, maisAvaliados } from '@/services/profissionais'
import heroImage from '@/assets/hero-medica.jpg'

const router = useRouter()

// ---- Dados vindos do backend ----
const especialidades = ref([])
const carregandoEspecialidades = ref(true)
const erroEspecialidades = ref('')

const medicos = ref([])
const totalProfissionais = ref(0)
const carregandoMedicos = ref(true)
const erroMedicos = ref('')

// A tela mostra no máximo 12 especialidades (2 linhas de 6) e 4 médicos
const MAX_ESPECIALIDADES = 12
const MAX_MEDICOS = 4

const especialidadesEmDestaque = computed(() => especialidades.value.slice(0, MAX_ESPECIALIDADES))

// Só afirma um número quando o backend o confirma
const subtitulo = computed(() =>
  totalProfissionais.value > 0
    ? `${totalProfissionais.value} ${totalProfissionais.value === 1 ? 'especialista de saúde está pronto' : 'especialistas de saúde estão prontos'} para te ajudar`
    : 'Especialistas de saúde prontos para te ajudar',
)

async function carregarEspecialidades() {
  carregandoEspecialidades.value = true
  erroEspecialidades.value = ''
  try {
    especialidades.value = await listarEspecialidades()
  } catch (erro) {
    erroEspecialidades.value = erro.message
  } finally {
    carregandoEspecialidades.value = false
  }
}

async function carregarMedicos() {
  carregandoMedicos.value = true
  erroMedicos.value = ''
  try {
    const { destaques, total } = await maisAvaliados(MAX_MEDICOS)
    medicos.value = destaques
    totalProfissionais.value = total
  } catch (erro) {
    erroMedicos.value = erro.message
  } finally {
    carregandoMedicos.value = false
  }
}

onMounted(() => {
  carregarEspecialidades()
  carregarMedicos()
})

// ---- Navegação ----
// A tela /busca lê id_especialidade da query string (mesmo nome do filtro da API)
function buscarPorEspecialidade(idEspecialidade) {
  router.push({
    name: 'busca-profissionais',
    query: idEspecialidade ? { id_especialidade: idEspecialidade } : {},
  })
}

function verPerfil(medico) {
  router.push({ name: 'perfil-profissional', params: { id: medico.id_profissional } })
}

const icones = {
  agenda:
    'M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 0 1 2.25-2.25h13.5A2.25 2.25 0 0 1 21 7.5v11.25m-18 0A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75m-18 0v-7.5A2.25 2.25 0 0 1 5.25 9h13.5A2.25 2.25 0 0 1 21 11.25v7.5m-9-6h.008v.008H12v-.008ZM12 15h.008v.008H12V15Zm0 2.25h.008v.008H12v-.008ZM9.75 15h.008v.008H9.75V15Zm0 2.25h.008v.008H9.75v-.008ZM7.5 15h.008v.008H7.5V15Zm0 2.25h.008v.008H7.5v-.008Zm6.75-4.5h.008v.008h-.008v-.008Zm0 2.25h.008v.008h-.008V15Zm0 2.25h.008v.008h-.008v-.008Zm2.25-4.5h.008v.008H16.5v-.008Zm0 2.25h.008v.008H16.5V15Z',
  escudo:
    'M9 12.75 11.25 15 15 9.75m-3-7.036A11.959 11.959 0 0 1 3.598 6 11.99 11.99 0 0 0 3 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285Z',
  qualificado:
    'M9 12.75 11.25 15 15 9.75M21 12c0 1.268-.63 2.39-1.593 3.068a3.745 3.745 0 0 1-1.043 3.296 3.745 3.745 0 0 1-3.296 1.043A3.745 3.745 0 0 1 12 21c-1.268 0-2.39-.63-3.068-1.593a3.746 3.746 0 0 1-3.296-1.043 3.745 3.745 0 0 1-1.043-3.296A3.745 3.745 0 0 1 3 12c0-1.268.63-2.39 1.593-3.068a3.745 3.745 0 0 1 1.043-3.296 3.746 3.746 0 0 1 3.296-1.043A3.746 3.746 0 0 1 12 3c1.268 0 2.39.63 3.068 1.593a3.746 3.746 0 0 1 3.296 1.043 3.746 3.746 0 0 1 1.043 3.296A3.745 3.745 0 0 1 21 12Z',
}

const destaques = [
  {
    title: 'Agendamento Rápido',
    text: 'Marque sua consulta em poucos cliques, sem filas ou espera telefônica.',
    icon: icones.agenda,
  },
  {
    title: 'Telemedicina Segura',
    text: 'Consultas por vídeo com total privacidade e segurança dos seus dados.',
    icon: icones.escudo,
  },
  {
    title: 'Profissionais Qualificados',
    text: 'Acesso aos melhores especialistas avaliados pela nossa comunidade.',
    icon: icones.qualificado,
  },
]
</script>

<template>
  <div class="flex min-h-screen flex-col bg-[#f8faff]">
    <AppHeader />

    <main class="flex-1">
      <!-- Hero: título + busca, foto à direita com degradê para o fundo -->
      <section class="relative isolate overflow-hidden">
        <img
          :src="heroImage"
          alt=""
          class="absolute inset-y-0 right-0 -z-10 hidden h-full w-3/5 object-cover object-top md:block"
        />
        <div
          class="absolute inset-0 -z-10 hidden bg-linear-to-r from-[#f8faff] from-40% via-[#f8faff]/70 via-55% to-transparent to-75% md:block"
          aria-hidden="true"
        />

        <div class="mx-auto flex min-h-[26rem] max-w-300 flex-col justify-center gap-5 px-12 py-16 md:min-h-[32rem]">
          <div class="flex flex-col gap-2">
            <h1 class="text-4xl font-bold text-[#0b2f5b]">Agende agora sua consulta</h1>
            <p class="text-sm text-[#0b2f5b]">{{ subtitulo }}</p>
          </div>

          <SpecialtySearch
            :options="especialidades"
            :loading="carregandoEspecialidades"
            @search="buscarPorEspecialidade"
          />
        </div>
      </section>

      <!-- Diferenciais -->
      <section class="mx-auto grid max-w-300 grid-cols-1 gap-10 px-12 py-20 md:grid-cols-3">
        <FeatureItem v-for="item in destaques" :key="item.title" v-bind="item" />
      </section>

      <!-- Especialidades -->
      <section class="mx-auto flex max-w-300 flex-col gap-8 px-12 pb-20">
        <SectionTitle
          title="Especialidades Mais Procuradas Na Simple Mark"
          subtitle="Encontre os melhores especialistas em diversas áreas da saúde"
        />

        <div
          v-if="carregandoEspecialidades"
          class="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6"
          aria-busy="true"
        >
          <div v-for="n in MAX_ESPECIALIDADES" :key="n" class="h-11 animate-pulse rounded-lg bg-gray-200" />
        </div>

        <div v-else-if="erroEspecialidades" class="flex flex-col items-start gap-3" role="alert">
          <p class="text-sm text-red-700">{{ erroEspecialidades }}</p>
          <button
            type="button"
            class="cursor-pointer text-sm font-semibold text-[#0b2f5b] underline underline-offset-4"
            @click="carregarEspecialidades"
          >
            Tentar novamente
          </button>
        </div>

        <p v-else-if="!especialidadesEmDestaque.length" class="text-sm text-gray-500">
          Nenhuma especialidade cadastrada ainda.
        </p>

        <div v-else class="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
          <SpecialtyChip
            v-for="e in especialidadesEmDestaque"
            :key="e.id_especialidade"
            :label="e.especialidade"
            @click="buscarPorEspecialidade(e.id_especialidade)"
          />
        </div>
      </section>

      <!-- Médicos mais avaliados -->
      <section class="bg-[#eff2fd] py-14">
        <div class="mx-auto flex max-w-300 flex-col gap-8 px-12">
          <SectionTitle
            title="Médicos Mais Avaliados"
            subtitle="Profissionais reconhecidos pela excelência no atendimento"
          />

          <div
            v-if="carregandoMedicos"
            class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4"
            aria-busy="true"
          >
            <div v-for="n in MAX_MEDICOS" :key="n" class="h-56 animate-pulse rounded-xl bg-gray-200" />
          </div>

          <div v-else-if="erroMedicos" class="flex flex-col items-start gap-3" role="alert">
            <p class="text-sm text-red-700">{{ erroMedicos }}</p>
            <button
              type="button"
              class="cursor-pointer text-sm font-semibold text-[#0b2f5b] underline underline-offset-4"
              @click="carregarMedicos"
            >
              Tentar novamente
            </button>
          </div>

          <p v-else-if="!medicos.length" class="text-sm text-gray-500">
            Ainda não há profissionais com horários disponíveis.
          </p>

          <div v-else class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
            <DoctorCard
              v-for="m in medicos"
              :key="m.id_profissional"
              :name="m.nome"
              :specialty="m.especialidade"
              :rating="m.avaliacao"
              @view="verPerfil(m)"
            />
          </div>
        </div>
      </section>
    </main>

    <AppFooter />
  </div>
</template>
