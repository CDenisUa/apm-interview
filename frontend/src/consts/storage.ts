// Consts

/** Browser localStorage keys — single source of truth, kept out of components. */
export const STORAGE_KEYS = {
  user: 'bmp:user',
  language: 'bmp:language',
  legacyCacheCleared: 'bmp:legacy-browser-cache-cleared',
} as const
