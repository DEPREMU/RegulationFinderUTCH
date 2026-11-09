export default function InfoNotice() {
  return (
    <aside className="notice" aria-label="Aviso informativo">
      <span className="notice__icon" aria-hidden="true">
        i
      </span>
      <div>
        <p className="notice__title">Información orientativa, no oficial.</p>
        <p className="notice__text">Consulta la fuente documental para cualquier trámite.</p>
      </div>
    </aside>
  )
}
