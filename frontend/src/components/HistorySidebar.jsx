function Icon({ children, size = 18 }) {
  return (
    <svg
      viewBox="0 0 24 24"
      width={size}
      height={size}
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      focusable="false"
    >
      {children}
    </svg>
  )
}

const ClockIcon = (
  <Icon>
    <path d="M3 12a9 9 0 1 0 3-6.7" />
    <path d="M3 4v5h5" />
    <path d="M12 8v4l3 2" />
  </Icon>
)

export default function HistorySidebar({ history, currentQuestion, open, onToggle, onSelect, onClear }) {
  const hasItems = history.length > 0

  return (
    <aside className={`history ${open ? 'history--open' : ''}`} aria-label="Historial de la sesión">
      <button
        type="button"
        className="history__rail"
        onClick={onToggle}
        aria-expanded={open}
        aria-controls="history-panel"
        aria-label="Abrir historial"
      >
        <span className="history__rail-panel">
          <Icon>
            <rect x="3" y="4" width="18" height="16" rx="2" />
            <path d="M9 4v16" />
            <path d="M13 10l2 2-2 2" />
          </Icon>
        </span>
        {ClockIcon}
        <span className="history__count">{history.length}</span>
      </button>

      <div id="history-panel" className="history__panel">
        <div className="history__top">
          <span className="history__title">
            {ClockIcon}
            Historial
            <span className="history__total">{history.length}</span>
          </span>
          <button
            type="button"
            className="history__close"
            onClick={onToggle}
            aria-expanded={open}
            aria-controls="history-panel"
            aria-label="Cerrar historial"
          >
            <Icon size={16}>
              <path d="M15 6l-6 6 6 6" />
            </Icon>
          </button>
        </div>

        {hasItems ? (
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
                    <Icon size={14}>
                      <circle cx="11" cy="11" r="6.5" />
                      <path d="M16 16l4 4" />
                    </Icon>
                    <span className="history__question">{item}</span>
                    {isCurrent && <span className="sr-only">Consulta actual</span>}
                  </button>
                </li>
              )
            })}
          </ul>
        ) : (
          <div className="history__empty">
            <p className="history__empty-title">Tu próxima consulta empieza aquí.</p>
            <p className="history__empty-text">Las preguntas de esta sesión aparecerán en este espacio.</p>
          </div>
        )}

        <div className="history__foot">
          {hasItems && (
            <button type="button" className="history__clear" onClick={onClear}>
              <Icon size={16}>
                <path d="M4 7h16" />
                <path d="M10 11v6M14 11v6" />
                <path d="M6 7l1 13h10l1-13" />
                <path d="M9 7V4h6v3" />
              </Icon>
              Limpiar historial
            </button>
          )}
          <p className="history__note">Solo durante esta sesión. Se elimina al recargar o cerrar la página.</p>
        </div>
      </div>
    </aside>
  )
}