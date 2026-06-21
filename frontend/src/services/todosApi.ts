// Services
import { apiClient, toQuery } from './apiClient'
// Types
import type { Priority, Todo, TodoPage, TodoQuery } from '../types/todo'

export interface CreateTodoInput {
  title: string
  description?: string
  priority?: Priority
  dueDate?: string | null
}

export const getTodos = (query: TodoQuery): Promise<TodoPage> => {
  const path = `/api/todos${toQuery({
    page: query.page,
    page_size: query.pageSize,
    search: query.search,
    completed: query.completed,
    priority: query.priority,
    sort_by: query.sortBy,
    order: query.order,
  })}`
  return apiClient.get<TodoPage>(path)
}

export const toggleTodo = (id: string): Promise<Todo> =>
  apiClient.post<Todo>(`/api/todos/${id}/toggle`)

export const createTodo = (input: CreateTodoInput): Promise<Todo> =>
  apiClient.post<Todo>('/api/todos', {
    title: input.title,
    description: input.description ?? '',
    priority: input.priority ?? 'medium',
    dueDate: input.dueDate ?? null,
  })
