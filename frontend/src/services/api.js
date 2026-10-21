const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080'
const ACCESS_TOKEN_KEY = 'access_token'

function url(path) {
  return new URL(path, baseURL).toString()
}

export function setAccessToken(token) {
  sessionStorage.setItem(ACCESS_TOKEN_KEY, token)
}

export function clearAccessToken() {
  sessionStorage.removeItem(ACCESS_TOKEN_KEY)
}

async function get(path, { params = {} } = {}) {
  const requestUrl = new URL(path, baseURL)

  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null) {
      requestUrl.searchParams.set(key, value)
    }
  }

  const token = sessionStorage.getItem(ACCESS_TOKEN_KEY)
  const response = await fetch(requestUrl, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  })

  const responseText = await response.text()
  let body = null
  if (responseText) {
    try {
      body = JSON.parse(responseText)
    } catch {
      if (response.ok) {
        throw new Error('A API retornou uma resposta inválida.')
      }
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

export default { get, url, setAccessToken, clearAccessToken }
