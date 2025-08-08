export default function CaptionRail({ lines }: { lines: string[] }) {
  return (
    <div className="space-y-1">
      {lines.map((line, i) => (
        <p key={i} className="text-xl leading-tight">{line}</p>
      ))}
    </div>
  )
}