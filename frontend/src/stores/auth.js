/**
 * Store de autenticação (Pinia)
 *
 * Guarda o desafio do login (entre as duas etapas), o token e a conta logada.
 * "Lembrar de mim" marcado  -> sessão salva no localStorage (sobrevive ao fechar o navegador)
 * "Lembrar de mim" desmarcado -> sessionStorage (some ao fechar a aba)
 */

import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import * as authService from '@/services/authService'
import { ApiError } from '@/services/authService'

const CHAVE = 'simplemark.auth'

export const ROTULOS_PERFIL = {
  paciente: 'Paciente',
  profissional: 'Profissional',
  administrador: 'Administrador',
}

function lerSessaoSalva() {
  for (const armazenamento of [localStorage, sessionStorage]) {
    try {
      const bruto = armazenamento.getItem(CHAVE)
      if (bruto) return JSON.parse(bruto)
    } catch {
      // armazenamento indisponível ou conteúdo inválido
    }
  }
  return null
}

function salvarSessao(dados, lembrar) {
  limparSessaoSalva()
  try {
    ;(lembrar ? localStorage : sessionStorage).setItem(CHAVE, JSON.stringify(dados))
  } catch {
    // sem armazenamento: a sessão vale só enquanto a página estiver aberta
  }
}

function limparSessaoSalva() {
  for (const armazenamento of [localStorage, sessionStorage]) {
    try {
      armazenamento.removeItem(CHAVE)
    } catch {
      // ignora
    }
  }
}

export const useAuthStore = defineStore('auth', () => {
  const salva = lerSessaoSalva()

  const token = ref(salva?.token ?? null)
  const usuario = ref(salva?.usuario ?? null)
  // Preenchido entre a etapa 1 e a etapa 2 do login
  const desafio = ref(null)

  const logado = computed(() => Boolean(token.value && usuario.value))
  const perfil = computed(() => usuario.value?.perfil ?? null)

  // Formato que o AppHeader espera: { name, role }
  const usuarioHeader = computed(() =>
    usuario.value
      ? {
          name: usuario.value.nome,
          role: ROTULOS_PERFIL[usuario.value.perfil] ?? '',
          perfil: usuario.value.perfil,
        }
      : null,
  )

  // Para onde o usuário vai logo depois de entrar
  const rotaInicial = computed(() =>
    perfil.value === 'administrador'
      ? { name: 'gestaoDeUsuarios' }
      : perfil.value === 'profissional'
        ? { name: 'dashboardDoProfissional' }
        : { name: 'home' },
  )

  /** Etapa 1. `perfilEsperado` é a tela de onde o usuário veio (paciente | profissional | administrador). */
  async function iniciarLogin({ identificador, senha, perfilEsperado, lembrar }) {
    const resposta = await authService.iniciarLogin({ identificador, senha })
    desafio.value = {
      idDesafio: resposta.id_desafio,
      emailMascarado: resposta.email_mascarado,
      expiraEmSegundos: resposta.expira_em_segundos,
      criadoEm: Date.now(),
      perfilEsperado,
      lembrar: Boolean(lembrar),
    }
  }

  /** Etapa 2. Só guarda a sessão se o perfil da conta bater com a tela usada. */
  async function confirmarLogin(codigo) {
    if (!desafio.value) {
      throw new ApiError('Sua confirmação expirou. Entre novamente para receber outro código.', 401)
    }
    const { idDesafio, perfilEsperado, lembrar } = desafio.value
    const resposta = await authService.confirmarLogin({ idDesafio, codigo })

    if (resposta.usuario.perfil !== perfilEsperado) {
      // Conta válida, mas na tela errada: encerra a sessão recém-aberta e avisa.
      authService.sair(resposta.access_token).catch(() => {})
      desafio.value = null
      const real = ROTULOS_PERFIL[resposta.usuario.perfil] ?? resposta.usuario.perfil
      throw new ApiError(
        `Esta conta é de ${real}. Entre pela tela de login de ${real}.`,
        403,
      )
    }

    token.value = resposta.access_token
    usuario.value = resposta.usuario
    desafio.value = null
    salvarSessao({ token: token.value, usuario: usuario.value }, lembrar)
  }

  function cancelarDesafio() {
    desafio.value = null
  }

  /** Logout: avisa o servidor (sem travar se falhar) e limpa tudo. */
  async function logout() {
    const tokenAtual = token.value
    token.value = null
    usuario.value = null
    desafio.value = null
    limparSessaoSalva()
    if (tokenAtual) {
      try {
        await authService.sair(tokenAtual)
      } catch {
        // sessão já encerrada/expirada no servidor: tudo certo
      }
    }
  }

  return {
    token,
    usuario,
    desafio,
    logado,
    perfil,
    usuarioHeader,
    rotaInicial,
    iniciarLogin,
    confirmarLogin,
    cancelarDesafio,
    logout,
  }
})