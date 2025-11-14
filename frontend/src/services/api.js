import axios from 'axios'
import { getStoredToken } from '../utils/auth'

const API_BASE_URL = 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
})

apiClient.interceptors.request.use(
  (config) => {
    const token = getStoredToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token')
      localStorage.removeItem('user_data')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// AUTH ENDPOINTS
export const loginUser = async (username, password) => {
  try {
    const formData = new URLSearchParams()
    formData.append('username', username)
    formData.append('password', password)

    console.log('🔐 Intentando login con:', { username, url: `${API_BASE_URL}/auth/login` })

    const response = await apiClient.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })
    
    console.log('✅ Login exitoso:', response.data)
    return response.data
  } catch (error) {
    console.error('❌ Error en login:', error)
    throw error
  }
}

export const getUserProfile = async () => {
  try {
    const response = await apiClient.get('/auth/me')
    return response.data
  } catch (error) {
    throw error
  }
}

// VENTA ENDPOINTS
export const getAutosDisponibles = async (search = '') => {
  try {
    const params = search ? { search } : {}
    const response = await apiClient.get('/venta/autos', { params })
    return response.data
  } catch (error) {
    console.error('❌ Error al obtener autos:', error)
    throw error
  }
}

export const registrarVenta = async (ventaData) => {
  try {
    console.log('📝 Registrando venta:', ventaData)
    const response = await apiClient.post('/venta/registrar', ventaData)
    console.log('✅ Venta registrada:', response.data)
    return response.data
  } catch (error) {
    console.error('❌ Error al registrar venta:', error)
    throw error
  }
}

export const getMisVentas = async (limit = 50) => {
  try {
    const response = await apiClient.get('/venta/mis-ventas', {
      params: { limit }
    })
    return response.data
  } catch (error) {
    console.error('❌ Error al obtener ventas:', error)
    throw error
  }
}

export const checkServerHealth = async () => {
  try {
    const response = await apiClient.get('/health')
    return response.data
  } catch (error) {
    throw error
  }
}

export default apiClient