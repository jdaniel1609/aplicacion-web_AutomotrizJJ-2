import WelcomeCard from '../components/WelcomeCard'

const Dashboard = () => {
  return (
    <div className="min-h-screen py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header del Dashboard */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Panel Principal
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Gestiona todas las operaciones de Automotriz JJ desde este panel centralizado
          </p>
        </div>

        {/* Tarjeta de bienvenida principal */}
        <div className="mb-12">
          <WelcomeCard />
        </div>

        {/* Grid de funcionalidades */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          <div className="card p-6 hover:shadow-xl transition-shadow duration-300">
            <div className="w-12 h-12 bg-gradient-blue rounded-lg mb-4 flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Inventario</h3>
            <p className="text-gray-600 text-sm">Gestión de repuestos y vehículos</p>
          </div>

          <div className="card p-6 hover:shadow-xl transition-shadow duration-300">
            <div className="w-12 h-12 bg-gradient-blue rounded-lg mb-4 flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Clientes</h3>
            <p className="text-gray-600 text-sm">Base de datos de clientes</p>
          </div>

          <div className="card p-6 hover:shadow-xl transition-shadow duration-300">
            <div className="w-12 h-12 bg-gradient-blue rounded-lg mb-4 flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Servicios</h3>
            <p className="text-gray-600 text-sm">Registro de servicios técnicos</p>
          </div>

          <div className="card p-6 hover:shadow-xl transition-shadow duration-300">
            <div className="w-12 h-12 bg-gradient-blue rounded-lg mb-4 flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 8v8m-4-5v5m-4-2v2m-2 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Reportes</h3>
            <p className="text-gray-600 text-sm">Análisis y estadísticas</p>
          </div>
        </div>

        {/* Estadísticas rápidas */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="card p-6 text-center">
            <div className="text-3xl font-bold text-primary-blue mb-2">150+</div>
            <div className="text-gray-600">Vehículos en Stock</div>
          </div>

          <div className="card p-6 text-center">
            <div className="text-3xl font-bold text-primary-blue mb-2">500+</div>
            <div className="text-gray-600">Clientes Activos</div>
          </div>

          <div className="card p-6 text-center">
            <div className="text-3xl font-bold text-primary-blue mb-2">98%</div>
            <div className="text-gray-600">Satisfacción del Cliente</div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard