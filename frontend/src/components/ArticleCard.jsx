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
      <header className="article__head">
        <div className="article__number-block">
          <span className="eyebrow">Artículo</span>
          <span className="article__number">{article.number}</span>
        </div>

        <div>
          <p className="article__result">
            Resultado {index + 1} · Texto original
          </p>
          <h3 className="article__document">{article.document}</h3>
          {article.topic && (
            <p className="eyebrow">{article.topic}</p>
          )}
        </div>
      </header>

      <p className="article__text">{shown}</p>

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

      <footer className="article__foot">
        <span>Texto original · Fuente documental</span>
        <span>{article.document}</span>
      </footer>
    </article>
  )
}