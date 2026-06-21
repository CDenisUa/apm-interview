// Core
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
// Components
import App from './App.tsx'
// Styles
import './index.css'

const APP_TITLE = 'Business Modernization Portal'
const LEGACY_CACHE_CLEANUP_KEY = 'bmp:legacy-browser-cache-cleared'

document.title = APP_TITLE

async function clearLegacyBrowserCache() {
  try {
    if (localStorage.getItem(LEGACY_CACHE_CLEANUP_KEY)) return

    const hadServiceWorkerController = Boolean(navigator.serviceWorker?.controller)
    const registrations = navigator.serviceWorker
      ? await navigator.serviceWorker.getRegistrations()
      : []
    const cacheNames = 'caches' in window ? await caches.keys() : []

    await Promise.all([
      ...registrations.map((registration) => registration.unregister()),
      ...cacheNames.map((cacheName) => caches.delete(cacheName)),
    ])

    localStorage.setItem(LEGACY_CACHE_CLEANUP_KEY, 'true')

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
