import { api } from '@/shared/lib/axios'

export interface AuthSession {
    session_id: string
    status: 'authenticating' | 'completed' | 'failed'
    message: string
}

export const authService = {
    async startAuth(modelo: string, plataforma: string, url: string): Promise<AuthSession> {
        const { data } = await api.post('/api/auth/start', {
            modelo,
            plataforma,
            url
        })
        return data
    },

    async getStatus(sessionId: string): Promise<AuthSession> {
        const { data } = await api.get(`/api/auth/status/${sessionId}`)
        return data
    },
}
