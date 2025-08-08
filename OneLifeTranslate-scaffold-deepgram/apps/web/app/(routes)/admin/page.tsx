import { createClient } from '@/lib/supabaseServer'
import { revalidatePath } from 'next/cache'

async function createService(data: FormData) {
  'use server'
  const supabase = createClient()
  const name = (data.get('name') as string)?.trim()
  if (!name) return
  await supabase.from('services').insert({ name })
  revalidatePath('/admin')
}

export default async function AdminPage() {
  const supabase = createClient()
  const { data } = await supabase.from('services').select('*').order('created_at', { ascending: false })

  return (
    <main className="p-4 space-y-6">
      <h1 className="text-xl font-semibold">Admin</h1>
      <form action={createService} className="flex gap-2">
        <input className="px-3 py-2 rounded bg-neutral-800 border border-neutral-700" name="name" placeholder="New service name" />
        <button className="px-3 py-2 rounded bg-sky-600">Create</button>
      </form>
      <ul className="space-y-2">
        {data?.map(svc => (
          <li key={svc.id} className="p-3 bg-neutral-900 rounded border border-neutral-800 flex items-center justify-between">
            <span>{svc.name}</span>
            <a className="text-sky-400 underline" href={`/listen/${svc.id}`}>Open listener</a>
          </li>
        ))}
      </ul>
    </main>
  )
}