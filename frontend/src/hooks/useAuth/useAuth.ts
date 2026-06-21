// Core
import { createContext, useContext } from 'react'
// Types
import type { User } from '../../types/user'

export interface AuthContextValue {
  user: User | null
  login: (name: string, email?: string) => void
  logout: () => void
}

export const AuthContext = createContext<AuthContextValue | null>(null)

export const useAuth = (): AuthContextValue => {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within <AuthProvider>')
  return ctx
}
