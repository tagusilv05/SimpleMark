// CRIADOR: João Marcos
// frontend/src/services/perfilService.js
const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8080'

async function requisitar(caminho, { method = 'GET', json, formData, token, blob = false } = {}) {
  const headers = { Accept: '*/*' }
  let body

  if (json !== undefined) {
    headers['Content-Type'] = 'application/json'
    body = JSON.stringify(json)
  } else if (formData) {
    // Não definir Content-Type: o browser coloca o boundary do multipart sozinho
    body = formData
  }

  if (token) headers.Authorization = `Bearer ${token}`

  const resp = await fetch(`${API_URL}${caminho}`, { method, headers, body })

  if (!resp.ok) {
    let detalhe = ''
    try {
      const d = await resp.json()
      detalhe = d.detail ?? d.mensagem ?? ''
    } catch {
      /* resposta sem JSON */
    }
    throw new Error(typeof detalhe === 'string' && detalhe ? detalhe : `Erro ${resp.status}`)
  }

  return blob ? resp.blob() : resp.json()
}

/* ---------- Usuário (paciente e profissional) ---------- */

export const buscarInfoUsuario = (id, token) =>
  requisitar(`/paciente/buscar-info-usuario/${id}`, { token })

export const alterarInfoPessoal = ({ id, nome, email, telefone }, token) =>
  requisitar('/paciente/altera-info-pessoal', {
    method: 'PUT',
    json: { id, nome, email, telefone },
    token,
  })

export const buscarInfoEndereco = (id, token) =>
  requisitar(`/paciente/buscar-info-endereco/${id}`, { token })

export const alterarEndereco = (idUsuario, e, token) =>
  requisitar('/paciente/altera-endereco', {
    method: 'PUT',
    json: {
      id_usuario: idUsuario,
      cep: e.cep,
      cidade: e.cidade,
      logradouro: e.logradouro,
      numero: Number(e.numero),
      bairro: e.bairro,
      complemento: e.complemento,
    },
    token,
  })

export const excluirUsuario = (id, tipo, token) =>
  requisitar('/paciente/excluir-usuario', {
    method: 'DELETE',
    json: { id, tipo }, // tipo: 'paciente' | 'profissional'
    token,
  })

/* ---------- Profissional ---------- */

export const listarEspecialidades = (token) =>
  requisitar('/profissionais/lista-especialidade', { token })

export const buscarInfoProfissional = (idUsuario, token) =>
  requisitar(`/profissionais/buscar-info-profissional/${idUsuario}`, { token })

// especialidades: [{ id_especialidade, numero_conselho, conselho, valor }]
export function alterarInfoProfissional(idUsuario, infoProfissional, especialidades, token) {
  const form = new FormData()
  form.append(
    'dados',
    JSON.stringify({
      id_usuario: idUsuario,
      info_profissional: infoProfissional,
      especialidade: especialidades,
    }),
  )
  form.append('imagem', '') // a imagem é enviada em endpoint próprio
  return requisitar('/profissionais/alterar-info-profissional', {
    method: 'PUT',
    formData: form,
    token,
  })
}

export const excluirEspecialidade = (idUsuario, idEspecialidade, token) =>
  requisitar('/profissionais/excluir-especialidade', {
    method: 'DELETE',
    json: { id_usuario: idUsuario, id_especialidade: idEspecialidade },
    token,
  })

export function salvarImagemProfissional(idUsuario, arquivo, token) {
  const form = new FormData()
  form.append('id_usuario', idUsuario)
  form.append('imagem', arquivo)
  return requisitar('/profissionais/salvar-imagem-profissional', {
    method: 'POST',
    formData: form,
    token,
  })
}

// Retorna uma URL local (blob:) pronta para usar em <img :src>
export async function buscarImagemProfissional(idUsuario, token) {
  const blob = await requisitar(`/profissionais/buscar-imagem-profissional/${idUsuario}`, {
    token,
    blob: true,
  })
  return URL.createObjectURL(blob)
}