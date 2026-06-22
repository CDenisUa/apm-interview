/** Internal type. DO NOT USE DIRECTLY. */
type Exact<T extends { [key: string]: unknown }> = { [K in keyof T]: T[K] };
/** Internal type. DO NOT USE DIRECTLY. */
export type Incremental<T> = T | { [P in keyof T]?: P extends ' $fragmentName' | '__typename' ? T[P] : never };
import { gql } from '@apollo/client';
import * as Apollo from '@apollo/client';
export type Maybe<T> = T | null;
export type InputMaybe<T> = Maybe<T>;
const defaultOptions = {} as const;
/** All built-in and custom scalars, mapped to their actual values */
export type Scalars = {
  ID: { input: string; output: string; }
  String: { input: string; output: string; }
  Boolean: { input: boolean; output: boolean; }
  Int: { input: number; output: number; }
  Float: { input: number; output: number; }
};

/**
 * GraphQL schema for the Business Modernization Portal backend.
 *
 * Single contract shared by both backends (Django + FastAPI / strawberry).
 * This file is the source of truth for GraphQL Code Generator. Refresh it from a
 * running server with `npm run schema:pull` whenever the backend contract changes.
 */
export type BusinessItem = {
  __typename?: 'BusinessItem';
  country: Scalars['String']['output'];
  id: Scalars['ID']['output'];
  name: Scalars['String']['output'];
  owner: Scalars['String']['output'];
  revenue: Scalars['Float']['output'];
  status: Scalars['String']['output'];
  updatedAt: Scalars['String']['output'];
};

export type BusinessItemInput = {
  country: Scalars['String']['input'];
  name: Scalars['String']['input'];
  owner: Scalars['String']['input'];
  revenue: Scalars['Float']['input'];
  status: Scalars['String']['input'];
};

export type Mutation = {
  __typename?: 'Mutation';
  bulkDeleteTodos: Scalars['Int']['output'];
  clearCompleted: Scalars['Int']['output'];
  createItem: BusinessItem;
  createTodo: Todo;
  deleteItem: Scalars['Boolean']['output'];
  deleteTodo: Scalars['Boolean']['output'];
  markAll: Scalars['Int']['output'];
  toggleTodo?: Maybe<Todo>;
  updateItem?: Maybe<BusinessItem>;
  updateTodo?: Maybe<Todo>;
};


export type MutationBulkDeleteTodosArgs = {
  ids: Array<Scalars['ID']['input']>;
};


export type MutationCreateItemArgs = {
  input: BusinessItemInput;
};


export type MutationCreateTodoArgs = {
  input: TodoInput;
};


export type MutationDeleteItemArgs = {
  id: Scalars['ID']['input'];
};


export type MutationDeleteTodoArgs = {
  id: Scalars['ID']['input'];
};


export type MutationMarkAllArgs = {
  completed?: Scalars['Boolean']['input'];
};


export type MutationToggleTodoArgs = {
  id: Scalars['ID']['input'];
};


export type MutationUpdateItemArgs = {
  id: Scalars['ID']['input'];
  input: BusinessItemInput;
};


export type MutationUpdateTodoArgs = {
  id: Scalars['ID']['input'];
  input: TodoInput;
};

export type PriorityCounts = {
  __typename?: 'PriorityCounts';
  high: Scalars['Int']['output'];
  low: Scalars['Int']['output'];
  medium: Scalars['Int']['output'];
};

export type Query = {
  __typename?: 'Query';
  item?: Maybe<BusinessItem>;
  items: Array<BusinessItem>;
  todo?: Maybe<Todo>;
  todoStats: TodoStats;
  todos: TodoPage;
};


export type QueryItemArgs = {
  id: Scalars['ID']['input'];
};


export type QueryItemsArgs = {
  country?: InputMaybe<Scalars['String']['input']>;
  search?: InputMaybe<Scalars['String']['input']>;
  status?: InputMaybe<Scalars['String']['input']>;
};


export type QueryTodoArgs = {
  id: Scalars['ID']['input'];
};


export type QueryTodosArgs = {
  completed?: InputMaybe<Scalars['Boolean']['input']>;
  order?: Scalars['String']['input'];
  overdue?: InputMaybe<Scalars['Boolean']['input']>;
  page?: Scalars['Int']['input'];
  pageSize?: Scalars['Int']['input'];
  priority?: InputMaybe<Scalars['String']['input']>;
  search?: InputMaybe<Scalars['String']['input']>;
  sortBy?: Scalars['String']['input'];
};

