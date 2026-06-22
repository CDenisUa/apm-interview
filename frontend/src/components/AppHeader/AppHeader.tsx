// Core
import { useTranslation } from 'react-i18next'
// Components
import LanguageSwitcher from '../LanguageSwitcher/LanguageSwitcher'
import UserMenu from '../UserMenu/UserMenu'
// Styles
import './AppHeader.css'

const AppHeader = () => {
  const { t } = useTranslation()

  return (
    <header className="app-header">
      <div className="app-header__brand">
        <span className="app-header__mark">BMP</span>
        <span className="app-header__title">{t('app.title')}</span>
      </div>
      <div className="app-header__right">
        <LanguageSwitcher />
        <UserMenu />
      </div>
    </header>
  )
}

export default AppHeader
