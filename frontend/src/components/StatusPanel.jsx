import owl from '../assets/owl-mascot.png'

function PencilIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      width="16"
      height="16"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      focusable="false"
    >
      <path d="M4 20l4-1 11-11-3-3L5 16z" />
      <path d="M14 7l3 3" />
    </svg>
  )
}

function RetryIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      width="16"
      height="16"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      focusable="false"
    >
      <path d="M4 12a8 8 0 1 0 3-6.2" />
      <path d="M4 4v5h5" />
    </svg>
  )
}

export function LoadingPanel() {
  return (
    <section className="status status--loading" aria-labelledby="loading-title">
      <div className="status__loadhead">
        <div className="progress" aria-hidden="true">
          <span className="progress__bar" />
        </div>
        <h2 id="loading-title" className="status__loadtitle">
          Buscando en los documentos normativos…
        </h2>
      </div>
      <div className="skeletons" aria-hidden="true">
        {[0, 1, 2].map((i) => (
          <div key={i} className="skeleton">
            <span className="skeleton__side" />
            <div className="skeleton__body">
              <span />
              <span />
              <span />
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}

export function EmptyPanel({ onRetry }) {
  return (
    <section className="status status--card" aria-labelledby="empty-title">
      <img className="status__owl" src={owl} width="88" alt="" aria-hidden="true" decoding="async" />
      <h2 id="empty-title" className="status__title">
        No encontramos artículos suficientemente relevantes
      </h2>
      <p className="status__text">
        Para no mostrarte información equivocada, el sistema se abstiene cuando la coincidencia no es clara. Intenta
        con otras palabras o con un tema más específico.
      </p>
      <button type="button" className="button button--primary" onClick={onRetry}>
        <PencilIcon />
        Reformular pregunta
      </button>
      <p className="status__tip">Prueba: usa términos como “inscripción”, “baja”, “calificaciones”.</p>
    </section>
  )
}

export function LowMatchPanel({ onRetry }) {
  return (
    <section className="status status--card" aria-labelledby="lowmatch-title">
      <img className="status__owl" src={owl} width="88" alt="" aria-hidden="true" decoding="async" />
      <h2 id="lowmatch-title" className="status__title">
        No encontramos artículos suficientemente relevantes
      </h2>
      <p className="status__text">
        Para no mostrarte información equivocada, el sistema se abstiene cuando la coincidencia no es clara. Intenta
        con otras palabras o con un tema más específico.
      </p>
      <button type="button" className="button button--primary" onClick={onRetry}>
        <PencilIcon />
        Reformular pregunta
      </button>
      <p className="status__tip">Prueba: usa términos como “inscripción”, “baja”, “calificaciones”.</p>
    </section>
  )
}

export function ErrorPanel({ onRetry }) {
  return (
    <section className="status status--card" aria-labelledby="error-title">
      <img className="status__owl" src={owl} width="88" alt="" aria-hidden="true" decoding="async" />
      <h2 id="error-title" className="status__title">
        No pudimos conectar con el servidor
      </h2>
      <p className="status__text">
        La consulta no llegó al sistema de búsqueda. Revisa la conexión de red e inténtalo de nuevo en unos segundos.
      </p>
      <button type="button" className="button button--secondary" onClick={onRetry}>
        <RetryIcon />
        Reintentar
      </button>
    </section>
  )
}