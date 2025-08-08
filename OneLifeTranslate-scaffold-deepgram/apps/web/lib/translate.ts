import { applyGlossary } from './glossary'

export async function translateText(text: string): Promise<string> {
  const mode = process.env.TRANSLATOR || 'none'
  const pre = applyGlossary(text)
  if (mode === 'openai') {
    const { OpenAI } = await import('openai')
    const client = new OpenAI({ apiKey: process.env.OPENAI_API_KEY })
    const resp = await client.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: [
        { role: 'system', content: 'You are a concise English→Spanish translator.' },
        { role: 'user', content: pre }
      ],
      temperature: 0.2,
    })
    const out = resp.choices[0]?.message?.content?.trim()
    return out || pre
  }
  return pre
}