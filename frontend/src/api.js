async function request(url, options) {
  let response
  try { response = await fetch(url, options) }
  catch { throw new Error('Cannot connect to the server. Please try again later.') }
  const data = await response.json().catch(() => ({}))
  if (!response.ok) {
    const detail = data.detail
    if ([502, 503, 504].includes(response.status)) throw new Error('This service is unavailable right now. Please try again later.')
    throw new Error(typeof detail === 'string' ? detail : `Request failed (${response.status}).`)
  }
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
