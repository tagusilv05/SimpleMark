/**
 * useLogin — lógica compartilhada pelas 3 telas de login (etapa 1: senha)
 *
 * USO (dentro do <script setup> da tela):
 *
 *   const { carregando, erro, entrar } = useLogin('paciente')   // 'profissional' | 'administrador'
 *   ...
 *   <form @submit.prevent="entrar(form)">
 *
 * Depois de a senha ser aceita, a API envia um código por e-mail e a tela
 * segue para `login/confirmar` (etapa 2).
 */

import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

export function useLogin(perfilEsperado) {
  const auth = useAuthStore()
  const router = useRouter()
  const route = useRoute()

  // Página protegida que mandou para o login (?redirect=/caminho). Só caminhos internos.
  function destinoSeguro() {
    const destino = route.query.redirect
    return typeof destino === 'string' && destino.startsWith('/') && !destino.startsWith('//')
      ? destino
      : null
  }

  const carregando = ref(false)
  const erro = ref('')

  async function entrar({ email, senha, lembrar }) {
    if (carregando.value) return
    erro.value = ''

    const identificador = (email ?? '').trim()
    if (!identificador || !senha) {
      erro.value = 'Informe o e-mail e a senha para entrar.'
      return
    }
    if (senha.length < 8) {
      erro.value = 'A senha deve ter no mínimo 8 caracteres.'
      return
    }

    carregando.value = true
    try {
      await auth.iniciarLogin({
        identificador,
        senha,
        perfilEsperado,
        lembrar,
        redirecionar: destinoSeguro(),
      })
      router.push({ name: 'login/confirmar' })
    } catch (e) {
      erro.value = e.message || 'Não foi possível entrar. Tente novamente.'
    } finally {
      carregando.value = false
    }
  }

  return { carregando, erro, entrar }
}