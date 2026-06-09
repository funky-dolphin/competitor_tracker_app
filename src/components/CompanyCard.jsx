const COMPANY_COLORS = {
  OpenAI:     '#10b981',
  Anthropic:  '#f97316',
  Google:     '#4285f4',
  Microsoft:  '#00a4ef',
  Apple:      '#9ca3af',
  Perplexity: '#8b5cf6',
  Meta:       '#1877f2',
  Amazon:     '#ff9900',
}

const BADGE_LABELS = { hot: 'Hot', new: 'New', watch: 'Watch' }

export default function CompanyCard({ data }) {
  const { company, signals } = data
  const latest = signals[0]
  const rest   = signals.slice(1)
  const color  = COMPANY_COLORS[company] ?? '#6366f1'

  if (!latest) return null

  return (
    <article className="card" style={{ '--company-color': color }}>
      <div className="card-header">
        <span className="card-company">{company}</span>
        <span className={`badge badge--${latest.badge}`}>
          {BADGE_LABELS[latest.badge]}
        </span>
      </div>

      <h2 className="card-title">
        <a href={latest.url} target="_blank" rel="noopener noreferrer">
          {latest.title}
        </a>
      </h2>

      {latest.summary && (
        <p className="card-summary">{latest.summary}</p>
      )}

      <div className="card-footer">
        <span className="card-date">{latest.date}</span>
        <a
          href={latest.url}
          target="_blank"
          rel="noopener noreferrer"
          className="card-link"
        >
          Read &rarr;
        </a>
      </div>

      {rest.length > 0 && (
        <ul className="card-more">
          {rest.map((s, i) => (
            <li key={i}>
              <span className={`badge badge--${s.badge} badge--sm`}>
                {BADGE_LABELS[s.badge]}
              </span>
              <a href={s.url} target="_blank" rel="noopener noreferrer">
                {s.title}
              </a>
            </li>
          ))}
        </ul>
      )}
    </article>
  )
}
