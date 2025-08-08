import Link from 'next/link'

export default function Home() {
  return (
    <main className="p-6 space-y-4">
      <h1 className="text-2xl font-semibold">OneLife Translate</h1>
      <p className="text-neutral-300">Real-time English → Spanish captions and audio.</p>
      <ul className="list-disc list-inside space-y-2">
        <li><Link className="text-sky-400 underline" href="/admin">Admin</Link></li>
        <li><Link className="text-sky-400 underline" href="/broadcaster">Broadcaster</Link></li>
        <li><Link className="text-sky-400 underline" href="/lab">Lab</Link></li>
      </ul>
    </main>
  )
}