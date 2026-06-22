// Core
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
// Components
import TodoList from './TodoList'
// Types
import type { Todo } from '../../types/todo'

const makeTodo = (over: Partial<Todo> = {}): Todo => ({
  id: '1',
  title: 'Task A',
  description: 'a description',
  completed: false,
  priority: 'high',
  dueDate: null,
  createdAt: '',
  updatedAt: '',
  ...over,
})

describe('TodoList', () => {
  it('shows an empty state when there are no todos', () => {
    render(<TodoList todos={[]} onToggle={() => {}} busyId={null} />)
    expect(screen.getByText(/no todos/i)).toBeInTheDocument()
  })

  it('renders a row with title and priority', () => {
    render(<TodoList todos={[makeTodo()]} onToggle={() => {}} busyId={null} />)
    expect(screen.getByText('Task A')).toBeInTheDocument()
    expect(screen.getByText('High')).toBeInTheDocument()
  })

  it('calls onToggle with the todo id when the checkbox is clicked', async () => {
    const onToggle = vi.fn()
    const user = userEvent.setup()
    render(<TodoList todos={[makeTodo({ id: 'x1' })]} onToggle={onToggle} busyId={null} />)

    await user.click(screen.getByRole('button', { name: /mark as completed/i }))
    expect(onToggle).toHaveBeenCalledWith('x1')
  })

  it('disables the checkbox for the busy todo', () => {
    render(<TodoList todos={[makeTodo({ id: 'x1' })]} onToggle={() => {}} busyId="x1" />)
    expect(screen.getByRole('button', { name: /mark as completed/i })).toBeDisabled()
  })
})
