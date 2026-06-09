export default function TickerBar({ signals }) {
  if (!signals.length) return null

  const items = signals
    .map(s => `${s.company.toUpperCase()}  ${s.title}`)
    .join('   •   ')

  const content = items + '   •   ' + items

  return (
    <div className="ticker-wrapper" role="marquee" aria-label="Latest signals">
      <span className="ticker-label">LIVE</span>
      <div className="ticker-track">
        <span className="ticker-content">{content}</span>
      </div>
    </div>
  )
}
