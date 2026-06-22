// Core
import { ApolloProvider } from '@apollo/client'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
// Components
import AppLayout from './components/AppLayout/AppLayout'
import ItemsPage from './pages/ItemsPage/ItemsPage'
import NewTaskPage from './pages/NewTaskPage/NewTaskPage'
import TodosPage from './pages/TodosPage/TodosPage'
// Hooks
import { AuthProvider } from './hooks/useAuth/AuthProvider'
// Services
import { apolloClient } from './services/apolloClient'

const App = () => {
  return (
    <ApolloProvider client={apolloClient}>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route element={<AppLayout />}>
              <Route index element={<TodosPage />} />
              <Route path="items" element={<ItemsPage />} />
              <Route path="new-task" element={<NewTaskPage />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ApolloProvider>
  )
}

export default App
