export default function LatencyBadge({ ms }: { ms?: number }) {
  const color = ms == null ? 'bg-neutral-700' : ms < 800 ? 'bg-emerald-600' : ms < 1500 ? 'bg-amber-600' : 'bg-rose-600'
  return (
    <span className={`inline-flex items-center px-2 py-1 rounded text-xs ${color}`}>
      {ms == null ? '—' : `${Math.round(ms)} ms`}
    </span>
  )
}