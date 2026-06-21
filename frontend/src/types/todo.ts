// Types

export type Priority = 'low' | 'medium' | 'high'

export interface Todo {
  id: string
  title: string
  description: string
  completed: boolean
  priority: Priority
  dueDate: string | null
  createdAt: string
  updatedAt: string
}

export interface TodoPage {
  items: Todo[]
  total: number
  page: number
  pageSize: number
  totalPages: number
}

export interface TodoQuery {
  page: number
  pageSize: number
  search?: string
  completed?: boolean
  priority?: Priority
  sortBy?: string
  order?: 'asc' | 'desc'
}
