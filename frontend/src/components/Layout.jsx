import { useAuth } from '../context/AuthContext'

const Layout = ({ children }) => {
  const { isAuthenticated, logout, user } = useAuth()

  return (
    <div className="min-h-screen bg-gradient-subtle">
      {/* Header - Solo mostrar si está autenticado */}
      {isAuthenticated && (
        <header className="bg-white shadow-sm border-b border-gray-100">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center">
                <h1 className="text-xl font-bold gradient-text">
                  Automotriz JJ
                </h1>
              </div>
              <div className="flex items-center space-x-4">
                <span className="text-sm text-gray-600">
                  Bienvenido, {user?.username}
                </span>
                <button
                  onClick={logout}
                  className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg 
                           transition-colors duration-200 text-sm font-medium"
                >
                  Cerrar Sesión
                </button>
              </div>
            </div>
          </div>
        </header>
      )}

      {/* Contenido principal */}
      <main className="flex-1">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-100 py-4">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center text-sm text-gray-500">
            © 2024 Automotriz JJ. Todos los derechos reservados.
          </div>
        </div>
      </footer>
    </div>
  )
}

export default Layout