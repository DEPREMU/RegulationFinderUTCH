// Folio: mascota decorativa con seis expresiones sobre una misma silueta.
// Es solo ornamento: el estado siempre se comunica también con texto.

const SLATE = '#455258'
const SLATE_DARK = '#3A464B'
const WING = '#566468'
const FACE = '#D5DDD7'
const IVORY = '#F5F0E1'
const GREEN = '#5FBB52'
const BEAK = '#C08A3E'
const INK = '#263438'

function Eyes({ expression }) {
  if (expression === 'rest') {
    return (
      <g stroke={INK} strokeWidth="1.6" fill="none" strokeLinecap="round">
        <path d="M44 56q6 4 12 0" />
        <path d="M74 56q6 4 12 0" />
      </g>
    )
  }
  if (expression === 'error') {
    return (
      <g stroke={INK} strokeWidth="1.6" fill="none" strokeLinecap="round">
        <path d="M44 58q6-5 12 0" />
        <path d="M74 58q6-5 12 0" />
      </g>
    )
  }
  const lookDown = expression === 'search'
  const dy = lookDown ? 2 : 0
  return (
    <g>
      <circle cx="50" cy="56" r="1.9" fill={INK} transform={`translate(0 ${dy})`} />
      <circle cx="80" cy="56" r="1.9" fill={INK} transform={`translate(0 ${dy})`} />
    </g>
  )
}

function Props({ expression }) {
  switch (expression) {
    case 'welcome':
      return (
        <g>
          <path d="M30 60 L8 36 L20 34 L44 70 Z" fill={WING} />
          <path d="M8 36 L20 34 L14 44 Z" fill={GREEN} />
        </g>
      )
    case 'search':
      return (
        <g>
          <path d="M44 94 L65 88 L86 94 L86 114 L65 108 L44 114 Z" fill={IVORY} stroke={SLATE} strokeWidth="1" />
          <path d="M65 88 V108" stroke={SLATE} strokeWidth="1" />
          <rect x="76" y="88" width="3" height="10" fill={GREEN} />
        </g>
      )
    case 'results':
      return (
        <g>
          <path d="M92 74 L116 70 L118 100 L94 104 Z" fill={IVORY} stroke={SLATE} strokeWidth="1" />
          <rect x="104" y="74" width="3" height="8" fill={GREEN} />
        </g>
      )
    case 'error':
      return <path d="M82 92 L96 84 L98 92 Z" fill={GREEN} />
    default:
      return null
  }
}

export default function Folio({ expression = 'welcome', size = 120, className = '' }) {
  return (
    <svg
      className={`folio ${className}`}
      viewBox="0 0 130 140"
      width={size}
      height={(size * 140) / 130}
      role="presentation"
      aria-hidden="true"
      focusable="false"
    >
      {/* Alas */}
      {expression !== 'welcome' && <path d="M22 62 L34 56 L38 100 L26 108 Z" fill={WING} />}
      <path d="M108 62 L96 56 L92 100 L104 108 Z" fill={WING} />
      {/* Cuerpo */}
      <path
        d="M30 34 L40 22 L52 32 L78 32 L90 22 L100 34 L104 92 Q104 124 65 124 Q26 124 26 92 Z"
        fill={SLATE}
      />
      <path d="M26 92 Q26 124 65 124 Q104 124 104 92" fill={SLATE_DARK} opacity=".35" />
      {/* Rostro */}
      <path d="M32 50 Q34 40 48 40 L82 40 Q96 40 98 50 L96 66 Q65 84 34 66 Z" fill={FACE} />
      <g fill="none" stroke={SLATE} strokeWidth="1.4">
        <circle cx="50" cy="56" r="10" />
        <circle cx="80" cy="56" r="10" />
        <path d="M60 56 Q65 53 70 56" />
      </g>
      <Eyes expression={expression} />
      <path d="M61 66 L69 66 L65 73 Z" fill={BEAK} />
      {/* Pecho-documento */}
      {expression !== 'search' && (
        <g>
          <path d="M42 78 Q65 70 88 78 L90 114 L44 114 Z" fill={IVORY} />
          <path d="M80 114 L90 114 L90 104 Z" fill="#D8D3BF" />
        </g>
      )}
      {/* Patas */}
      <path d="M46 124 L56 124 L51 130 Z" fill={GREEN} />
      <path d="M74 124 L84 124 L79 130 Z" fill={GREEN} />
      <Props expression={expression} />
    </svg>
  )
}
