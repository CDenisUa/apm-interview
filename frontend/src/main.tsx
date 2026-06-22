// Core
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
// Components
import App from './App.tsx'
// Services
import i18n from './i18n/i18n'
// Styles
import './index.css'
// Consts
import { STORAGE_KEYS } from './consts/storage'

const syncDocumentTitle = () => {
  document.title = i18n.t('app.title')
  document.documentElement.lang = i18n.language
}

syncDocumentTitle()
i18n.on('languageChanged', syncDocumentTitle)

const clearLegacyBrowserCache = async () => {
  try {
    if (localStorage.getItem(STORAGE_KEYS.legacyCacheCleared)) return

    const hadServiceWorkerController = Boolean(navigator.serviceWorker?.controller)
    const registrations = navigator.serviceWorker
      ? await navigator.serviceWorker.getRegistrations()
      : []
    const cacheNames = 'caches' in window ? await caches.keys() : []

    await Promise.all([
      ...registrations.map((registration) => registration.unregister()),
      ...cacheNames.map((cacheName) => caches.delete(cacheName)),
    ])

    localStorage.setItem(STORAGE_KEYS.legacyCacheCleared, 'true')

    // A page stays controlled until reload even after its old worker is removed.
    if (hadServiceWorkerController) window.location.reload()
  } catch {
    // Browser storage may be unavailable; static metadata still remains authoritative.
  }
}

void clearLegacyBrowserCache()

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
