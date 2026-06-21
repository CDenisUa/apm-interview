// Core
import { useCallback, useEffect, useState } from 'react'
// Services
import { getTodos } from '../../services/todosApi'
// Types
import type { TodoPage, TodoQuery } from '../../types/todo'

interface State {
  data: TodoPage | null
  loading: boolean
  error: string | null
}

export const useTodos = (query: TodoQuery) => {
  const [state, setState] = useState<State>({ data: null, loading: true, error: null })
  const [reloadKey, setReloadKey] = useState(0)

  useEffect(() => {
    let cancelled = false
    const run = async () => {
      setState((s) => ({ ...s, loading: true, error: null }))
      try {
        const data = await getTodos(query)
        if (!cancelled) setState({ data, loading: false, error: null })
      } catch (err: unknown) {
        if (!cancelled)
          setState({ data: null, loading: false, error: err instanceof Error ? err.message : 'Error' })
      }
    }
    void run()
    return () => {
      cancelled = true
    }
  }, [query, reloadKey])

  const refetch = useCallback(() => setReloadKey((k) => k + 1), [])
  return { ...state, refetch }
}
