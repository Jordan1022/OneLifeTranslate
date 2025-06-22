
# Real‑Time English→Spanish Translation Stream  
*(OneLife Church – v0.3 ‑ **Dante + Cloud STT/MT Edition**)*  

---

## 1. High‑Level Flow

```
Mixer Dante BUS ─► Dante LAN ─► **Translation PC** ─► OpenAI Whisper API ─► Glossary ─► GPT‑4o Mini (EN→ES) ─► ElevenLabs‑TTS ─► LL‑HLS ─► Client Page
                                      (Mac mini / NUC)                       (context helpers)                    (audio + captions)
```

---

## 2. Components & Choices

| Stage | Library / Service | Cost | Notes |
|-------|-------------------|------|-------|
| **Audio capture** | Dante Virtual Soundcard (DVS) + PortAudio/ALSA | **$49 one‑time** | Mixer routes AUX/Matrix on Dante; DVS appears as standard sound device. |
| **Speech‑to‑Text** | **OpenAI Whisper API** (`audio.transcriptions`) | **$0.006 / audio‑min** | 48 kHz WAV POST → JSON; ≈300 ms latency; no local models. |
| Glossary / context | Custom Python filter | Free | CSV glossary applied to English before translation. |
| **Machine Translation** | **OpenAI GPT‑4o Mini** (`chat.completions`) | **≈ $0.005 / 750 chars** | 120–180 ms latency; prompt includes glossary notes if needed. |
| **Text‑to‑Speech** | ElevenLabs Real‑Time v2 Streaming | $0.15 / 1 k chars | Voice “Lucía – Neutral LATAM”; ≈$35–46 / mo (4‑5 sermons). |
| Packager / Stream | `ffmpeg` → chunked‑CMAF LL‑HLS | Free | Glass‑to‑glass delay ≈2–3 s. |
| Backend API | FastAPI (Py 3.11) | Free | WebSocket in / HLS out / SSE captions. |
| Front‑end | Next.js + Tailwind (or Flutter Web) | Free | Auth gate + `<audio>` element + live captions pane. |
| Hosting / CDN | Cloudflare Free tier (orange‑cloud) | Free egress (< 100 GB / mo) | Origin = Translation PC; CDN caches `.m3u8` + `.m4s`. |

---

## 3. Directory Skeleton

```
onelife-translate/
├─ ingest/
│  ├─ audio_capture.py        # DVS input
│  └─ pcm_queue.py
├─ stt/
│  └─ whisper_api_worker.py   # OpenAI STT
├─ translate/
│  └─ gpt4o_worker.py         # EN→ES cloud MT
├─ tts/
│  └─ eleven_stream.py
├─ streamer/
│  ├─ hls_packager.py
│  └─ api.py                  # FastAPI routes + SSE
├─ frontend/
│  ├─ pages/
│  └─ components/
└─ PLAN.md
```

---

## 4. GPT‑4o Translation Worker Snippet

```python
# translate/gpt4o_worker.py
import os, queue, asyncio, openai

openai.api_key = os.getenv("OPENAI_API_KEY")
SYSTEM = "You are a fast, literal English→Spanish translator. Observe the glossary JSON if present."

async def translate_loop(en_q: "queue.Queue[str]", es_q: "queue.Queue[str]"):
    while True:
        text = en_q.get()
        resp = await openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"system","content": SYSTEM},
                      {"role":"user","content": text}],
            temperature=0,
            max_tokens=0,
            response_format={"type":"text"}
        )
        es_q.put(resp.choices[0].message.content.strip())
```

---

## 5. Environment / Deployment

```bash
# Prereqs
choco install ffmpeg            # or apt/brew
python -m venv venv && venv\Scripts\activate
pip install openai fastapi uvicorn[standard] websockets
# ElevenLabs helper
pip install elevenlabs
# Cloudflare tunnel if external access
```

```bash
export OPENAI_API_KEY="sk-..."       # Whisper + GPT‑4o
export ELEVEN_API_KEY="..."          # ElevenLabs
```

_No local model downloads required._

---

## 6. Latency & Sync Strategy

| Segment | Target (ms) |
|---------|-------------|
| Dante buffer | 1 |
| Whisper API | 300 |
| Glossary + GPT‑4o MT | 150 |
| ElevenLabs first‑byte | 200 |
| LL‑HLS buffer (2 parts) | 400 |
| **Total** | **≈1 100–3 100 ms** |

Spanish text arrives ≈2 s before its matching audio; we delay display via SSE timestamps so reading & listening align.

---

## 7. Glossary Format (`glossary.csv`)

```csv
en,es
Holy Spirit,Espíritu Santo
Lord's Supper,Cena del Señor
tithes & offerings,ofrendas y diezmos
```

---

## 8. MVP Checklist

- [ ] Dante flow (AUX → DVS) verified in **Dante Controller**.  
- [ ] FFmpeg captures 48 kHz mono without drop‑outs.  
- [ ] **Whisper API** returns transcript <400 ms.  
- [ ] **GPT‑4o Mini** translates chunk in <200 ms.  
- [ ] ElevenLabs streams Spanish audio.  
- [ ] HLS + captions play on mobile browsers.  
- [ ] Two‑service dry run before soft‑launch.  

---

## 9. Future Nice‑to‑Haves

- Moderator dashboard (“correct & re‑speak”).  
- Auto‑archive to bilingual subtitles + podcast.  
- Redundant Dante primary/secondary NICs.  

---

## 10. Captions Timing (Live Sync)

```ts
const audioStart = performance.now() / 1000;
evtSource.onmessage = (e) => {
  const { t, txt } = JSON.parse(e.data);
  const delay = (audioStart + t) - (performance.now() / 1000);
  setTimeout(() => appendCaption(txt), Math.max(0, delay * 1000));
};
```

---

### Contact / Ownership

| Role | Owner | Notes |
|------|-------|-------|
| Repo maintainer | Jordan @ Goodly Dev | merge rules, CI |
| Dante routing / clock | Sound team | mixer = clock leader |
| Glossary curation | Spanish ministry lead | PRs to `glossaries/` |

---

> **License** MIT for local code; comply with Audinate, OpenAI, ElevenLabs terms.
