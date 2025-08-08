import { NextResponse } from 'next/server'

export async function GET() {
  // For production, mint a server-side scoped token instead of exposing API key
  const key = process.env.ASR_API_KEY || process.env.NEXT_PUBLIC_DEEPGRAM_BROWSER_KEY
  if (!key) return NextResponse.json({ error: 'Missing ASR key' }, { status: 500 })
  // TODO: Exchange for a short-lived Deepgram token; for MVP we return the key directly if using browser key
  return NextResponse.json({ token: key })
}