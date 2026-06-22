// Core
import { NavLink } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
// Styles
import './Sidebar.css'
// Consts
import { ROUTES } from '../../consts/routes'

interface NavItem {
  to: string
  labelKey: string
  icon: string
}

const NAV: NavItem[] = [
  { to: ROUTES.todos, labelKey: 'nav.todos', icon: '☑' },
  { to: ROUTES.newTask, labelKey: 'nav.newTask', icon: '+' },
  { to: ROUTES.items, labelKey: 'nav.items', icon: '▦' },
]

const Sidebar = () => {
  const { t } = useTranslation()

  return (
    <aside className="sidebar">
      <nav className="sidebar__nav">
        {NAV.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end
            className={({ isActive }) =>
              `sidebar__link${isActive ? ' sidebar__link--active' : ''}`
            }
          >
            <span className="sidebar__icon" aria-hidden="true">
              {item.icon}
            </span>
            {t(item.labelKey)}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}

export default Sidebar
