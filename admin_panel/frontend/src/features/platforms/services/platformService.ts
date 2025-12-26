import { api } from '@/shared/lib/axios'
import { Platform } from '@/shared/types/api'

export const platformService = {
    async getAll(): Promise<Platform[]> {
        const { data } = await api.get('/api/platforms')
        return data
    },

    async create(platform: { nombre: string; url: string }): Promise<Platform> {
        const { data } = await api.post('/api/platforms', platform)
        return data
    },
}
