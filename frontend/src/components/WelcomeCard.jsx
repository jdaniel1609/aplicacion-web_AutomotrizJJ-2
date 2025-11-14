const WelcomeCard = () => {
  return (
    <div className="card p-8 max-w-2xl mx-auto">
      <div className="text-center">
        {/* Ícono de empresa automotriz */}
        <div className="mb-6">
          <div className="w-20 h-20 bg-gradient-blue rounded-full mx-auto flex items-center justify-center">
            <svg 
              className="w-10 h-10 text-white" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M19 14l-1.5-1.5M5 14l1.5-1.5m0 0L12 7l5.5 5.5M12 7v10"
              />
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M9 21V9a2 2 0 012-2h2a2 2 0 012 2v12"
              />
            </svg>
          </div>
        </div>

        {/* Mensaje de bienvenida */}
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Saludos desde la empresa
        </h1>
        <h2 className="text-3xl font-bold gradient-text mb-6">
          Automotriz JJ
        </h2>

        {/* Descripción */}
        <p className="text-gray-600 text-lg mb-8 leading-relaxed">
          Bienvenido a nuestro sistema de gestión empresarial. 
          Aquí podrás acceder a todas las herramientas necesarias 
          para optimizar los procesos de nuestra empresa automotriz.
        </p>

        {/* Características destacadas */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="text-center p-4">
            <div className="w-12 h-12 bg-blue-100 rounded-lg mx-auto mb-3 flex items-center justify-center">
              <svg className="w-6 h-6 text-primary-blue" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="font-semibold text-gray-900">Gestión Eficiente</h3>
            <p className="text-sm text-gray-600">Optimiza todos tus procesos</p>
          </div>

          <div className="text-center p-4">
            <div className="w-12 h-12 bg-blue-100 rounded-lg mx-auto mb-3 flex items-center justify-center">
              <svg className="w-6 h-6 text-primary-blue" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h3 className="font-semibold text-gray-900">Tecnología Avanzada</h3>
            <p className="text-sm text-gray-600">Herramientas de última generación</p>
          </div>

          <div className="text-center p-4">
            <div className="w-12 h-12 bg-blue-100 rounded-lg mx-auto mb-3 flex items-center justify-center">
              <svg className="w-6 h-6 text-primary-blue" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            </div>
            <h3 className="font-semibold text-gray-900">Equipo Profesional</h3>
            <p className="text-sm text-gray-600">Soporte especializado</p>
          </div>
        </div>

        {/* Botón de acción */}
        <div className="flex justify-center">
          <button className="btn-primary px-8">
            Explorar Sistema
          </button>
        </div>
      </div>
    </div>
  )
}

export default WelcomeCard