import axios from 'axios'

// Configuración del cliente axios para el frontend
export const api = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 30000, // 30 segundos
})

// Interceptor para manejar respuestas
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response) {
            // El servidor respondió con un código de error
            console.error('API Error:', error.response.status, error.response.data)
        } else if (error.request) {
            // La solicitud fue hecha pero no hubo respuesta
            console.error('Network Error:', error.message)
        } else {
            // Algo pasó al configurar la solicitud
            console.error('Error:', error.message)
        }
        return Promise.reject(error)
    }
)




