// Core
import { useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'
// Hooks
import { AuthContext } from './useAuth'
import type { AuthContextValue } from './useAuth'
// Types
import type { User } from '../../types/user'

const STORAGE_KEY = 'bmp:user'

const readStored = (): User | null => {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? (JSON.parse(raw) as User) : null
  } catch {
    return null
  }
}

const defaultEmail = (name: string): string =>
  `${name.trim().toLowerCase().replace(/\s+/g, '.')}@example.com`

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(() => readStored())

  useEffect(() => {
    if (user) localStorage.setItem(STORAGE_KEY, JSON.stringify(user))
    else localStorage.removeItem(STORAGE_KEY)
  }, [user])

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      login: (name, email) =>
        setUser({ name: name.trim(), email: (email || defaultEmail(name)).trim() }),
      logout: () => setUser(null),
    }),
    [user],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