export type Todo = {
  __typename?: 'Todo';
  completed: Scalars['Boolean']['output'];
  createdAt: Scalars['String']['output'];
  description: Scalars['String']['output'];
  dueDate?: Maybe<Scalars['String']['output']>;
  id: Scalars['ID']['output'];
  priority: Scalars['String']['output'];
  title: Scalars['String']['output'];
  updatedAt: Scalars['String']['output'];
};

export type TodoInput = {
  completed?: Scalars['Boolean']['input'];
  description?: Scalars['String']['input'];
  dueDate?: InputMaybe<Scalars['String']['input']>;
  priority?: Scalars['String']['input'];
  title: Scalars['String']['input'];
};

export type TodoPage = {
  __typename?: 'TodoPage';
  items: Array<Todo>;
  page: Scalars['Int']['output'];
  pageSize: Scalars['Int']['output'];
  total: Scalars['Int']['output'];
  totalPages: Scalars['Int']['output'];
};

export type TodoStats = {
  __typename?: 'TodoStats';
  active: Scalars['Int']['output'];
  byPriority: PriorityCounts;
  completed: Scalars['Int']['output'];
  overdue: Scalars['Int']['output'];
  total: Scalars['Int']['output'];
};

export type ItemsQueryVariables = Exact<{
  country?: string | null | undefined;
  status?: string | null | undefined;
  search?: string | null | undefined;
}>;


export type ItemsQuery = { items: Array<{ id: string, name: string, country: string, status: string, revenue: number, owner: string, updatedAt: string }> };

export type TodosQueryVariables = Exact<{
  page: number;
  pageSize: number;
  completed?: boolean | null | undefined;
  priority?: string | null | undefined;
  search?: string | null | undefined;
  sortBy: string;
  order: string;
}>;


export type TodosQuery = { todos: { total: number, page: number, pageSize: number, totalPages: number, items: Array<{ id: string, title: string, description: string, completed: boolean, priority: string, dueDate: string | null, createdAt: string, updatedAt: string }> } };

export type ToggleTodoMutationVariables = Exact<{
  id: string;
}>;


export type ToggleTodoMutation = { toggleTodo: { id: string, completed: boolean, updatedAt: string } | null };


export const ItemsDocument = gql`
    query Items($country: String, $status: String, $search: String) {
  items(country: $country, status: $status, search: $search) {
    id
    name
    country
    status
    revenue
    owner
    updatedAt
  }
}
    `;

/**
 * __useItemsQuery__
 *
 * To run a query within a React component, call `useItemsQuery` and pass it any options that fit your needs.
 * When your component renders, `useItemsQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useItemsQuery({
 *   variables: {
 *      country: // value for 'country'
 *      status: // value for 'status'
 *      search: // value for 'search'
 *   },
 * });
 */
export function useItemsQuery(baseOptions?: Apollo.QueryHookOptions<ItemsQuery, ItemsQueryVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<ItemsQuery, ItemsQueryVariables>(ItemsDocument, options);
      }
export function useItemsLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<ItemsQuery, ItemsQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<ItemsQuery, ItemsQueryVariables>(ItemsDocument, options);
        }
// @ts-ignore
export function useItemsSuspenseQuery(baseOptions?: Apollo.SuspenseQueryHookOptions<ItemsQuery, ItemsQueryVariables>): Apollo.UseSuspenseQueryResult<ItemsQuery, ItemsQueryVariables>;
export function useItemsSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<ItemsQuery, ItemsQueryVariables>): Apollo.UseSuspenseQueryResult<ItemsQuery | undefined, ItemsQueryVariables>;
export function useItemsSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<ItemsQuery, ItemsQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<ItemsQuery, ItemsQueryVariables>(ItemsDocument, options);
        }
export type ItemsQueryHookResult = ReturnType<typeof useItemsQuery>;
export type ItemsLazyQueryHookResult = ReturnType<typeof useItemsLazyQuery>;
export type ItemsSuspenseQueryHookResult = ReturnType<typeof useItemsSuspenseQuery>;
export type ItemsQueryResult = Apollo.QueryResult<ItemsQuery, ItemsQueryVariables>;
export const TodosDocument = gql`
    query Todos($page: Int!, $pageSize: Int!, $completed: Boolean, $priority: String, $search: String, $sortBy: String!, $order: String!) {
  todos(
    page: $page
    pageSize: $pageSize
    completed: $completed
    priority: $priority
    search: $search
    sortBy: $sortBy
    order: $order
  ) {
    items {
      id
      title
      description
      completed
      priority
      dueDate
      createdAt
      updatedAt
    }
    total
    page
    pageSize
    totalPages
  }
}
    `;

