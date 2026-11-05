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

// Área inicial de cada perfil, logo depois do login
export const ROTA_INICIAL_PERFIL = {
  paciente: { name: 'home' },
  profissional: { name: 'dashboardDoProfissional' },
  administrador: { name: 'gestaoDeUsuarios' },
}

// Tela de login de cada perfil
export const ROTA_LOGIN_PERFIL = {
  paciente: 'login/paciente',
  profissional: 'login/profissional',
  administrador: 'login/administrador',
}

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

  // Para onde o usuário vai logo depois de entrar (área do próprio perfil)
  const rotaInicial = computed(() => ROTA_INICIAL_PERFIL[perfil.value] ?? { name: 'home' })

  // Sessão já conferida com o servidor nesta aba (evita uma chamada por navegação)
  let validacao = null
  let validadaEm = 0
  const REVALIDAR_MS = 5 * 60 * 1000

  /** Apaga a sessão só no navegador (o servidor já não aceita o token). */
  function limparSessaoLocal() {
    token.value = null
    usuario.value = null
    validacao = null
    validadaEm = 0
    limparSessaoSalva()
  }

  /**
   * Confere o token no servidor (GET /auth/eu) e atualiza os dados da conta.
   * Token recusado (sessão encerrada, expirada ou conta banida) apaga a sessão local.
   * Sem conexão, mantém a sessão salva. Devolve true se continua logado.
   */
  async function validarSessao({ forcar = false } = {}) {
    if (!token.value) return false
    if (!forcar && validadaEm && Date.now() - validadaEm < REVALIDAR_MS) return logado.value
    if (validacao) return validacao

    const tokenConferido = token.value
    validacao = authService
      .obterUsuario(tokenConferido)
      .then((dados) => {
        if (token.value !== tokenConferido) return logado.value
        usuario.value = dados
        validadaEm = Date.now()
        const lembrar = (() => {
          try {
            return Boolean(localStorage.getItem(CHAVE))
          } catch {
            return false
          }
        })()
        salvarSessao({ token: token.value, usuario: dados }, lembrar)
        return true
      })
      .catch((erro) => {
        if (erro.status === 401 || erro.status === 403) {
          if (token.value === tokenConferido) limparSessaoLocal()
          return false
        }
        return logado.value
      })
      .finally(() => {
        validacao = null
      })
    return validacao
  }

  /** Etapa 1. `perfilEsperado` é a tela de onde o usuário veio (paciente | profissional | administrador). */
  async function iniciarLogin({ identificador, senha, perfilEsperado, lembrar, redirecionar }) {
    const resposta = await authService.iniciarLogin({ identificador, senha })
    desafio.value = {
      idDesafio: resposta.id_desafio,
      emailMascarado: resposta.email_mascarado,
      expiraEmSegundos: resposta.expira_em_segundos,
      criadoEm: Date.now(),
      perfilEsperado,
      lembrar: Boolean(lembrar),
      redirecionar: redirecionar || null,
    }
  }

  /** Etapa 2. Só guarda a sessão se o perfil da conta bater com a tela usada. */
  async function confirmarLogin(codigo) {
    if (!desafio.value) {
      throw new ApiError('Sua confirmação expirou. Entre novamente para receber outro código.', 401)
    }
    const { idDesafio, perfilEsperado, lembrar, redirecionar } = desafio.value
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
    validadaEm = Date.now()
    salvarSessao({ token: token.value, usuario: usuario.value }, lembrar)

    // Volta para a página protegida que pediu o login, se for da área deste perfil
    return redirecionar || rotaInicial.value
  }

  /** Atualiza os dados da conta logada (ex.: nome e e-mail editados em Minha Conta). */
  function atualizarUsuario(parcial) {
    if (!usuario.value) return
    usuario.value = { ...usuario.value, ...parcial }
    let lembrar = false
    try {
      lembrar = Boolean(localStorage.getItem(CHAVE))
    } catch {
      // armazenamento indisponível
    }
    salvarSessao({ token: token.value, usuario: usuario.value }, lembrar)
  }

  function cancelarDesafio() {
    desafio.value = null
  }

  /** Logout: avisa o servidor (sem travar se falhar) e limpa tudo. */
  async function logout() {
    const tokenAtual = token.value
    desafio.value = null
    limparSessaoLocal()
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
    validarSessao,
    limparSessaoLocal,
    atualizarUsuario,
    iniciarLogin,
    confirmarLogin,
    cancelarDesafio,
    logout,
  }
})