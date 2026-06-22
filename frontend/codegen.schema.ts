// Core
import type { CodegenConfig } from '@graphql-codegen/cli'

/**
 * Refreshes the committed `schema.graphql` SDL by introspecting a running
 * backend. Both backends expose the same contract:
 *   Django  -> http://localhost:8001/graphql
 *   FastAPI -> http://localhost:8002/graphql
 * Override with the `GRAPHQL_SCHEMA_URL` env variable. Run via `npm run schema:pull`.
 */
const config: CodegenConfig = {
  schema: process.env.GRAPHQL_SCHEMA_URL ?? 'http://localhost:8002/graphql',
  generates: {
    'schema.graphql': {
      plugins: ['schema-ast'],
    },
  },
}

export default config
