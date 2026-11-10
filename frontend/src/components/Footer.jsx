import BrandSymbol from './BrandSymbol.jsx'
import bisLogo from '../assets/logoBis.svg'
import utchLogo from '../assets/Logotipo_UTCH.png'

export default function Footer() {
  return (
    <footer className="footer">
      <div className="footer__brand">
        <BrandSymbol size={24} />
        <div>
          <p className="footer__name">Regulation Finder</p>
          <p className="footer__tagline">Universidad Tecnológica de Chihuahua · BIS</p>
        </div>
      </div>

      <div className="footer__side">
        <p className="footer__legal">
          Información orientativa, no oficial. Recupera artículos originales; no genera ni interpreta respuestas.
        </p>
        <div className="footer__logos">
          <img className="footer__logo-bis" src={bisLogo} alt="BIS" />
          <img className="footer__logo-utch" src={utchLogo} alt="Universidad Tecnológica de Chihuahua" />
        </div>
      </div>
    </footer>
  )
}