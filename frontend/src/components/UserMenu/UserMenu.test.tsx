// Core
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it } from 'vitest'
// Components
import UserMenu from './UserMenu'
// Hooks
import { AuthProvider } from '../../hooks/useAuth/AuthProvider'

const renderMenu = () =>
  render(
    <AuthProvider>
      <UserMenu />
    </AuthProvider>,
  )

const signIn = async (user: ReturnType<typeof userEvent.setup>, name: string) => {
  await user.click(screen.getByRole('button', { name: /sign in/i }))
  await user.type(screen.getByPlaceholderText(/your name/i), name)
  await user.click(screen.getByRole('button', { name: /continue/i }))
}

beforeEach(() => localStorage.clear())

describe('UserMenu', () => {
  it('shows a Sign in button when signed out', () => {
    renderMenu()
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument()
  })

  it('signs in by name and shows the user', async () => {
    const user = userEvent.setup()
    renderMenu()
    await signIn(user, 'Denys')
    expect(screen.getByText('Denys')).toBeInTheDocument()
  })

  it('signs out and returns to the Sign in button', async () => {
    const user = userEvent.setup()
    renderMenu()
    await signIn(user, 'Denys')
    await user.click(screen.getByRole('button', { name: /denys/i }))
    await user.click(screen.getByRole('button', { name: /sign out/i }))
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument()
  })
})
