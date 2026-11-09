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

  return (
    <form className="query" onSubmit={handleSubmit} noValidate>
      <label className="eyebrow eyebrow--muted" htmlFor="question">
        Tu pregunta
      </label>
      <div className={`query__field ${loading ? 'query__field--busy' : ''} ${error ? 'query__field--invalid' : ''}`}>
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

      {error && (
        <p id="question-error" className="query__error" role="alert">
          {error}
        </p>
      )}

      <div className="query__actions">
        <span className="query__limit">Hasta 3 artículos · Texto original</span>
        <button type="submit" className="button button--primary" disabled={loading}>
          {loading ? 'Buscando artículos…' : 'Buscar artículos'}
          <span aria-hidden="true"> →</span>
        </button>
      </div>
    </form>
  )
}
