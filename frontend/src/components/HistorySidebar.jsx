export default function HistorySidebar({ history, currentQuestion, open, onToggle, onSelect, onClear }) {
  const hasItems = history.length > 0

  return (
    <aside className={`history ${open ? 'history--open' : ''}`} aria-label="Historial de la sesión">
      <button
        type="button"
        className="history__header"
        onClick={onToggle}
        aria-expanded={open}
        aria-controls="history-panel"
      >
        <span className="history__title">Historial reciente</span>
        <span className="history__chevron" aria-hidden="true">
          {open ? '×' : '⌄'}
        </span>
        <span className="history__undo" aria-hidden="true">
          ↶
        </span>
      </button>

      <div id="history-panel" className="history__panel">
        {hasItems ? (
          <>
            <ul className="history__list">
              {history.map((item) => {
                const isCurrent = item === currentQuestion
                return (
                  <li key={item}>
                    <button
                      type="button"
                      className={`history__item ${isCurrent ? 'history__item--current' : ''}`}
                      onClick={() => onSelect(item)}
                      aria-current={isCurrent ? 'true' : undefined}
                    >
                      {isCurrent && <span className="history__badge">Consulta actual</span>}
                      <span className="history__question">{item}</span>
                      {isCurrent && <span className="history__meta">Pregunta de esta sesión</span>}
                    </button>
                  </li>
                )
              })}
            </ul>
            <button type="button" className="history__clear" onClick={onClear}>
              Limpiar historial
            </button>
          </>
        ) : (
          <div className="history__empty">
            <span className="history__dash" aria-hidden="true">
              —
            </span>
            <p className="history__empty-title">Tu próxima consulta empieza aquí.</p>
            <p className="history__empty-text">Las preguntas de esta sesión aparecerán en este espacio.</p>
          </div>
        )}
        <p className="history__note">Solo durante esta sesión. Se elimina al recargar o cerrar la página.</p>
      </div>
    </aside>
  )
}
