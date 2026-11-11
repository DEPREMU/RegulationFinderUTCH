import ArticleCard from './ArticleCard.jsx'
import InfoNotice from './InfoNotice.jsx'

export default function Results({ articles }) {
  const documents = new Set(articles.map((article) => article.document)).size

  return (
    <section className="results" aria-labelledby="results-title">
      <div className="results__head">
        <div>
          <p className="eyebrow">
            {articles.length} {articles.length === 1 ? 'artículo' : 'artículos'} · {documents}{' '}
            {documents === 1 ? 'documento' : 'documentos'}
          </p>
          <h2 id="results-title" className="display display--medium">
            Resultados de búsqueda
          </h2>
        </div>
        <p className="results__note">Texto original · sin interpretaciones</p>
      </div>

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