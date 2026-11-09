import Folio from './Folio.jsx'

const STEPS = ['Consulta recibida', 'Localizando la fuente documental', 'Preparando el texto original']

export function LoadingPanel() {
  return (
    <section className="status" aria-labelledby="loading-title">
      <Folio expression="search" size={130} />
      <div className="status__body">
        <h2 id="loading-title" className="status__title">
          Consultando documentos disponibles…
        </h2>
        <p className="status__text">Conservamos tu pregunta mientras localizamos artículos existentes.</p>
        <ol className="steps">
          {STEPS.map((step, i) => (
            <li key={step} className={`steps__item ${i === 0 ? 'steps__item--done' : ''} ${i === 1 ? 'steps__item--active' : ''}`}>
              <span className="steps__mark" aria-hidden="true">
                {i === 0 ? '✓' : `0${i + 1}`}
              </span>
              {step}
            </li>
          ))}
        </ol>
        <div className="progress" aria-hidden="true">
          <span className="progress__bar" />
        </div>
      </div>
    </section>
  )
}

export function EmptyPanel({ onRetry }) {
  return (
    <section className="status status--wide" aria-labelledby="empty-title">
      <Folio expression="reflection" size={130} />
      <div className="status__body">
        <p className="eyebrow">Sin artículos encontrados</p>
        <h2 id="empty-title" className="display display--medium">
          Probemos con otra pregunta.
        </h2>
        <p className="lead lead--small">
          No encontramos artículos para esta consulta en los documentos disponibles. No hay resultados que mostrar.
        </p>
        <p className="status__tip">
          Prueba con el nombre de la actividad y el aspecto que deseas consultar: participación, requisitos o
          convocatoria.
        </p>
        <button type="button" className="button button--primary" onClick={onRetry}>
          Reformular pregunta <span aria-hidden="true">→</span>
        </button>
      </div>
    </section>
  )
}

export function LowMatchPanel({ onRetry }) {
  return (
    <section className="status status--wide" aria-labelledby="lowmatch-title">
      <Folio expression="reflection" size={130} />
      <div className="status__body">
        <p className="eyebrow">Necesitamos mayor precisión</p>
        <h2 id="lowmatch-title" className="display display--medium">
          Una pregunta más específica, una mejor fuente.
        </h2>
        <p className="lead lead--small">
          Hay coincidencias documentales, pero no son suficientemente
          relevantes para tu pregunta. Preferimos no mostrar artículos
          débilmente relacionados.
        </p>
        <button
          type="button"
          className="button button--primary"
          onClick={onRetry}
        >
          Reformular pregunta <span aria-hidden="true">→</span>
        </button>
      </div>
    </section>
  )
}

export function ErrorPanel({ onRetry }) {
  return (
    <section className="status status--wide" aria-labelledby="error-title">
      <Folio expression="error" size={130} />
      <div className="status__body">
        <p className="eyebrow">Conexión interrumpida</p>
        <h2 id="error-title" className="display display--medium">
          Tu pregunta sigue aquí.
        </h2>
        <p className="lead lead--small">
          No pudimos consultar los documentos. Revisa tu conexión e inténtalo otra vez; no necesitas escribir de
          nuevo tu pregunta.
        </p>
        <button type="button" className="button button--primary" onClick={onRetry}>
          Intentar nuevamente <span aria-hidden="true">→</span>
        </button>
        <p className="status__small">Si el problema continúa, vuelve a consultar más tarde.</p>
      </div>
    </section>
  )
}
