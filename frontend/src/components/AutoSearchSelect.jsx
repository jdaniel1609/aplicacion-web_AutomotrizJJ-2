import { useState, useEffect, useRef } from 'react'
import { getAutosDisponibles } from '../services/api'

const AutoSearchSelect = ({ value, onChange, required = false }) => {
  const [search, setSearch] = useState('')
  const [autos, setAutos] = useState([])
  const [filteredAutos, setFilteredAutos] = useState([])
  const [showDropdown, setShowDropdown] = useState(false)
  const [loading, setLoading] = useState(false)
  const [selectedAuto, setSelectedAuto] = useState(null)
  const dropdownRef = useRef(null)

  // Cargar autos al montar el componente
  useEffect(() => {
    loadAutos()
  }, [])

  // Filtrar autos según búsqueda
  useEffect(() => {
    if (search.trim() === '') {
      setFilteredAutos(autos)
    } else {
      const searchLower = search.toLowerCase()
      const filtered = autos.filter(auto => {
        const fullName = `${auto.marca} ${auto.modelo} ${auto.anio}`.toLowerCase()
        return fullName.includes(searchLower)
      })
      setFilteredAutos(filtered)
    }
  }, [search, autos])

  // Cerrar dropdown al hacer click fuera
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setShowDropdown(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const loadAutos = async () => {
    try {
      setLoading(true)
      const response = await getAutosDisponibles()
      setAutos(response.autos || [])
      setFilteredAutos(response.autos || [])
    } catch (error) {
      console.error('Error al cargar autos:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleInputChange = (e) => {
    const value = e.target.value
    setSearch(value)
    setShowDropdown(true)
  }

  const handleSelectAuto = (auto) => {
    const autoText = `${auto.marca} ${auto.modelo} ${auto.anio}`
    setSearch(autoText)
    setSelectedAuto(auto)
    setShowDropdown(false)
    onChange(auto.id, autoText)
  }

  const handleInputFocus = () => {
    setShowDropdown(true)
  }

  return (
    <div className="relative" ref={dropdownRef}>
      <div className="relative">
        <input
          type="text"
          value={search}
          onChange={handleInputChange}
          onFocus={handleInputFocus}
          placeholder="Buscar auto por marca, modelo o año..."
          className="input-field pr-10"
          required={required}
          autoComplete="off"
        />
        <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
          <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
      </div>

      {/* Dropdown de resultados */}
      {showDropdown && (
        <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
          {loading ? (
            <div className="p-4 text-center text-gray-500">
              Cargando autos...
            </div>
          ) : filteredAutos.length > 0 ? (
            filteredAutos.map((auto) => (
              <div
                key={auto.id}
                onClick={() => handleSelectAuto(auto)}
                className="p-3 hover:bg-blue-50 cursor-pointer border-b border-gray-100 last:border-b-0
                         transition-colors duration-150"
              >
                <div className="flex justify-between items-center">
                  <div>
                    <div className="font-semibold text-gray-900">
                      {auto.marca} {auto.modelo}
                    </div>
                    <div className="text-sm text-gray-600">
                      Año: {auto.anio} 
                      {auto.precio_referencial && (
                        <span className="ml-2">
                          • S/. {auto.precio_referencial.toLocaleString('es-PE')}
                        </span>
                      )}
                    </div>
                  </div>
                  {auto.stock && (
                    <div className="text-xs text-green-600 font-medium">
                      Stock: {auto.stock}
                    </div>
                  )}
                </div>
              </div>
            ))
          ) : (
            <div className="p-4 text-center text-gray-500">
              No se encontraron autos
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default AutoSearchSelect