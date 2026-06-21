// Core
import { NavLink } from 'react-router-dom'
// Styles
import './Sidebar.css'
// Consts
import { ROUTES } from '../../consts/routes'

interface NavItem {
  to: string
  label: string
  icon: string
}

const NAV: NavItem[] = [
  { to: ROUTES.todos, label: 'Todos', icon: '☑' },
  { to: ROUTES.newTask, label: 'New task', icon: '+' },
  { to: ROUTES.items, label: 'Business Items', icon: '▦' },
]

const Sidebar = () => {
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
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}

export default Sidebar
