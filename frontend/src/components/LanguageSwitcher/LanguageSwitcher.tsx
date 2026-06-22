// Core
import { useTranslation } from 'react-i18next'
// Styles
import './LanguageSwitcher.css'
// Consts
import { SUPPORTED_LANGUAGES } from '../../i18n/i18n'

const LanguageSwitcher = () => {
  const { t, i18n } = useTranslation()
  const current = i18n.resolvedLanguage ?? i18n.language

  return (
    <div className="language-switcher" role="group" aria-label={t('language.label')}>
      {SUPPORTED_LANGUAGES.map((lng) => (
        <button
          key={lng}
          type="button"
          className={`language-switcher__btn${
            current === lng ? ' language-switcher__btn--active' : ''
          }`}
          aria-pressed={current === lng}
          onClick={() => i18n.changeLanguage(lng)}
        >
          {lng.toUpperCase()}
        </button>
      ))}
    </div>
  )
}

export default LanguageSwitcher
