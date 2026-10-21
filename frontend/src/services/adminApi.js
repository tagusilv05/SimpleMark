const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080'
const ACCESS_TOKEN_KEY = 'access_token'

function requestUrl(path) {
  return new URL(path, baseURL)
}

function headers(extra = {}) {
  const token = sessionStorage.getItem(ACCESS_TOKEN_KEY)
  return token ? { Authorization: `Bearer ${token}`, ...extra } : extra
}

async function parseResponse(response) {
  const responseText = await response.text()
  let body = null

  if (responseText) {
    try {
      body = JSON.parse(responseText)
    } catch {
      if (response.ok) throw new Error('A API retornou uma resposta inválida.')
    }
  }

  if (!response.ok) {
    const message = body?.detail ?? body?.mensagem
    throw new Error(
      typeof message === 'string'
        ? message
        : `Falha na requisição à API: ${response.status} ${response.statusText}`,
    )
  }

  return { data: body }
}

async function get(path, { params = {} } = {}) {
  const url = requestUrl(path)
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null) url.searchParams.set(key, value)
  }
  return parseResponse(await fetch(url, { headers: headers() }))
}

async function post(path, body = undefined) {
  const options = {
    method: 'POST',
    headers: headers(body === undefined ? {} : { 'Content-Type': 'application/json' }),
  }
  if (body !== undefined) options.body = JSON.stringify(body)
  return parseResponse(await fetch(requestUrl(path), options))
}

function clearAccessToken() {
  sessionStorage.removeItem(ACCESS_TOKEN_KEY)
}

export default { get, post, clearAccessToken }