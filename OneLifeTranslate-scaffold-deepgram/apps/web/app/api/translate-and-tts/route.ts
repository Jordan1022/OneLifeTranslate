import { NextRequest, NextResponse } from 'next/server'
import { translateText } from '@/lib/translate'
import { synthesizeAndStore } from '@/lib/tts'

export async function POST(req: NextRequest) {
  const { serviceId, text } = await req.json()
  if (!serviceId || !text) return NextResponse.json({ error: 'Missing serviceId or text' }, { status: 400 })
  const translated = await translateText(text)
  const url = await synthesizeAndStore(serviceId, translated)
  return NextResponse.json({ translated, url })
}