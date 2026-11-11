import owl from '../assets/owl-mascot.png'
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

function StepIcon({ n }) {
  const common = {
    viewBox: '0 0 24 24',
    width: 20,
    height: 20,
    fill: 'none',
    stroke: 'currentColor',
    strokeWidth: 1.8,
    strokeLinecap: 'round',
    strokeLinejoin: 'round',
    'aria-hidden': 'true',
    focusable: 'false',
  }
  if (n === '01') {
    return (
      <svg {...common}>
        <path d="M4 5h16v11H9l-5 4z" />
        <path d="M8 9h8M8 12h5" />
      </svg>
    )
  }
  if (n === '02') {
    return (
      <svg {...common}>
        <circle cx="11" cy="11" r="6" />
        <path d="M16 16l4 4" />
      </svg>
    )
  }
  return (
    <svg {...common}>
      <path d="M3 5.5C5 4.5 8 4.5 12 6c4-1.5 7-1.5 9-.5V18c-2-1-5-1-9 .5C8 17 5 17 3 18z" />
      <path d="M12 6v12.5" />
    </svg>
  )
}

export function HomeIntro() {
  return (
    <div className="hero">
      <img className="status__owl" src={owl} width="120" alt="" aria-hidden="true" decoding="async" />
      <div className="hero__text">
        <p className="eyebrow">Reglamentos UTCH / Consulta documental</p>
        <h1 className="display">
          Encuentra artículos,
          <br />
          <em>no interpretaciones.</em>
        </h1>
        <p className="lead">
          Haz una pregunta sobre el reglamento. Recuperamos hasta tres artículos existentes y mostramos su texto
          original, sin generar respuestas ni interpretaciones oficiales.
        </p>
      </div>
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
                {question}
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
              <div className="how__top">
                <span className="how__icon">
                  <StepIcon n={step.n} />
                </span>
                <span className="how__n">{step.n}</span>
              </div>
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