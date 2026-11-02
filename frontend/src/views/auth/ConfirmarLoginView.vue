<script setup>
/**
 * ConfirmarLoginView — etapa 2 do login: código de 6 dígitos enviado por e-mail
 *
 * Fluxo: tela de login (paciente | profissional | administrador) -> senha aceita
 *        -> esta tela (rota `login/confirmar`) -> painel do perfil.
 *
 * O desafio (id, e-mail mascarado, validade) vem da store `auth`. Se a página for
 * recarregada o desafio se perde: o guard do router devolve para `/login`.
 */

import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import FormField from '@/components/shared/FormField.vue'
import FormButton from '@/components/shared/FormButton.vue'
import { useAuthStore } from '@/stores/auth'
import imagemPaciente from '@/assets/imagempaciente.jpg'
import imagemProfissional from '@/assets/imagemprofissional.png'
import imagemAdmin from '@/assets/imagemadministrador.png'

const router = useRouter()
const auth = useAuthStore()

const TAMANHO_CODIGO = 6

const codigo = ref('')
const carregando = ref(false)
const erro = ref('')

// Cada perfil mantém a sua imagem e a sua tela de login
const porPerfil = {
  paciente: { imagem: imagemPaciente, login: 'login/paciente' },
  profissional: { imagem: imagemProfissional, login: 'login/profissional' },
  administrador: { imagem: imagemAdmin, login: 'login/administrador' },
}
const perfilEsperado = auth.desafio?.perfilEsperado ?? 'paciente'
const contexto = porPerfil[perfilEsperado]
const emailMascarado = auth.desafio?.emailMascarado ?? ''

// Só números, no máximo 6
watch(codigo, (valor) => {
  const limpo = valor.replace(/\D/g, '').slice(0, TAMANHO_CODIGO)
  if (limpo !== valor) codigo.value = limpo
})

// ---- Contagem regressiva da validade do código ----
const restante = ref(0)
let intervalo = null

function atualizarRestante() {
  if (!auth.desafio) return
  const { expiraEmSegundos, criadoEm } = auth.desafio
  const passou = Math.floor((Date.now() - criadoEm) / 1000)
  restante.value = Math.max(0, expiraEmSegundos - passou)
}

onMounted(() => {
  atualizarRestante()
  intervalo = setInterval(atualizarRestante, 1000)
})
onBeforeUnmount(() => clearInterval(intervalo))

const tempoFormatado = computed(() => {
  const m = String(Math.floor(restante.value / 60)).padStart(2, '0')
  const s = String(restante.value % 60).padStart(2, '0')
  return `${m}:${s}`
})
const expirou = computed(() => restante.value === 0)

async function confirmar() {
  if (carregando.value) return
  erro.value = ''

  if (codigo.value.length !== TAMANHO_CODIGO) {
    erro.value = `O código de confirmação deve ter ${TAMANHO_CODIGO} números.`
    return
  }

  carregando.value = true
  try {
    await auth.confirmarLogin(codigo.value)
    router.push(auth.rotaInicial)
  } catch (e) {
    erro.value = e.message || 'Não foi possível confirmar o código. Tente novamente.'
  } finally {
    carregando.value = false
  }
}

function voltar() {
  auth.cancelarDesafio()
  router.push({ name: contexto.login })
}
</script>

<template>
  <main class="grid min-h-screen bg-[#fafaff] lg:grid-cols-[minmax(0,41fr)_minmax(0,59fr)]">
    <!-- Coluna do formulário -->
    <section class="flex flex-col px-6 pt-6 sm:px-10 lg:pt-8">
      <img
        src="/LOGO%20OFICIAL%20SEM%20FUNDO.png"
        alt="Simple Mark"
        class="h-36 w-auto self-start"
      />

      <div class="my-auto w-full max-w-111.75 py-8 lg:ml-16">
        <div class="rounded-2xl border border-gray-200 bg-white p-6 sm:p-10">
          <header class="mb-8">
            <h1 class="text-2xl font-medium text-[#00507a]">Confirme seu acesso</h1>
            <p class="mt-2 text-[15px] leading-6 text-gray-700">
              Enviamos um código de {{ TAMANHO_CODIGO }} números para
              <strong class="font-semibold">{{ emailMascarado }}</strong>. Digite-o abaixo para
              entrar.
            </p>
          </header>

          <form class="flex flex-col gap-6" @submit.prevent="confirmar">
            <FormField
              v-model="codigo"
              label="Código de confirmação"
              type="text"
              variant="outline"
              placeholder="000000"
              inputmode="numeric"
            />

            <p class="-mt-3 text-sm" :class="expirou ? 'text-red-700' : 'text-gray-600'">
              <template v-if="expirou">
                O código expirou. Volte e entre novamente para receber outro.
              </template>
              <template v-else>O código expira em {{ tempoFormatado }}.</template>
            </p>

            <p
              v-if="erro"
              role="alert"
              class="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
            >
              {{ erro }}
            </p>

            <FormButton type="submit" class="h-13! w-full" :disabled="carregando || expirou">
              Confirmar
            </FormButton>
          </form>

          <div class="mt-8 flex flex-col items-center gap-2 border-t border-gray-200 pt-8">
            <p class="text-[15px] text-gray-700">Não recebeu o código?</p>
            <RouterLink
              :to="{ name: contexto.login }"
              class="text-sm font-bold text-[#042d5c] hover:underline"
              @click="auth.cancelarDesafio()"
            >
              Voltar e entrar novamente
            </RouterLink>
          </div>
        </div>
      </div>
    </section>

    <!-- Coluna da imagem (somente desktop) -->
    <aside class="relative hidden overflow-hidden lg:block">
      <img
        :src="contexto.imagem"
        alt="Ilustração da plataforma Simple Mark"
        class="absolute inset-0 size-full object-cover object-right"
      />
    </aside>
  </main>
</template>