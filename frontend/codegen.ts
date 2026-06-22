// Core
import type { CodegenConfig } from '@graphql-codegen/cli'

/**
 * Generates fully-typed Apollo hooks (useItemsQuery, useToggleTodoMutation, …)
 * from the committed SDL in `schema.graphql` and the `.graphql` operations
 * under `src/graphql`. Output: a single file at `src/gql/generated.ts`.
 *
 * Run `npm run codegen` after editing any operation; `npm run schema:pull`
 * refreshes `schema.graphql` from a running backend.
 */
const config: CodegenConfig = {
  schema: './schema.graphql',
  documents: 'src/**/*.graphql',
  ignoreNoDocuments: true,
  generates: {
    'src/gql/generated.ts': {
      plugins: [
        'typescript',
        'typescript-operations',
        'typescript-react-apollo',
      ],
      config: {
        withHooks: true,
        reactApolloVersion: 3,
        scalars: { ID: 'string' },
      },
    },
  },
}

export default config
