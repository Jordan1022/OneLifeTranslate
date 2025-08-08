"use client"
import { createBrowserClient } from '@/lib/supabaseClient'
import { useEffect, useState } from 'react'
import { useAudioQueue } from './audio-client'

export default function ListenPage({ params }: { params: { serviceId: string }}) {
  const [segments, setSegments] = useState<any[]>([])
  const audio = useAudioQueue()

  useEffect(() => {
    const supabase = createBrowserClient()
    const channel = supabase.channel('segments')
      .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'segments', filter: `service_id=eq.${params.serviceId}` }, (payload) => {
        const seg = payload.new as any
        setSegments(prev => [seg, ...prev].slice(0, 20))
        if (seg.audio_url) audio.enqueue(seg.audio_url)
      })
      .subscribe()

    return () => { supabase.removeChannel(channel) }
  }, [params.serviceId, audio])

  return (
    <main className="p-4 space-y-4">
      <h1 className="text-xl font-semibold">Listen</h1>
      <div className="space-y-1">
        {segments.map(s => (
          <p key={s.id} className="text-lg">{s.text_translated || s.text_original}</p>
        ))}
      </div>
    </main>
  )
}