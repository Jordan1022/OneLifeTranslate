const SAMPLE_ENTRIES: Array<[string, string]> = [
  ['OR name', 'OneLife'],
]

export function applyGlossary(text: string): string {
  return SAMPLE_ENTRIES.reduce((acc, [from, to]) => acc.replaceAll(from, to), text)
}