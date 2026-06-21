// Core
import { Outlet } from 'react-router-dom'
// Components
import AppHeader from '../AppHeader/AppHeader'
import Sidebar from '../Sidebar/Sidebar'
import ChepioTechFooter from '../ChepioTechFooter/ChepioTechFooter'
// Styles
import './AppLayout.css'

const AppLayout = () => {
  return (
    <div className="app-layout">
      <AppHeader />
      <div className="app-layout__body">
        <Sidebar />
        <div className="app-layout__main-col">
          <main className="app-layout__main">
            <Outlet />
          </main>
          <ChepioTechFooter />
        </div>
      </div>
    </div>
  )
}

export default AppLayout
