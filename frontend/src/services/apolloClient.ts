// Core
import { ApolloClient, HttpLink, InMemoryCache } from '@apollo/client'
// Consts
import { API_BASE_URL } from '../consts/api'

/** Apollo Client pointed at the backend's GraphQL endpoint (Django or FastAPI). */
export const apolloClient = new ApolloClient({
  link: new HttpLink({ uri: `${API_BASE_URL}/graphql` }),
  cache: new InMemoryCache(),
})
