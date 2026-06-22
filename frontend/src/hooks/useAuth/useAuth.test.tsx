// Core
import { act, renderHook } from '@testing-library/react'
import type { ReactNode } from 'react'
import { beforeEach, describe, expect, it } from 'vitest'
// Hooks
import { AuthProvider } from './AuthProvider'
import { useAuth } from './useAuth'
// Consts
import { STORAGE_KEYS } from '../../consts/storage'

const wrapper = ({ children }: { children: ReactNode }) => <AuthProvider>{children}</AuthProvider>

beforeEach(() => localStorage.clear())

describe('useAuth', () => {
  it('starts signed out', () => {
    const { result } = renderHook(() => useAuth(), { wrapper })
    expect(result.current.user).toBeNull()
  })

  it('logs in, derives an email from the name, and persists it', () => {
    const { result } = renderHook(() => useAuth(), { wrapper })
    act(() => result.current.login('Denys Chepiha'))

    expect(result.current.user).toEqual({
      name: 'Denys Chepiha',
      email: 'denys.chepiha@example.com',
    })
    expect(localStorage.getItem(STORAGE_KEYS.user)).toContain('Denys Chepiha')
  })

  it('logs out and clears storage', () => {
    const { result } = renderHook(() => useAuth(), { wrapper })
    act(() => result.current.login('Anna'))
    act(() => result.current.logout())

    expect(result.current.user).toBeNull()
    expect(localStorage.getItem(STORAGE_KEYS.user)).toBeNull()
  })

  it('restores a persisted user on mount', () => {
    localStorage.setItem(STORAGE_KEYS.user, JSON.stringify({ name: 'Saved', email: 's@e.com' }))
    const { result } = renderHook(() => useAuth(), { wrapper })
    expect(result.current.user?.name).toBe('Saved')
  })
})
