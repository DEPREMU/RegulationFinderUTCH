import BrandSymbol from './BrandSymbol.jsx'
import bisLogo from '../assets/logoBis.svg'
import utchLogo from '../assets/Logotipo_UTCH.png'

export default function Header() {
  return (
    <header className="header">
      <div className="header__brand">
        <BrandSymbol size={30} />
        <div>
          <p className="header__name">Regulation Finder</p>
          <p className="header__tagline">Sistema de búsqueda documental</p>
        </div>
      </div>

      <div className="header__utch">
        <img className="header__logo-bis" src={bisLogo} alt="BIS" />
        <img className="header__logo-utch" src={utchLogo} alt="Universidad Tecnológica de Chihuahua" />
      </div>
    </header>
  )
}