// Consts

/**
 * Base URL of the backend the app talks to.
 *
 * Both backends expose an identical REST + GraphQL contract, so this is the
 * only place that needs to change to switch between them:
 *   Django  -> http://localhost:8001
 *   FastAPI -> http://localhost:8002
 *
 * Override at build/run time via the `VITE_API_BASE_URL` env variable.
 */
export const API_BASE_URL: string =
  import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8001'
