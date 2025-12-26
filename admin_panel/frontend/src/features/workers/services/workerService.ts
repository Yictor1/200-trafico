import { api } from '@/shared/lib/axios'
import { Worker, WorkerCode } from '@/shared/types/api'

export const workerService = {
    async getAll(): Promise<Worker[]> {
        const { data } = await api.get('/api/workers')
        return data
    },

    async getCode(nombre: string): Promise<WorkerCode> {
        const { data } = await api.get(`/api/workers/${nombre}`)
        return data
    },

    async update(nombre: string, code: string): Promise<void> {
        await api.put(`/api/workers/${nombre}`, { code })
    },

    async delete(nombre: string): Promise<void> {
        await api.delete(`/api/workers/${nombre}`)
    },
}
