function errorMessage(status, data) {
  const { detail, error } = data
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) return detail.map(item => item.msg).filter(Boolean).join('. ') || 'Please check your input.'
  if (typeof error === 'string') return error
  if ([502, 503, 504].includes(status)) return 'This service is unavailable right now. It may be starting up, so please try again in a minute.'
  return `Request failed (${status}).`
}

async function request(url, options) {
  let response
  try { response = await fetch(url, options) }
  catch { throw new Error('Cannot connect to the server. Please try again later.') }
  const data = await response.json().catch(() => ({}))
  if (!response.ok) throw new Error(errorMessage(response.status, data))
  return data
}

export function getJson(url) { return request(url) }

export function sendPhoto(file, region) {
  const body = new FormData()
  body.append('image', file)
  body.append('region', region)
  return request('/classification/recommend', { method: 'POST', body })
}

export function sendChat(token, text) {
  return request(`/chat/${token}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  })
}

async function isHealthy(url) {
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), 20000)
  try {
    const response = await fetch(url, { signal: controller.signal, cache: 'no-store' })
    const data = await response.json()
    return response.ok && data.status === 'ok'
  } catch { return false }
  finally { clearTimeout(timer) }
}

export async function wakeService(url, shouldStop = () => false, limit = 90000) {
  const end = Date.now() + limit
  while (Date.now() < end && !shouldStop()) {
    if (await isHealthy(url)) return true
    await new Promise(resolve => setTimeout(resolve, 5000))
  }
  return false
}

export function getChat(token) { return request(`/chat/${token}`) }

export function clearChat(token) { return request(`/chat/${token}`, { method: 'DELETE' }) }
