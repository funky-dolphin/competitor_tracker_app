const FILTERS = [
  { value: 'all',   label: 'All' },
  { value: 'hot',   label: 'Hot' },
  { value: 'new',   label: 'New' },
  { value: 'watch', label: 'Watch' },
]

export default function FilterBar({ filter, setFilter }) {
  return (
    <div className="filter-bar" role="group" aria-label="Filter signals">
      {FILTERS.map(({ value, label }) => (
        <button
          key={value}
          className={`filter-btn filter-btn--${value}${filter === value ? ' active' : ''}`}
          onClick={() => setFilter(value)}
          aria-pressed={filter === value}
        >
          {label}
        </button>
      ))}
    </div>
  )
}
