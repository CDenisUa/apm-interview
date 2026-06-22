// Core
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
// Components
import TodosPage from './TodosPage'
// Hooks
import { AuthProvider } from '../../hooks/useAuth/AuthProvider'
// Services
import * as todosApi from '../../services/todosApi'
// Types
import type { TodoPage } from '../../types/todo'

vi.mock('../../services/todosApi')

const makePage = (over: Partial<TodoPage> = {}): TodoPage => ({
  items: [
    {
      id: '1',
      title: 'Task A',
      description: '',
      completed: false,
      priority: 'high',
      dueDate: null,
      createdAt: '',
      updatedAt: '',
    },
  ],
  total: 1,
  page: 1,
  pageSize: 10,
  totalPages: 1,
  ...over,
})

const renderPage = () =>
  render(
    <AuthProvider>
      <TodosPage />
    </AuthProvider>,
  )

beforeEach(() => {
  localStorage.clear()
  vi.mocked(todosApi.getTodos).mockResolvedValue(makePage())
  vi.mocked(todosApi.toggleTodo).mockResolvedValue({} as never)
})

describe('TodosPage', () => {
  it('loads and renders todos from the API', async () => {
    renderPage()
    expect(await screen.findByText('Task A')).toBeInTheDocument()
    expect(screen.getByText(/1 items/i)).toBeInTheDocument()
  })

  it('refetches with the debounced search term', async () => {
    const user = userEvent.setup()
    renderPage()
    await screen.findByText('Task A')

    await user.type(screen.getByPlaceholderText(/search/i), 'report')
    await waitFor(() => {
      const searched = vi.mocked(todosApi.getTodos).mock.calls.some(
        ([q]) => q.search === 'report',
      )
      expect(searched).toBe(true)
    })
  })

  it('toggles a todo and refetches', async () => {
    const user = userEvent.setup()
    renderPage()
    await screen.findByText('Task A')

    await user.click(screen.getByRole('button', { name: /mark as completed/i }))
    await waitFor(() => expect(vi.mocked(todosApi.toggleTodo)).toHaveBeenCalledWith('1'))
  })
})
