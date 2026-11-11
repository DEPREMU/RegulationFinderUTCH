export default function BrandSymbol({ size = 30 }) {
  return (
    <svg
      viewBox="0 0 64 64"
      width={size}
      height={size}
      role="img"
      aria-label="Regulation Finder"
      style={{ display: 'block', flexShrink: 0 }}
    >
      {/* Cuadro verde */}
      <rect width="64" height="64" rx="15" fill="#245d43" />
      {/* Muesca superior */}
      <path
        d="M28 12 L31.5 16 L35 12"
        fill="none"
        stroke="#fffdf8"
        strokeWidth="2.2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      {/* Ojo izquierdo */}
      <circle cx="21" cy="28" r="8.5" fill="#fffdf8" />
      <circle cx="21" cy="28" r="5.2" fill="#245d43" />
      <circle cx="21" cy="28" r="2.6" fill="#fffdf8" />
      {/* Ojo derecho con lupa */}
      <circle cx="40" cy="28" r="8.5" fill="#fffdf8" />
      <circle cx="40" cy="28" r="5.2" fill="#245d43" />
      <circle cx="40" cy="28" r="3.6" fill="#42b6a5" />
      <path d="M46 34 L53 41" stroke="#42b6a5" strokeWidth="3" strokeLinecap="round" />
      {/* Barra inferior */}
      <rect x="16" y="46" width="31" height="3.2" rx="1.6" fill="#bccbc4" />
    </svg>
  )
}