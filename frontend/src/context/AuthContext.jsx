import { createContext, useContext, useState, useEffect } from 'react'
import { loginUser } from '../services/api'
import { getStoredToken, setStoredToken, removeStoredToken } from '../utils/auth'

const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = getStoredToken()
    const storedUser = localStorage.getItem('user_data')
    
    if (token && storedUser) {
      setIsAuthenticated(true)
      setUser(JSON.parse(storedUser))
    }
    setLoading(false)
  }, [])

  const login = async (username, password) => {
    try {
      setLoading(true)
      const response = await loginUser(username, password)
      
      if (response.access_token) {
        setStoredToken(response.access_token)
        
        const userData = {
          token: response.access_token,
          username: response.user.username,
          full_name: response.user.full_name,
          email: response.user.email,
          role: response.user.role,
          codigo_vendedor: response.user.codigo_vendedor,
          sucursal_provincia: response.user.sucursal_provincia,
          sucursal_distrito: response.user.sucursal_distrito,
          sucursal: `${response.user.sucursal_provincia}/${response.user.sucursal_distrito}`
        }
        
        localStorage.setItem('user_data', JSON.stringify(userData))
        setUser(userData)
        setIsAuthenticated(true)
        return { success: true }
      }
      
      return { success: false, error: 'Credenciales inválidas' }
    } catch (error) {
      console.error('Error en login:', error)
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Error de conexión con el servidor' 
      }
    } finally {
      setLoading(false)
    }
  }

  const logout = () => {
    removeStoredToken()
    localStorage.removeItem('user_data')
    setUser(null)
    setIsAuthenticated(false)
  }

  const value = {
    user,
    isAuthenticated,
    loading,
    login,
    logout
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}