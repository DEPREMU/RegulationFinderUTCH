export default function InfoNotice() {
  return (
    <aside className="notice" aria-label="Aviso informativo">
      <span className="notice__icon" aria-hidden="true">
        <svg
          viewBox="0 0 24 24"
          width="16"
          height="16"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.8"
          strokeLinecap="round"
          strokeLinejoin="round"
          focusable="false"
        >
          <circle cx="12" cy="12" r="9" />
          <path d="M12 11v5" />
          <path d="M12 8h.01" />
        </svg>
      </span>
      <div className="notice__body">
        <p className="notice__title">Información orientativa, no oficial.</p>
        <p className="notice__text">Consulta la fuente documental para cualquier trámite.</p>
      </div>
    </aside>
  )
}