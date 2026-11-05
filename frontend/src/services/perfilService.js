// CRIADOR: João Marcos
// frontend/src/services/perfilService.js
/**
 * perfilService — chamadas da área "Minha Conta" (paciente e profissional).
 *
 * Usa o cliente HTTP comum (services/api.js): o token da sessão vai sozinho e um
 * 401 encerra a sessão local. As rotas só aceitam o id da própria conta logada.
 *
 * ENDPOINTS
 *   GET    /usuario/buscar-info-usuario/{id}            dados pessoais
 *   GET    /usuario/buscar-info-endereco/{id}           endereço (404 se não houver)
 *   PUT    /usuario/altera-info-pessoal                 { id, nome, email, telefone }
 *   PUT    /usuario/altera-endereco                     { id_usuario, cep, cidade, ... }
 *   PUT    /usuario/alterar-senha                       { senha_atual, nova_senha }
 *   PATCH  /usuario/inativar-usuario?id_usuario=        desativa a conta
 *   DELETE /usuario/excluir-usuario                     { id, tipo }
 *   GET    /profissionais/lista-especialidade
 *   GET    /profissionais/buscar-info-profissional/{id}
 *   PUT    /profissionais/alterar-info-profissional     multipart: dados (JSON)
 *   DELETE /profissionais/excluir-especialidade         { id_usuario, id_especialidade }
 *   POST   /profissionais/salvar-imagem-profissional    multipart: id_usuario, imagem
 *   GET    /profissionais/buscar-imagem-profissional/{id}
 *
 * O último argumento `token` das funções é aceito só por compatibilidade e é ignorado.
 */
import { api } from '@/services/api'

/* ---------- Usuário (paciente e profissional) ---------- */

export const buscarInfoUsuario = (id) => api.get(`/usuario/buscar-info-usuario/${id}`)

export const alterarInfoPessoal = ({ id, nome, email, telefone }) =>
  api.put('/usuario/altera-info-pessoal', { id, nome, email, telefone })

/** Endereço do usuário, ou null se ainda não houver um cadastrado. */
export async function buscarInfoEndereco(id) {
  try {
    return await api.get(`/usuario/buscar-info-endereco/${id}`)
  } catch (erro) {
    if (erro.status === 404) return null
    throw erro
  }
}

export const alterarEndereco = (idUsuario, e) =>
  api.put('/usuario/altera-endereco', {
    id_usuario: idUsuario,
    cep: e.cep,
    cidade: e.cidade,
    logradouro: e.logradouro,
    numero: e.numero == null ? null : String(e.numero),
    bairro: e.bairro,
    complemento: e.complemento || null,
  })

export const alterarSenha = ({ atual, nova }) =>
  api.put('/usuario/alterar-senha', { senha_atual: atual, nova_senha: nova })

export const inativarUsuario = (id) =>
  api.patch(`/usuario/inativar-usuario?id_usuario=${encodeURIComponent(id)}`)

export const excluirUsuario = (id, tipo) =>
  api.delete('/usuario/excluir-usuario', { body: { id, tipo } }) // tipo: 'paciente' | 'profissional'

/* ---------- Profissional ---------- */

export const listarEspecialidades = () => api.get('/profissionais/lista-especialidade')

export const buscarInfoProfissional = (idUsuario) =>
  api.get(`/profissionais/buscar-info-profissional/${idUsuario}`)

// especialidades: [{ id_especialidade, numero_conselho, conselho, valor }]
export function alterarInfoProfissional(idUsuario, infoProfissional, especialidades) {
  const form = new FormData()
  form.append(
    'dados',
    JSON.stringify({
      id_usuario: idUsuario,
      info_profissional: infoProfissional,
      especialidade: especialidades,
    }),
  )
  // A imagem é enviada no endpoint próprio (salvarImagemProfissional)
  return api.put('/profissionais/alterar-info-profissional', form)
}

export const excluirEspecialidade = (idUsuario, idEspecialidade) =>
  api.delete('/profissionais/excluir-especialidade', {
    body: { id_usuario: idUsuario, id_especialidade: idEspecialidade },
  })

export function salvarImagemProfissional(idUsuario, arquivo) {
  const form = new FormData()
  form.append('id_usuario', idUsuario)
  form.append('imagem', arquivo)
  return api.post('/profissionais/salvar-imagem-profissional', form)
}

// Retorna uma URL local (blob:) pronta para usar em <img :src>
export async function buscarImagemProfissional(idUsuario) {
  const blob = await api.get(`/profissionais/buscar-imagem-profissional/${idUsuario}`, null, { blob: true })
  return URL.createObjectURL(blob)
}
