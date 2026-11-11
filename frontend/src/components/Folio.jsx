// Folio: mascota decorativa (búho). Es solo ornamento: el estado siempre
// se comunica también con texto. En error se muestra un ícono de advertencia.
import owl from '../assets/owl-mascot.png'

export default function Folio({ expression = 'welcome', size = 120, className = '' }) {
  if (expression === 'error') {
    const diameter = Math.min(size, 56)
    return (
      <span
        className={`folio folio--alert ${className}`}
        style={{ width: diameter, height: diameter }}
        role="presentation"
        aria-hidden="true"
      >
        <svg
          viewBox="0 0 24 24"
          width={diameter * 0.45}
          height={diameter * 0.45}
          fill="none"
          stroke="currentColor"
          strokeWidth="1.8"
          strokeLinecap="round"
          strokeLinejoin="round"
          focusable="false"
        >
          <path d="M12 4 L21 19 H3 Z" />
          <path d="M12 10v4" />
          <path d="M12 16.5h.01" />
        </svg>
      </span>
    )
  }

  return (
    <img
      className={`folio ${className}`}
      src={owl}
      width={size}
      alt=""
      role="presentation"
      aria-hidden="true"
      decoding="async"
    />
  )
}