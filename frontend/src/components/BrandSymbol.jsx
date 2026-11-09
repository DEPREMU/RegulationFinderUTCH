import logo from '../assets/logo.svg'

export default function BrandSymbol({ size = 30 }) {
  return (
    <img
      src={logo}
      alt="Regulation Finder"
      style={{
        height: size,
        width: 'auto',
        display: 'block',
        objectFit: 'contain',
      }}
    />
  )
}
