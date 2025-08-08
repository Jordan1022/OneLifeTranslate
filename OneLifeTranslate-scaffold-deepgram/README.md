# OneLife Translate (Vercel + Supabase)

Mobile-first SPA for real-time English→Spanish captions + audio, built with:
- Next.js (App Router) as PWA
- Supabase (Postgres + Storage + Realtime via Postgres Changes)
- Managed ASR (Deepgram streaming)
- ElevenLabs TTS (Spanish voice)
- Glossary-first translation pipeline

## Quick start (local)

```bash
cd apps/web
npm i
npm run dev
```

### Env vars (apps/web/.env)
```
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE=
ELEVENLABS_API_KEY=
ELEVENLABS_VOICE_ID=
ASR_PROVIDER=deepgram
ASR_API_KEY=   # Server-side recommended; for MVP you can add NEXT_PUBLIC_DEEPGRAM_BROWSER_KEY to test
NEXT_PUBLIC_DEEPGRAM_BROWSER_KEY=
TRANSLATOR=none  # or openai
OPENAI_API_KEY=
```

## Supabase setup
1) Create bucket: `tts-segments` (Public)
2) Run `supabase/schema.sql` in SQL editor.
3) Database → Replication → Enable Realtime on `public.segments` (INSERT).

## Pages
- `/admin` – create service, list services
- `/broadcaster` – select Dante/USB input and go live
- `/listen/{serviceId}` – captions + audio queue (tap "Enable audio")
- `/lab` – glossary & latency tests

## Notes
- For production, DO NOT expose your Deepgram key in the browser. Mint a short-lived token via a server route and inject it at runtime.
- ElevenLabs is called per finalized segment via Edge function and stored in Supabase Storage with signed URLs.

## Testing
- Unit + component tests: Vitest + React Testing Library
- E2E: Playwright

Scripts:
- `npm run test` – run unit tests once
- `npm run test:watch` – watch mode
- `npm run e2e` – run Playwright tests (headed)
- `npm run e2e:ci` – run Playwright tests (headless)

## Contributing workflow (PR)
1) Create branch
```bash
git checkout -b scaffold/mvp
```
2) Add files from this ZIP
3) Commit & push
```bash
git add .
git commit -m "MVP scaffold with Deepgram ASR + sample glossary"
git push -u origin scaffold/mvp
```
4) Open PR on GitHub from `scaffold/mvp` → `main`.