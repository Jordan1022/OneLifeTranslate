import { createClient } from './supabaseServer'

export async function synthesizeAndStore(serviceId: string, text: string): Promise<string | null> {
  const supabase = createClient()
  const apiKey = process.env.ELEVENLABS_API_KEY
  const voiceId = process.env.ELEVENLABS_VOICE_ID
  if (!apiKey || !voiceId) return null

  const resp = await fetch(`https://api.elevenlabs.io/v1/text-to-speech/${voiceId}`, {
    method: 'POST',
    headers: {
      'xi-api-key': apiKey,
      'content-type': 'application/json'
    },
    body: JSON.stringify({ text })
  })
  if (!resp.ok) return null
  const arrayBuffer = await resp.arrayBuffer()
  const filePath = `${serviceId}/${Date.now()}.mp3`
  const { error } = await supabase.storage.from('tts-segments').upload(filePath, arrayBuffer, { contentType: 'audio/mpeg', upsert: true })
  if (error) return null
  const { data } = await supabase.storage.from('tts-segments').createSignedUrl(filePath, 60 * 60)
  return data?.signedUrl ?? null
}