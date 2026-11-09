import { useCallback, useEffect, useRef, useState } from 'react'
import Header from './components/Header.jsx'
import Footer from './components/Footer.jsx'
import HistorySidebar from './components/HistorySidebar.jsx'
import QueryForm from './components/QueryForm.jsx'
import Results from './components/Results.jsx'
import InfoNotice from './components/InfoNotice.jsx'
import { HomeIntro, HomeExtras } from './components/Home.jsx'
import { LoadingPanel, EmptyPanel, LowMatchPanel, ErrorPanel } from './components/StatusPanel.jsx'
import { searchArticles } from './services/search.js'

const MAX_HISTORY = 6
const EMPTY_MESSAGE = 'Ingrese una pregunta primero para consultar los documentos.'

export default function App() {
  const [question, setQuestion] = useState('')
  const [status, setStatus] = useState('idle') // idle | loading | results | empty | lowMatch | error
  const [articles, setArticles] = useState([])
  const [history, setHistory] = useState([])
  const [historyOpen, setHistoryOpen] = useState(false)
  const [validation, setValidation] = useState('')
  const [announcement, setAnnouncement] = useState('')

  const textareaRef = useRef(null)
  const requestId = useRef(0)

  // Cancela respuestas atrasadas si el componente se desmonta.
  useEffect(() => {
    const ref = requestId
    return () => {
      ref.current += 1
    }
  }, [])

  const runSearch = useCallback(async (rawQuestion) => {
    const text = rawQuestion.trim()

    if (!text) {
      setValidation(EMPTY_MESSAGE)
      setAnnouncement(EMPTY_MESSAGE)
      textareaRef.current?.focus()
      return
    }

    const current = ++requestId.current
    setValidation('')
    setQuestion(text)
    setStatus('loading')
    setAnnouncement('Consultando documentos disponibles…')
    setHistory((prev) => [text, ...prev.filter((item) => item !== text)].slice(0, MAX_HISTORY))
    setHistoryOpen(false)

    try {
      const result = await searchArticles(text)
      if (current !== requestId.current) return
      setArticles(result.articles ?? [])
      setStatus(result.status)
      if (result.status === 'results') {
        const total = result.articles.length
        setAnnouncement(`Se encontraron ${total} ${total === 1 ? 'artículo' : 'artículos'}.`)
      } else {
        setAnnouncement('No se encontraron artículos suficientemente relevantes.')
      }
    } catch {
      if (current !== requestId.current) return
      setArticles([])
      setStatus('error')
      setAnnouncement('No pudimos consultar los documentos. Tu pregunta se conservó.')
    }
  }, [])

  const handleChange = (value) => {
    setQuestion(value)
    if (validation) setValidation('')
  }

  const handleSelectHistory = (item) => {
    setQuestion(item)
    runSearch(item)
  }

  const handleClearHistory = () => {
    setHistory([])
    setHistoryOpen(false)
  }

  const handleReformulate = () => {
    textareaRef.current?.focus()
    textareaRef.current?.select()
  }

  const isIdle = status === 'idle'
  const isLoading = status === 'loading'

  return (
    <div className="app">
      <Header />

      <div className="layout">
        <HistorySidebar
          history={history}
          currentQuestion={isIdle ? '' : question}
          open={historyOpen}
          onToggle={() => setHistoryOpen((value) => !value)}
          onSelect={handleSelectHistory}
          onClear={handleClearHistory}
        />

        <main id="consultar" className="main">
          {isIdle && <HomeIntro />}
          {status === 'loading' && <p className="eyebrow main__kicker">Consulta en curso</p>}
          {status === 'loading' && <h1 className="display main__title">De la pregunta al documento.</h1>}

          <QueryForm
            value={question}
            onChange={handleChange}
            onSubmit={() => runSearch(question)}
            loading={isLoading}
            error={validation}
            showHint={isIdle || isLoading}
            textareaRef={textareaRef}
          />

          <div className="sr-only" role="status" aria-live="polite">
            {announcement}
          </div>

          {isLoading && <LoadingPanel />}
          {status === 'results' && <Results articles={articles} />}
          {status === 'empty' && <EmptyPanel onRetry={handleReformulate} />}
          {status === 'lowMatch' && (
            <LowMatchPanel onRetry={handleReformulate} />
          )}
          {status === 'error' && <ErrorPanel onRetry={() => runSearch(question)} />}

          {isIdle && <HomeExtras onPick={(text) => { setQuestion(text); setValidation(''); textareaRef.current?.focus() }} />}
          {(isLoading || status === 'empty' || status === 'lowMatch' || status === 'error') && <InfoNotice />}
        </main>
      </div>

      <Footer />
    </div>
  )
}
