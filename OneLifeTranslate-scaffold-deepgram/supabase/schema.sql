-- Public schema for caption segments and services
create table if not exists public.services (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  created_at timestamptz not null default now()
);

create table if not exists public.segments (
  id uuid primary key default gen_random_uuid(),
  service_id uuid not null references public.services(id) on delete cascade,
  lang_from text not null default 'en',
  lang_to text not null default 'es',
  is_final boolean not null default false,
  text_original text not null,
  text_translated text,
  audio_url text,
  started_at timestamptz not null default now(),
  finalized_at timestamptz
);

-- Helpful index for realtime listeners per service
create index if not exists idx_segments_service_created on public.segments(service_id, started_at desc);

-- Storage bucket: create manually via dashboard as README says: tts-segments (Public)