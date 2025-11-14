// Clave para almacenar el token en localStorage
const TOKEN_KEY = 'auth_token'

// Obtener token del localStorage
export const getStoredToken = () => {
  try {
    return localStorage.getItem(TOKEN_KEY)
  } catch (error) {
    console.error('Error al obtener token:', error)
    return null
  }
}

// Guardar token en localStorage
export const setStoredToken = (token) => {
  try {
    localStorage.setItem(TOKEN_KEY, token)
  } catch (error) {
    console.error('Error al guardar token:', error)
  }
}

// Eliminar token del localStorage
export const removeStoredToken = () => {
  try {
    localStorage.removeItem(TOKEN_KEY)
  } catch (error) {
    console.error('Error al eliminar token:', error)
  }
}

// Verificar si el token existe y no está vacío
export const hasValidToken = () => {
  const token = getStoredToken()
  return token && token.trim() !== ''
}

// Decodificar JWT token (sin verificación, solo para obtener payload)
export const decodeToken = (token) => {
  try {
    const base64Url = token.split('.')[1]
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    )
    return JSON.parse(jsonPayload)
  } catch (error) {
    console.error('Error al decodificar token:', error)
    return null
  }
}

// Verificar si el token ha expirado
export const isTokenExpired = (token) => {
  try {
    const decoded = decodeToken(token)
    if (!decoded || !decoded.exp) return true
    
    const currentTime = Date.now() / 1000
    return decoded.exp < currentTime
  } catch (error) {
    console.error('Error al verificar expiración del token:', error)
    return true
  }
}