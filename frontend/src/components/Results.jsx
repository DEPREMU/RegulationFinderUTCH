import ArticleCard from './ArticleCard.jsx'
import BrandSymbol from './BrandSymbol.jsx'
import Folio from './Folio.jsx'
import InfoNotice from './InfoNotice.jsx'

export default function Results({ articles }) {
  const documents = new Set(articles.map((article) => article.document)).size

  return (
    <section className="results" aria-labelledby="results-title">
      <div className="results__top">
        <div className="results__signature">
          <BrandSymbol size={24} />
          <div>
            <p className="results__sig-name">Regulation Finder</p>
            <p className="results__sig-tag">Sistema de búsqueda documental</p>
          </div>
        </div>
        <Folio expression="results" size={64} />
      </div>

      <p className="eyebrow">
        {articles.length} {articles.length === 1 ? 'artículo' : 'artículos'} / {documents}{' '}
        {documents === 1 ? 'documento' : 'documentos'}
      </p>
      <h2 id="results-title" className="display">
        Resultados de búsqueda
      </h2>
      <p className="lead lead--small">Artículos recuperados para tu consulta. Sin resúmenes ni interpretaciones.</p>

      <InfoNotice />

      <div className="results__list">
        {articles.map((article, index) => (
          <ArticleCard key={`${article.document}-${article.number}`} article={article} index={index} />
        ))}
      </div>

      <p className="results__end">Fin de los resultados · Puedes hacer una nueva consulta.</p>
    </section>
  )
}
