// Servicio de búsqueda documental conectado al backend Flask.

const API_URL = import.meta.env.VITE_API_URL ?? '/api/search'
const REQUEST_TIMEOUT = 10000

function normalize(payload) {
  const statusMap = {
    ok: 'results',
    empty: 'empty',
    low_match: 'lowMatch',
  }

  const status = statusMap[payload.status] ?? 'error'

  const articles = Array.isArray(payload.articles)
    ? payload.articles.slice(0, 3).map((article) => ({
        number: article.article_id,
        document: article.source,
        text: article.text,
        topic: article.topic,
      }))
    : []

  if (status === 'results' && articles.length === 0) {
    return { status: 'empty', articles: [] }
  }

  return { status, articles }
}

export async function searchArticles(question, { signal } = {}) {
  const controller = new AbortController()

  const timeoutId = setTimeout(() => {
    controller.abort()
  }, REQUEST_TIMEOUT)

  const handleAbort = () => controller.abort()

  signal?.addEventListener('abort', handleAbort)

  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ question }),
      signal: controller.signal,
    })

    if (!response.ok) {
      throw new Error(`Error ${response.status}`)
    }

    return normalize(await response.json())
  } finally {
    clearTimeout(timeoutId)
    signal?.removeEventListener('abort', handleAbort)
  }
}