/**
 * __useTodosQuery__
 *
 * To run a query within a React component, call `useTodosQuery` and pass it any options that fit your needs.
 * When your component renders, `useTodosQuery` returns an object from Apollo Client that contains loading, error, and data properties
 * you can use to render your UI.
 *
 * @param baseOptions options that will be passed into the query, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options;
 *
 * @example
 * const { data, loading, error } = useTodosQuery({
 *   variables: {
 *      page: // value for 'page'
 *      pageSize: // value for 'pageSize'
 *      completed: // value for 'completed'
 *      priority: // value for 'priority'
 *      search: // value for 'search'
 *      sortBy: // value for 'sortBy'
 *      order: // value for 'order'
 *   },
 * });
 */
export function useTodosQuery(baseOptions: Apollo.QueryHookOptions<TodosQuery, TodosQueryVariables> & ({ variables: TodosQueryVariables; skip?: boolean; } | { skip: boolean; }) ) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useQuery<TodosQuery, TodosQueryVariables>(TodosDocument, options);
      }
export function useTodosLazyQuery(baseOptions?: Apollo.LazyQueryHookOptions<TodosQuery, TodosQueryVariables>) {
          const options = {...defaultOptions, ...baseOptions}
          return Apollo.useLazyQuery<TodosQuery, TodosQueryVariables>(TodosDocument, options);
        }
// @ts-ignore
export function useTodosSuspenseQuery(baseOptions?: Apollo.SuspenseQueryHookOptions<TodosQuery, TodosQueryVariables>): Apollo.UseSuspenseQueryResult<TodosQuery, TodosQueryVariables>;
export function useTodosSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<TodosQuery, TodosQueryVariables>): Apollo.UseSuspenseQueryResult<TodosQuery | undefined, TodosQueryVariables>;
export function useTodosSuspenseQuery(baseOptions?: Apollo.SkipToken | Apollo.SuspenseQueryHookOptions<TodosQuery, TodosQueryVariables>) {
          const options = baseOptions === Apollo.skipToken ? baseOptions : {...defaultOptions, ...baseOptions}
          return Apollo.useSuspenseQuery<TodosQuery, TodosQueryVariables>(TodosDocument, options);
        }
export type TodosQueryHookResult = ReturnType<typeof useTodosQuery>;
export type TodosLazyQueryHookResult = ReturnType<typeof useTodosLazyQuery>;
export type TodosSuspenseQueryHookResult = ReturnType<typeof useTodosSuspenseQuery>;
export type TodosQueryResult = Apollo.QueryResult<TodosQuery, TodosQueryVariables>;
export const ToggleTodoDocument = gql`
    mutation ToggleTodo($id: ID!) {
  toggleTodo(id: $id) {
    id
    completed
    updatedAt
  }
}
    `;
export type ToggleTodoMutationFn = Apollo.MutationFunction<ToggleTodoMutation, ToggleTodoMutationVariables>;

/**
 * __useToggleTodoMutation__
 *
 * To run a mutation, you first call `useToggleTodoMutation` within a React component and pass it any options that fit your needs.
 * When your component renders, `useToggleTodoMutation` returns a tuple that includes:
 * - A mutate function that you can call at any time to execute the mutation
 * - An object with fields that represent the current status of the mutation's execution
 *
 * @param baseOptions options that will be passed into the mutation, supported options are listed on: https://www.apollographql.com/docs/react/api/react-hooks/#options-2;
 *
 * @example
 * const [toggleTodoMutation, { data, loading, error }] = useToggleTodoMutation({
 *   variables: {
 *      id: // value for 'id'
 *   },
 * });
 */
export function useToggleTodoMutation(baseOptions?: Apollo.MutationHookOptions<ToggleTodoMutation, ToggleTodoMutationVariables>) {
        const options = {...defaultOptions, ...baseOptions}
        return Apollo.useMutation<ToggleTodoMutation, ToggleTodoMutationVariables>(ToggleTodoDocument, options);
      }
export type ToggleTodoMutationHookResult = ReturnType<typeof useToggleTodoMutation>;
export type ToggleTodoMutationResult = Apollo.MutationResult<ToggleTodoMutation>;
export type ToggleTodoMutationOptions = Apollo.BaseMutationOptions<ToggleTodoMutation, ToggleTodoMutationVariables>;