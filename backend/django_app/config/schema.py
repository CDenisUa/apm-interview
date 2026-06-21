"""Root GraphQL schema — merges the items and todos modules into one."""
# Core
import strawberry
from strawberry.tools import merge_types
# Local
from items.graphql import Query as ItemsQuery, Mutation as ItemsMutation
from todos.graphql import TodoQuery, TodoMutation

Query = merge_types("Query", (ItemsQuery, TodoQuery))
Mutation = merge_types("Mutation", (ItemsMutation, TodoMutation))

schema = strawberry.Schema(query=Query, mutation=Mutation)
