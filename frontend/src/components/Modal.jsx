const Modal = ({ isOpen, onClose, title, message, type = 'success' }) => {
  if (!isOpen) return null

  const getIcon = () => {
    if (type === 'success') {
      return (
        <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-green-100 mb-4">
          <svg className="h-10 w-10 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>
      )
    }
    
    if (type === 'error') {
      return (
        <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-red-100 mb-4">
          <svg className="h-10 w-10 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
      )
    }
  }

  const getTitleColor = () => {
    return type === 'success' ? 'text-green-600' : 'text-red-600'
  }

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      {/* Overlay */}
      <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div 
          className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" 
          aria-hidden="true"
          onClick={onClose}
        ></div>

        {/* Center modal */}
        <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>

        {/* Modal panel */}
        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div className="sm:flex sm:items-start">
              <div className="mt-3 text-center sm:mt-0 w-full">
                {/* Icono */}
                {getIcon()}

                {/* Título */}
                <h3 className={`text-2xl leading-6 font-bold ${getTitleColor()} mb-4`} id="modal-title">
                  {title}
                </h3>

                {/* Mensaje */}
                <div className="mt-2">
                  <p className="text-lg text-gray-700">
                    {message}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Botón de cerrar */}
          <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button
              type="button"
              onClick={onClose}
              className={`w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-6 py-3 
                       ${type === 'success' ? 'bg-green-600 hover:bg-green-700' : 'bg-red-600 hover:bg-red-700'} 
                       text-base font-medium text-white focus:outline-none focus:ring-2 focus:ring-offset-2 
                       ${type === 'success' ? 'focus:ring-green-500' : 'focus:ring-red-500'} 
                       sm:ml-3 sm:w-auto sm:text-sm transition-colors duration-200`}
            >
              Aceptar
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Modal