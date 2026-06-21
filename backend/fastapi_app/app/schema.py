"""Root GraphQL schema — merges the items and todos modules into one."""
# Core
import strawberry
from strawberry.tools import merge_types
# Local
from .graphql_schema import Query as ItemsQuery, Mutation as ItemsMutation
from .todo_graphql import TodoQuery, TodoMutation

Query = merge_types("Query", (ItemsQuery, TodoQuery))
Mutation = merge_types("Mutation", (ItemsMutation, TodoMutation))

schema = strawberry.Schema(query=Query, mutation=Mutation)
