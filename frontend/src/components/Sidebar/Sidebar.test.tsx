// Core
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it } from 'vitest'
// Components
import Sidebar from './Sidebar'

describe('Sidebar', () => {
  it('renders the navigation links', () => {
    render(
      <MemoryRouter>
        <Sidebar />
      </MemoryRouter>,
    )
    expect(screen.getByRole('link', { name: /todos/i })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /new task/i })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /business items/i })).toBeInTheDocument()
  })

  it('marks the link for the current route as active', () => {
    render(
      <MemoryRouter initialEntries={['/items']}>
        <Sidebar />
      </MemoryRouter>,
    )
    expect(screen.getByRole('link', { name: /business items/i })).toHaveClass(
      'sidebar__link--active',
    )
    expect(screen.getByRole('link', { name: /todos/i })).not.toHaveClass(
      'sidebar__link--active',
    )
  })
})
