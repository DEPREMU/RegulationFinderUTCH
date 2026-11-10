import { useRef } from 'react'

export default function QueryForm({
  value,
  onChange,
  onSubmit,
  loading,
  error,
  showHint,
  textareaRef,
}) {
  const fallbackRef = useRef(null)
  const ref = textareaRef ?? fallbackRef

  const handleSubmit = (event) => {
    event.preventDefault()
    onSubmit()
  }

  const handleKeyDown = (event) => {
    // Enter envía; Shift+Enter inserta salto de línea.
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      onSubmit()
    }
  }

  const handleClear = () => {
    onChange('')
    ref.current?.focus()
  }

  return (
    <form className="query" onSubmit={handleSubmit} noValidate>
      <label className="eyebrow eyebrow--muted" htmlFor="question">
        Tu pregunta
      </label>
      <div className={`query__field ${loading ? 'query__field--busy' : ''} ${error ? 'query__field--invalid' : ''}`}>
        <span className="query__icon" aria-hidden="true">
          <svg
            viewBox="0 0 24 24"
            width="20"
            height="20"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.8"
            strokeLinecap="round"
            strokeLinejoin="round"
            focusable="false"
          >
            <circle cx="11" cy="11" r="6.5" />
            <path d="M16 16l4 4" />
          </svg>
        </span>
        <div className="query__body">
          <textarea
            id="question"
            ref={ref}
            className="query__input"
            rows={showHint ? 2 : 1}
            value={value}
            onChange={(event) => onChange(event.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Escribe tu pregunta sobre el reglamento UTCH"
            readOnly={loading}
            aria-invalid={error ? 'true' : 'false'}
            aria-describedby={error ? 'question-error' : 'question-help'}
          />
          {showHint && (
            <p id="question-help" className="query__help">
              Una pregunta concreta ayuda a encontrar el artículo.
            </p>
          )}
        </div>
        {value && !loading && (
          <button type="button" className="query__clear" onClick={handleClear} aria-label="Borrar pregunta">
            <svg
              viewBox="0 0 24 24"
              width="16"
              height="16"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              aria-hidden="true"
              focusable="false"
            >
              <path d="M6 6l12 12M18 6L6 18" />
            </svg>
          </button>
        )}
        <button type="submit" className="button button--primary" disabled={loading}>
          {loading ? 'Buscando artículos…' : 'Buscar artículos'}
          <span aria-hidden="true"> →</span>
        </button>
      </div>

      {error && (
        <p id="question-error" className="query__error" role="alert">
          {error}
        </p>
      )}

      <p className="query__limit">Hasta 3 artículos · Texto original</p>
    </form>
  )
}