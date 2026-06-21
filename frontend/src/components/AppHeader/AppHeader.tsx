// Components
import UserMenu from '../UserMenu/UserMenu'
// Styles
import './AppHeader.css'

const AppHeader = () => {
  return (
    <header className="app-header">
      <div className="app-header__brand">
        <span className="app-header__mark">BMP</span>
        <span className="app-header__title">Business Modernization Portal</span>
      </div>
      <div className="app-header__right">
        <UserMenu />
      </div>
    </header>
  )
}

export default AppHeader
