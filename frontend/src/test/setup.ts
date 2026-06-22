// Extends `expect` with DOM matchers (toBeInTheDocument, etc.) for every test.
import '@testing-library/jest-dom'
// Initialise the shared i18n instance so `useTranslation` resolves real
// (English) strings instead of raw keys when components render under test.
import '../i18n/i18n'

// jsdom under Vitest can expose a partial localStorage (missing clear()).
// Install a complete in-memory implementation so storage-backed code is testable.
const createMemoryStorage = (): Storage => {
  const store = new Map<string, string>()
  return {
    get length() {
      return store.size
    },
    clear: () => store.clear(),
    getItem: (key: string) => (store.has(key) ? store.get(key)! : null),
    key: (index: number) => Array.from(store.keys())[index] ?? null,
    removeItem: (key: string) => {
      store.delete(key)
    },
    setItem: (key: string, value: string) => {
      store.set(key, String(value))
    },
  } as Storage
}

Object.defineProperty(globalThis, 'localStorage', {
  value: createMemoryStorage(),
  configurable: true,
  writable: true,
})
