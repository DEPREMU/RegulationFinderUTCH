import { useState } from 'react'

const COLLAPSE_AT = 190

export default function ArticleCard({ article, index }) {
  const [expanded, setExpanded] = useState(false)
  const isLong = article.text.length > COLLAPSE_AT
  const collapsed = isLong && !expanded
  const shown = collapsed
    ? `${article.text.slice(0, COLLAPSE_AT).trimEnd()}…`
    : article.text

  return (
    <article className="article" style={{ '--i': index }}>
      <div className="article__side">
        <span className="article__label">Artículo</span>
        <span className="article__number">{article.number}</span>
        <span className="article__result">Resultado {index + 1}</span>
      </div>

      <div className="article__main">
        {article.topic && <h3 className="article__topic">{article.topic}</h3>}

        <div className="article__body">
          <p className="eyebrow eyebrow--muted">Texto original</p>
          <p className="article__text">{shown}</p>
        </div>

        <footer className="article__foot">
          <span className="article__source">Fuente: {article.document}</span>
          {isLong && (
            <button
              type="button"
              className="article__toggle"
              onClick={() => setExpanded((value) => !value)}
              aria-expanded={expanded}
            >
              {expanded ? 'Contraer artículo' : 'Leer artículo completo'}
              <span aria-hidden="true">{expanded ? ' ⌃' : ' ⌄'}</span>
            </button>
          )}
        </footer>
      </div>
    </article>
  )
}