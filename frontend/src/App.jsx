import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import Login from './pages/Login'
import VentaAuto from './pages/VentaAuto'
import Layout from './components/Layout'

function App() {
  const { isAuthenticated } = useAuth()

  return (
    <Router>
      <Layout>
        <Routes>
          <Route 
            path="/login" 
            element={!isAuthenticated ? <Login /> : <Navigate to="/venta-auto" replace />} 
          />
          <Route 
            path="/venta-auto" 
            element={isAuthenticated ? <VentaAuto /> : <Navigate to="/login" replace />} 
          />
          <Route 
            path="/" 
            element={<Navigate to={isAuthenticated ? "/venta-auto" : "/login"} replace />} 
          />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App