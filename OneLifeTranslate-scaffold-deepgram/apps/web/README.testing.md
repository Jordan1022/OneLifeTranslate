# Testing

This app includes unit/component tests (Vitest + RTL) and E2E (Playwright).

## Setup
```bash
npm i
npx playwright install --with-deps
```

## Commands
- `npm run test` – unit tests
- `npm run e2e` – E2E (headed)

## Notes
- JS DOM environment is configured via Vitest.
- Add E2E specs under `tests/e2e`.