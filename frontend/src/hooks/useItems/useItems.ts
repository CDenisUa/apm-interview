// Core
import { useEffect, useState } from 'react'
// Services
import { getItems } from '../../services/itemsApi'
import type { ItemsQuery } from '../../services/itemsApi'
// Types
import type { BusinessItem } from '../../types/item'

interface State {
  data: BusinessItem[] | null
  loading: boolean
  error: string | null
}

export const useItems = (query: ItemsQuery) => {
  const [state, setState] = useState<State>({ data: null, loading: true, error: null })

  useEffect(() => {
    let cancelled = false
    const run = async () => {
      setState((s) => ({ ...s, loading: true, error: null }))
      try {
        const data = await getItems(query)
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
  }, [query])

  return state
}
