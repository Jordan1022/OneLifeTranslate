# Database Setup

## Enable pgcrypto Extension (required)

The project relies on PostgreSQL's `pgcrypto` extension for generating UUIDs and other cryptographic helpers (e.g. `gen_random_uuid()`). Make sure it is enabled in **all** environments (local, dev, staging, prod).

```sql
-- connect to the database first, then run:
create extension if not exists pgcrypto;
```

If you are using Supabase locally, you can apply the migration in the `supabase/migrations` directory or execute it manually:

```bash
psql "$SUPABASE_DB_URL" -c "create extension if not exists pgcrypto;"
```

After enabling the extension, verify that it works:

```sql
select gen_random_uuid(); -- should return a UUID value
```

> Important: Avoid enabling unnecessary extensions or any features that require superuser privileges on managed Supabase Postgres instances.