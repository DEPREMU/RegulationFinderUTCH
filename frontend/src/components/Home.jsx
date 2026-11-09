import Folio from './Folio.jsx'
import InfoNotice from './InfoNotice.jsx'

const STARTERS = [
  '¿Qué requisitos existen para presentar un examen de ingreso?',
  '¿Qué establece el reglamento sobre las evaluaciones?',
  '¿Qué disposiciones se aplican a los estudiantes?',
]

const STEPS = [
  { n: '01', title: 'Pregunta', text: 'Describe lo que necesitas consultar.' },
  { n: '02', title: 'Localiza', text: 'La consulta se clasifica y busca en documentos disponibles.' },
  { n: '03', title: 'Lee la fuente', text: 'Revisa hasta 3 artículos con su procedencia.' },
]

export function HomeIntro() {
  return (
    <div className="hero">
      <div>
        <p className="eyebrow">Reglamentos UTCH / Consulta documental</p>
        <h1 className="display">
          Encuentra artículos,
          <br />
          no interpretaciones.
        </h1>
      </div>
      <Folio expression="welcome" size={140} className="hero__folio" />
      <p className="lead">
        Haz una pregunta sobre el reglamento. Recuperamos hasta tres artículos existentes y mostramos su texto
        original, sin generar respuestas ni interpretaciones oficiales.
      </p>
    </div>
  )
}

export function HomeExtras({ onPick }) {
  return (
    <>
      <section className="starters" aria-labelledby="starters-title">
        <h2 id="starters-title" className="eyebrow">
          Puedes empezar por aquí
        </h2>
        <ul>
          {STARTERS.map((question) => (
            <li key={question}>
              <button type="button" className="starters__item" onClick={() => onPick(question)}>
                <span>{question}</span>
                <span aria-hidden="true">↗</span>
              </button>
            </li>
          ))}
        </ul>
      </section>

      <section id="como-funciona" className="how" aria-labelledby="how-title">
        <h2 id="how-title" className="eyebrow">
          Del documento a tu consulta
        </h2>
        <ol className="how__list">
          {STEPS.map((step) => (
            <li key={step.n}>
              <span className="how__n">{step.n}</span>
              <div>
                <p className="how__title">{step.title}</p>
                <p className="how__text">{step.text}</p>
              </div>
            </li>
          ))}
        </ol>
      </section>

      <InfoNotice />
    </>
  )
}
