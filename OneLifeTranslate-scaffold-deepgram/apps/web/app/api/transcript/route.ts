import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@/lib/supabaseServer'
import { translateText } from '@/lib/translate'
import { synthesizeAndStore } from '@/lib/tts'

export async function POST(req: NextRequest) {
  const body = await req.json()
  const { serviceId, text, isFinal, langFrom = 'en', langTo = 'es' } = body || {}
  if (!serviceId || !text) return NextResponse.json({ error: 'Missing serviceId or text' }, { status: 400 })

  const translated = await translateText(text)
  const supabase = createClient()
  let audioUrl: string | null = null
  if (isFinal) {
    audioUrl = await synthesizeAndStore(serviceId, translated)
  }
  const { data, error } = await supabase.from('segments').insert({
    service_id: serviceId,
    lang_from: langFrom,
    lang_to: langTo,
    is_final: !!isFinal,
    text_original: text,
    text_translated: translated,
    audio_url: audioUrl
  }).select('*').single()
  if (error) return NextResponse.json({ error: error.message }, { status: 500 })
  return NextResponse.json({ segment: data })
}